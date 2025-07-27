import boto3
import csv

# AWS profile and region
aws_profile = "primary"
aws_region = "ap-south-1"  # Mumbai region

# List of EC2 Instance IDs
instance_ids = [
    "i-0abcd1234efgh5678",  # Replace with actual instance IDs
]

# Initialize AWS session
session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
ec2_client = session.client("ec2")

# Fetch instance details
response = ec2_client.describe_instances(InstanceIds=instance_ids)

# Extract relevant details
instance_data = []
for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        instance_id = instance["InstanceId"]
        public_ip = instance.get(
            "PublicIpAddress", "N/A"
        )  # Handle cases where public IP is absent
        name_tag = "N/A"

        # Extract "Name" tag if available
        if "Tags" in instance:
            for tag in instance["Tags"]:
                if tag["Key"] == "Name":
                    name_tag = tag["Value"]
                    break

        instance_data.append([instance_id, name_tag, public_ip])

# Save to CSV
csv_filename = "ec2_instances.csv"
with open(csv_filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Instance ID", "Label", "Public IP"])
    writer.writerows(instance_data)

print(f"CSV file '{csv_filename}' has been generated successfully.")
