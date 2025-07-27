import boto3
import json
from botocore.exceptions import ClientError
from openpyxl import Workbook
from datetime import datetime
import os


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


def get_aws_account_id(session):
    try:
        sts_client = session.client("sts")
        identity = sts_client.get_caller_identity()
        account_id = identity["Account"]
        print(f"AWS Account ID: {account_id}")
        return account_id
    except Exception as e:
        print(f"Error fetching AWS Account ID: {e}")


def check_bucket_acl(s3_client, bucket_name):
    try:
        acl = s3_client.get_bucket_acl(Bucket=bucket_name)
        for grant in acl["Grants"]:
            grantee = grant.get("Grantee", {})
            if grantee.get("URI") == "http://acs.amazonaws.com/groups/global/AllUsers":
                return True
    except ClientError:
        pass
    return False


def check_bucket_policy_public(s3_client, bucket_name):
    try:
        policy = s3_client.get_bucket_policy(Bucket=bucket_name)
        policy_dict = json.loads(policy["Policy"])
        for statement in policy_dict.get("Statement", []):
            if statement.get("Effect") == "Allow":
                principal = statement.get("Principal")
                if principal == "*" or principal == {"AWS": "*"}:
                    actions = statement.get("Action", [])
                    if isinstance(actions, str):
                        actions = [actions]
                    if any(action in ["s3:GetObject", "s3:*"] for action in actions):
                        return True
    except ClientError:
        pass
    return False


def get_block_public_access_setting(s3_client, bucket_name):
    try:
        response = s3_client.get_public_access_block(Bucket=bucket_name)
        config = response["PublicAccessBlockConfiguration"]
        # If all 4 settings are True, bucket is fully private
        if all(
            [
                config.get("BlockPublicAcls", False),
                config.get("IgnorePublicAcls", False),
                config.get("BlockPublicPolicy", False),
                config.get("RestrictPublicBuckets", False),
            ]
        ):
            return "Private"
        else:
            return "Public"
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchPublicAccessBlockConfiguration":
            # print(f"No Public Access Block configuration for bucket: {bucket_name}")
            return "No Config (Possibly Public)"
        else:
            print(f"Unexpected error for bucket {bucket_name}: {e}")
            return "Unknown"


def main():

    aws_profile = chooseProfile(fetchProfiles())
    session = boto3.Session(profile_name=aws_profile)
    aws_account_id = str(get_aws_account_id(session))  # Use appropriate profile
    s3 = session.client("s3")
    date = datetime.now().strftime("%Y-%m-%d")

    try:
        response = s3.list_buckets()
        buckets = response["Buckets"]
    except ClientError as e:
        print(f"Error fetching buckets: {e}")
        return

    # Create Excel workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "S3 Public Access Report"

    # Headers
    ws.append(
        [
            "Name of Bucket",
            "Block Public Access Setting",
            "ACL Status",
            "Bucket Policy",
        ]
    )

    for bucket in buckets:
        name = bucket["Name"]
        block_public_setting = get_block_public_access_setting(s3, name)
        acl_status = check_bucket_acl(s3, name)
        policy_public = check_bucket_policy_public(s3, name)
        # last_modified_time = get_latest_object_modified_time(s3, name)

        if block_public_setting != "Private":
            row = [
                name,
                block_public_setting,
                "Yes" if acl_status else "No",
                "Yes" if policy_public else "No",
                # last_modified_time,
            ]
            ws.append(row)

        # Save Excel report
        # output_file = f"s3_public_access_report_{date}.xlsx"
        output_dir = os.path.dirname(os.path.abspath(__file__))
    # Save Excel file
    output_file = os.path.join(
        output_dir, f"S3_audit_report-{aws_account_id}-{date}.xlsx"
    )
    wb.save(output_file)
    print(f"Report saved to: {output_file}")


if __name__ == "__main__":
    main()
