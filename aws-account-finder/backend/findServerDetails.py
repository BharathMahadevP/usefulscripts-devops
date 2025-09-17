import boto3
from botocore.exceptions import ClientError, ProfileNotFound
import os
from dotenv import load_dotenv
import ipaddress

load_dotenv()


def get_aws_account_id(session):
    try:
        sts_client = session.client("sts")
        identity = sts_client.get_caller_identity()
        account_id = identity["Account"]
        print(f" Searching AWS Account ID: {account_id}...")
        return account_id
    except Exception as e:
        print(f"Error fetching AWS Account ID: {e}")


def create_session(aws_access_key_id, aws_secret_access_key, aws_session_token=None):
    return boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,  # Optional (for temporary creds)
    )


def get_all_regions(session):
    regions = session.client("ec2", region_name="us-east-1")
    response = regions.describe_regions(AllRegions=True)

    enabled_regions = [
        region["RegionName"]
        for region in response["Regions"]
        if region["OptInStatus"] in ["opt-in-not-required", "opted-in"]
    ]
    return enabled_regions



def finddetails(ip, inputType):

    # Load credentials
    creds_primary = {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID_PRIMARY"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY_PRIMARY"),
    }

    creds_secondary = {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID_SECONDARY"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY_SECONDARY"),
    }

    sessions = [create_session(**creds_secondary), create_session(**creds_primary)]

    for i, session in enumerate(sessions):
        regions = get_all_regions(session)
        AccountId = get_aws_account_id(session)
        for region in regions:
            ec2 = session.client("ec2", region_name=region)

            try:
                if inputType == "ec2":
                    response = ec2.describe_instances(InstanceIds=[ip])
                else:
                    res = ipaddress.ip_address(ip)
                    if res.is_private:
                        response = ec2.describe_instances(
                            Filters=[{"Name": "private-ip-address", "Values": [ip]}]
                        )
                    else:
                        response = ec2.describe_instances(
                            Filters=[{"Name": "ip-address", "Values": [ip]}]
                        )
                for reservation in response["Reservations"]:
                    for instance in reservation["Instances"]:
                        label = "No Name Tag"
                        for tag in instance["Tags"]:
                            instance_id = instance["InstanceId"]
                            awsAccountId = reservation["OwnerId"]
                            public_ip = instance.get("PublicIpAddress", "N/A")
                            private_ip = instance.get("PrivateIpAddress", "N/A")
                            if (tag["Key"] == "Name") is True:
                                label = tag["Value"]

                        if instance_id:
                            return (
                                instance_id,
                                region,
                                awsAccountId,
                                label,
                                public_ip,
                                private_ip,
                            )
            except ClientError as e:
                print(f"Error querying region {region}: {e}")
        print(
            f"\n❌ Instance with public IP not found in any region of the AWS Accout: {AccountId}"
        )