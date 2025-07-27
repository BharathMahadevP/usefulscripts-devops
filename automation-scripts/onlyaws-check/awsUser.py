import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()


def get_aws_account_id(session):
    try:
        sts_client = session.client("sts")
        identity = sts_client.get_caller_identity()
        account_id = identity["Account"]
        return account_id
    except Exception as e:
        print(f"Error fetching AWS Account ID: {e}")


def check_iam_user_exists(username, session):

    # session = boto3.Session(profile_name=profile)
    iam = session.client("iam")
    try:
        response = iam.get_user(UserName=username)
        if response["User"]["UserName"] == username:
            account_id = get_aws_account_id(session)
            print(f"User {username} exists in {account_id}")
            return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchEntity":
            print(f"User {username} does not exist.")
            return False
        else:
            raise e


def create_session(aws_access_key_id, aws_secret_access_key, aws_session_token=None):
    return boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,  # Optional (for temporary creds)
    )


def awsUser(username):

    # Load credentials
    creds_primary = {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID_PRIMARY"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY_PRIMARY"),
    }

    creds_secondary = {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID_SECONDARY"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY_SECONDARY"),
    }

    sessions = [create_session(**creds_primary), create_session(**creds_secondary)]
    
    awsUserStatus = []
    for i, session in enumerate(sessions):

        # profiles = fetchProfiles()
        # for profile in profiles:
        userStatus = check_iam_user_exists(username, session)
        if userStatus is True:
            awsUserStatus.append("Yes")
        else:
            awsUserStatus.append("No")
    return awsUserStatus
