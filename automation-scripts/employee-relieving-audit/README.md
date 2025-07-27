# The Employee Relieving Audit

This Python script automates various steps involved in the employee relieving audit process.

### Steps performed via the script:

##### 1. Gitlab Audit

- Verifies the status of the user account (checks if the account is blocked or active).
- Prompts the admin to block active accounts.
- Removes all SSH keys for users in blocked status.
- Resets the password of the GitLab user account.

##### 2. Azure Access Validation

Checks if the user has access to the Azure Portal.

##### 3. AWS Access Validation

Checks if the user has access to any of the configured AWS Accounts .

## Prerequisites

- Python installed and properly set up on the machine.
- Personal Access Token (PAT) from GitLab with admin access to all relevant APIs.
- AWS Credentials (Access Key and Secret Key), with read access to IAM users.
- Azure Client ID and Client Secret with read access to Azure Entra ID users.


## Steps to execute script

> Ensure all prerequisites mentioned above are fulfilled before proceeding.

1. Clone this repository

```bash
git clone https://github.com/BharathMahadevP/usefulscripts-devops.git
```

2. Navigate to the project directory

```bash
cd employee-relieving-audit/
```

3. Install the required python modules

```bash
pip install requests python-dotenv msal boto3 openpyxl
```

4. Create a new `.env` file

```bash
cp .envsample .env
```

5. Add the necessary values for PAT and Azure Authetication

| Value                             | Description                                                |
| --------------------------------- | ---------------------------------------------------------- |
| `API_TOKEN`                       | Personal Access Token from GitLab                          |
| `AZURE_CLIENT_ID`                 | Application (client) ID of the Azure App Registration      |
| `AZURE_CLIENT_SECRET`             | Value of the client secret from the Azure App Registration |
| `AZURE_TENENT_ID`                 | Directory (tenant) ID of the Azure App Registration        |
| `AWS_ACCESS_KEY_ID_PRIMARY`       | Access Key of Primary AWS                                  |
| `AWS_SECRET_ACCESS_KEY_PRIMARY`   | Secret Key of Primary AWS                                  |
| `AWS_ACCESS_KEY_ID_SECONDARY`     | Access Key of Secondary AWS                                |
| `AWS_SECRET_ACCESS_KEY_SECONDARY` | Secret Key of Secondary AWS                                |

```bash
vim .env
```

6. Add the email IDs of all relieved users who need to be audited.

7. Run the script

```bash
python3 main.py
```

> Type pyth and press Tab button. This will autofill with the current python installed on your system.
