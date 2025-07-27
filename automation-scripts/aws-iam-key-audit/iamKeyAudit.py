import boto3
from datetime import datetime, timezone
from openpyxl import Workbook
import os

# Threshold in days
AGE_THRESHOLD_DAYS = 90


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


# Use the AWS profile 'primary'
aws_profile = chooseProfile(fetchProfiles())
print(f"Using AWS profile: {aws_profile}")
session = boto3.Session(profile_name=aws_profile)
iam_client = session.client("iam")


def get_all_users():
    paginator = iam_client.get_paginator("list_users")
    users = []
    for response in paginator.paginate():
        users.extend(response["Users"])
    return users


def get_aws_account_id(aws_profile):
    try:
        session = boto3.Session(profile_name=aws_profile)
        sts_client = session.client("sts")
        identity = sts_client.get_caller_identity()
        account_id = identity["Account"]
        print(f"AWS Account ID: {account_id}")
        print(f"Using AWS profile: {aws_profile}")
        return account_id
    except Exception as e:
        print(f"Error fetching AWS Account ID: {e}")


def get_old_keys(user_name):
    old_keys_info = []
    response = iam_client.list_access_keys(UserName=user_name)
    for key_metadata in response["AccessKeyMetadata"]:
        create_date = key_metadata["CreateDate"]
        age_days = (datetime.now(timezone.utc) - create_date).days
        status = key_metadata["Status"]

        if age_days >= AGE_THRESHOLD_DAYS:
            last_used_days = "Never Used"
            try:
                usage_response = iam_client.get_access_key_last_used(
                    AccessKeyId=key_metadata["AccessKeyId"]
                )
                last_used_date = usage_response.get("AccessKeyLastUsed", {}).get(
                    "LastUsedDate"
                )
                if last_used_date:
                    last_used_days = (datetime.now(timezone.utc) - last_used_date).days
                    if last_used_days == 0:
                        last_used_days = "Recently Used"
            except Exception as e:
                last_used_days = "Error"

            old_keys_info.append(
                {
                    "AccessKeyId": key_metadata["AccessKeyId"],
                    "CreateDate": create_date.strftime("%Y-%m-%d"),
                    "AgeDays": age_days,
                    "LastUsedDaysAgo": last_used_days,
                    "KeyStatus": status,
                }
            )
    return old_keys_info


def create_excel_report(data):
    wb = Workbook()
    ws = wb.active
    ws.title = "Old IAM Keys"

    # Header
    ws.append(
        [
            "Username",
            "Key ID",
            "Key Age (days)",
            "Created On",
            "Last Used (days ago)",
            "Key Status",
        ]
    )

    # Rows
    for item in data:
        for key in item["OldKeys"]:
            ws.append(
                [
                    item["UserName"],
                    key["AccessKeyId"],
                    key["AgeDays"],
                    key["CreateDate"],
                    key["LastUsedDaysAgo"],
                    key["KeyStatus"],
                ]
            )

    # Save to file
    aws_account_id = get_aws_account_id(aws_profile)
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, f"old_iam_keys-{aws_account_id}.xlsx")
    wb.save(output_file)
    print(f"Excel file 'old_iam_keys-{aws_account_id}.xlsx' created successfully.")


def main():
    all_users = get_all_users()
    report_data = []

    for user in all_users:
        username = user["UserName"]
        old_keys = get_old_keys(username)
        if old_keys:
            report_data.append({"UserName": username, "OldKeys": old_keys})

    if report_data:
        create_excel_report(report_data)
    else:
        print("No keys older than or equal to 90 days found.")


if __name__ == "__main__":
    main()
