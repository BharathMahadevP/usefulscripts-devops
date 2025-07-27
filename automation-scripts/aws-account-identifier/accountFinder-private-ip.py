import boto3
from botocore.exceptions import ClientError, ProfileNotFound

import json


def fetchIPfromUser():
    TARGET_PRIVATE_IP = input("Enter the  private IP: ")
    return TARGET_PRIVATE_IP


def get_all_regions():
    ec2 = boto3.client("ec2", region_name="us-east-1")
    response = ec2.describe_regions(AllRegions=True)

    enabled_regions = [
        region["RegionName"]
        for region in response["Regions"]
        if region["OptInStatus"] in ["opt-in-not-required", "opted-in"]
    ]
    return enabled_regions


def fetchProfiles():
    session = boto3.Session()
    profiles = session.available_profiles
    return profiles


def find_instance_by_private_ip(private_ip, AWS_PROFILE):
    try:
        session = boto3.Session(profile_name=AWS_PROFILE)
    except ProfileNotFound:
        print(f"❌ Profile '{AWS_PROFILE}' not found.")
        return None, None

    regions = get_all_regions()

    for region in regions:
        ec2 = session.client("ec2", region_name=region)
        try:
            response = ec2.describe_instances(
                Filters=[{"Name": "private-ip-address", "Values": [private_ip]}]
            )
            json_string = json.dumps(response, default=str, indent=2)
            # print(json_string)

            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    for tag in instance.get("Tags", []):
                        instance_id = instance["InstanceId"]
                        awsAccountId = reservation["OwnerId"]
                        if tag["Key"] == "Name":
                            label = tag["Value"]

                    if instance_id:
                        return instance_id, region, awsAccountId, label
        except ClientError as e:
            print(f"Error querying region {region}: {e}")
    print(
        f"\n❌ Instance with private IP not found in any region of the profile: {AWS_PROFILE}"
    )


def main():

    TARGET_PRIVATE_IP = fetchIPfromUser()

    if not TARGET_PRIVATE_IP:
        print("❌ No IP provided. Exiting.")
        return None

    AWS_PROFILES = fetchProfiles()
    for profile in AWS_PROFILES:
        result = find_instance_by_private_ip(TARGET_PRIVATE_IP, profile)

        if result:
            instance_id, region, awsAccountId, label = result
            print("<==================================>")
            print(f"\nEC2 Instance ID: {instance_id}")
            print(f"Region: {region}")
            print(f"AWS Account ID: {awsAccountId}")
            print(f"Label Name: {label}")
            return


if __name__ == "__main__":
    main()
