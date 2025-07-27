import boto3
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


# Use the AWS profile 'primary'
aws_profile = chooseProfile(fetchProfiles())
print(f"Using AWS profile: {aws_profile}")
session = boto3.Session(profile_name=aws_profile)
date = datetime.now().strftime("%Y-%m-%d")


def get_all_regions():
    ec2_client = session.client("ec2", region_name="us-east-1")
    response = ec2_client.describe_regions(AllRegions=True)
    enabled_regions = [
        region["RegionName"]
        for region in response["Regions"]
        if region["OptInStatus"] in ["opt-in-not-required", "opted-in"]
    ]
    return enabled_regions


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


# Initialize Excel workbook
wb = Workbook()
ws = wb.active
ws.title = "SG Audit Report"
ws.append(["Region", "Security Group ID", "Group Name", "In Use", "Attached Resources"])


def check_sg_usage(region, sg_id):
    in_use_resources = []

    ec2 = session.client("ec2", region_name=region)
    elb = session.client("elb", region_name=region)
    elbv2 = session.client("elbv2", region_name=region)
    rds = session.client("rds", region_name=region)
    lambda_client = session.client("lambda", region_name=region)

    # ENIs
    enis = ec2.describe_network_interfaces(
        Filters=[{"Name": "group-id", "Values": [sg_id]}]
    )
    for eni in enis["NetworkInterfaces"]:
        in_use_resources.append(f"ENI:{eni['NetworkInterfaceId']}")

    # EC2
    instances = ec2.describe_instances(
        Filters=[{"Name": "instance.group-id", "Values": [sg_id]}]
    )
    for reservation in instances["Reservations"]:
        for instance in reservation["Instances"]:
            in_use_resources.append(f"EC2:{instance['InstanceId']}")

    # Classic Load Balancers (ELB)
    try:
        clbs = elb.describe_load_balancers()["LoadBalancerDescriptions"]
        for clb in clbs:
            if sg_id in clb.get("SecurityGroups", []):
                in_use_resources.append(f"CLB:{clb['LoadBalancerName']}")
    except ClientError as e:
        print(f"[{region}] Error checking classic ELB: {e}")

    # Application/NLB (ELBv2)
    try:
        albs = elbv2.describe_load_balancers()["LoadBalancers"]
        for alb in albs:
            lb_arn = alb["LoadBalancerArn"]
            attrs = elbv2.describe_load_balancer_attributes(LoadBalancerArn=lb_arn)
            lb_desc = elbv2.describe_load_balancers(LoadBalancerArns=[lb_arn])
            lb_sgs = lb_desc["LoadBalancers"][0].get("SecurityGroups", [])
            if sg_id in lb_sgs:
                in_use_resources.append(f"ALB/NLB:{alb['LoadBalancerName']}")
    except ClientError as e:
        print(f"[{region}] Error checking ALB/NLB: {e}")

    # RDS
    try:
        dbs = rds.describe_db_instances()["DBInstances"]
        for db in dbs:
            vpc_sgs = db.get("VpcSecurityGroups", [])
            for sg in vpc_sgs:
                if sg_id == sg["VpcSecurityGroupId"]:
                    in_use_resources.append(f"RDS:{db['DBInstanceIdentifier']}")
    except ClientError as e:
        print(f"[{region}] Error checking RDS: {e}")

    # Lambda
    try:
        functions = lambda_client.list_functions()["Functions"]
        for function in functions:
            conf = lambda_client.get_function_configuration(
                FunctionName=function["FunctionName"]
            )
            if "VpcConfig" in conf:
                for vpc_sg in conf["VpcConfig"].get("SecurityGroupIds", []):
                    if sg_id == vpc_sg:
                        in_use_resources.append(f"Lambda:{function['FunctionName']}")
    except ClientError as e:
        print(f"[{region}] Error checking Lambda: {e}")

    return in_use_resources


def main():
    aws_account_id = str(get_aws_account_id(aws_profile))
    regions = get_all_regions()

    for region in regions:
        print(f"Auditing region: {region}")
        try:
            ec2 = session.client("ec2", region_name=region)
            sg_response = ec2.describe_security_groups()

            for sg in sg_response["SecurityGroups"]:
                sg_id = sg["GroupId"]
                sg_name = sg.get("GroupName", "N/A")
                used_by = check_sg_usage(region, sg_id)
                in_use = "Yes" if used_by else "No"
                used_by_str = ", ".join(used_by) if used_by else "None"

                ws.append([region, sg_id, sg_name, in_use, used_by_str])

        except ClientError as e:
            print(f"Error in region {region}: {e}")

    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(
        output_dir, f"sg_audit_report-{aws_account_id}-{date}.xlsx"
    )
    wb.save(output_file)
    print(f"Security Group audit report saved to {output_file}")


if __name__ == "__main__":
    main()
