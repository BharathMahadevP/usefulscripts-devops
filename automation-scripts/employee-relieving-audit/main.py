from awsUser import awsUser
from azureUser import azureUser
from gitlabAudit import (
    fetch_username,
    fetch_user_details,
    get_user_status,
    fetch_user_ssh_keys,
    delete_ssh_key,
    generate_password,
    reset_password,
    block_user,
)
from openpyxl import Workbook
import os


# Initialize Excel workbook
wb = Workbook()
ws = wb.active
ws.title = "Employee Relieving Audit Report"
ws.append(
    [
        "Mail ID",
        "User Status",
        "SSH Keys Removal",
        "Gitlab Password Reset",
        "Azure User Check",
        "Primary AWS User Check",
        "Secondary AWS User Check",
    ]
)

# Initialize variables
UserStatus = "-"
keyRemovalStatus = "-"
passwordResetStatus = "-"
azureUserStatus = "-"
awsUserStatusPrimary = "-"
awsUserStatusSecondary = "-"

mailIds = fetch_username()

for mailId in mailIds:
    responses = fetch_user_details(mailId)
    if responses:
        UserStatus, user_id = get_user_status(responses)

        if UserStatus == "active" or UserStatus == "deactivated":
            user_response = input(
                f"User {mailId} is {UserStatus}. Do you want to block the user? (yes/no): "
            )
            if user_response.lower() == "yes":
                block_user(mailId)
                UserStatus = "blocked"
            else:
                print(f"\n -> Skipping user {mailId} as they are not blocked.")

        if UserStatus == "blocked":
            ssh_ids = fetch_user_ssh_keys(user_id)
            print(f"User: {mailId}")
            print(f"User Status: {UserStatus}")
            if UserStatus == "blocked":
                if ssh_ids:
                    print(f"SSH Key IDs: {ssh_ids}")
                    for ssh_id in ssh_ids:
                        delete_ssh_key(ssh_id, user_id)
                        keyRemovalStatus = "SSH keys removed successfully"
                else:
                    print(f"No SSH keys found for user: {mailId}")
                    keyRemovalStatus = "No SSH keys found"
            # print("Resetting password for :", mailId)
            passwordResetStatus = reset_password(user_id, generate_password(20))

    else:
        print(f"\n -> User {mailId} does not exist in GitLab.")
        UserStatus = "User does not exist in GitLab"
        # checking if user exists in AWS (Primary/Secondary)
    print("\nAWS User Check for:", mailId)
    awsUserStatus = awsUser(mailId)
    awsUserStatusPrimary, awsUserStatusSecondary = (
        awsUserStatus[0],
        awsUserStatus[1],
    )
    # checking if user exists in Azure
    azureUserStatus = azureUser(mailId)

    # Append results to the Excel sheet
    ws.append(
        [
            mailId,
            UserStatus,
            keyRemovalStatus,
            passwordResetStatus,
            azureUserStatus,
            awsUserStatusPrimary,
            awsUserStatusSecondary,
        ]
    )
    print(f"\n---------------------------------\n")
output_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(output_dir, "employee_relieving_audit_report.xlsx")
wb.save(output_file)

print(
    "==================================================================================================="
)
print(f"Audit report saved to {output_file}")
print(
    "==================================================================================================="
)
