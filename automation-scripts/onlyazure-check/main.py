from azureUser import azureUser
from openpyxl import Workbook
import os

# Initialize Excel workbook
wb = Workbook()
ws = wb.active
ws.title = "Employee Relieving Audit Report"

ws.append(["Mail ID", "Azure User Check"])

azureUserStatus = "-"


def fetch_username():
    script_root = os.path.dirname(os.path.abspath(__file__))
    userFile = os.path.join(script_root, "users.txt")
    with open(userFile, "r") as f:
        names = [line.strip() for line in f if line.strip()]
    return names


mailIds = fetch_username()


for mailId in mailIds:
    azureUserStatus = azureUser(mailId)
    ws.append([mailId, azureUserStatus])

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

