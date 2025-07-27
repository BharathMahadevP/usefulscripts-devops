import boto3
from botocore.exceptions import ClientError
from openpyxl import Workbook
from datetime import datetime
import os
# from sendEmail import sendMail


def fetchProfiles():
    session = boto3.Session()
    profiles = session.available_profiles
    return profiles

def chooseProfile(profiles=fetchProfiles()):
    print("Available AWS profiles:")
    for i, profile in enumerate(profiles):
        print(f"{i + 1}. {profile}")

    while True:
        try:
            choice = int(input("Select a profile by entering the number: "))
            if 1 <= choice <= len(profiles):
                return profiles[choice - 1]
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a valid number.")

aws_profile= chooseProfile(fetchProfiles())
print(f"Using AWS profile: {aws_profile}")
session = boto3.Session(profile_name=aws_profile)
date = datetime.now().strftime("%Y-%m-%d")


def get_all_regions():
    aws_region = boto3.client("ec2", region_name="us-east-1")
    response = aws_region.describe_regions(AllRegions=True)

    enabled_regions = [
        region["RegionName"]
        for region in response["Regions"]
        if region["OptInStatus"] in ["opt-in-not-required", "opted-in"]
    ]
    return enabled_regions


def get_aws_account_id():
    try:
        sts_client = boto3.client("sts")
        identity = sts_client.get_caller_identity()
        account_id = identity["Account"]
        print(f"AWS Account ID: {account_id}")
        return account_id
    except Exception as e:
        print(f"Error fetching AWS Account ID: {e}")


# Initialize Excel workbook
wb = Workbook()
ws = wb.active
ws.title = "EBS Audit Report"
ws.append(["Region", "Volume ID", "Encrypted", "Attached EC2 Instance"])


def main():
    # inititalise count vairables
    encryptedCOunt = 0
    unEncryptedCount = 0
    unattachedCount = 0
    attachedCount = 0
    totalCount = 0

    # fetching AWS account ID
    aws_account_id = str(get_aws_account_id())
    # fetching all regions
    regions = get_all_regions()

    for region in regions:
        print(f"Checking region: {region}")
        ec2_regional = session.client("ec2", region_name=region)
        try:
            volumes = ec2_regional.describe_volumes()["Volumes"]
            for volume in volumes:
                volume_id = volume["VolumeId"]

                if volume["VolumeId"]:
                    totalCount += 1

                encrypted = volume["Encrypted"]
                if encrypted:
                    encryptedCOunt += 1
                else:
                    unEncryptedCount += 1

                attachments = volume.get("Attachments", [])
                instance_id = (
                    attachments[0]["InstanceId"] if attachments else "Not Attached"
                )
                if instance_id == "Not Attached":
                    unattachedCount += 1
                else:
                    attachedCount += 1
                ws.append([region, volume_id, encrypted, instance_id])

        except ClientError as e:
            print(f"Error retrieving volumes in region {region}: {e}")

    # print("Total EBS Volumes:", totalCount)
    # print("Encrypted EBS Volumes:", encryptedCOunt)
    # print("Unencrypted EBS Volumes:", unEncryptedCount)
    # print("Attached EBS Volumes:", attachedCount)
    # print("Unattached EBS Volumes:", unattachedCount)

    output_dir = os.path.dirname(os.path.abspath(__file__))
    # Save Excel file
    output_file = os.path.join(
        output_dir, f"ebs_encryption_report-{aws_account_id}-{date}.xlsx"
    )

    wb.save(output_file)
    print(f"Report saved to {output_file}")
    # print("Sending mail with attachment... \n")
    # sendMail(
    #     output_file,
    #     encryptedCOunt,
    #     unEncryptedCount,
    #     unattachedCount,
    #     attachedCount,
    #     totalCount,
    #     date,
    #     aws_account_id,
    # )


if __name__ == "__main__":
    main()
