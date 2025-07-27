import requests
import os
from dotenv import load_dotenv
from msal import ConfidentialClientApplication

load_dotenv()

# Azure AD app registration details
client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
tenant_id = os.getenv("AZURE_TENENT_ID")

# Microsoft Graph endpoint and scope
authority = f"https://login.microsoftonline.com/{tenant_id}"
scope = ["https://graph.microsoft.com/.default"]
graph_endpoint = "https://graph.microsoft.com/v1.0"
# user_principal_name = user_name


def azureUser(user_principal_name):

    # Create MSAL confidential client
    app = ConfidentialClientApplication(
        client_id, authority=authority, client_credential=client_secret
    )

    # Acquire token
    token_response = app.acquire_token_for_client(scopes=scope)

    if "access_token" in token_response:
        access_token = token_response["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Make Graph API call
        url = f"{graph_endpoint}/users/{user_principal_name}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            user = response.json()
            print(
                f"✅ {user['displayName']} : {user['userPrincipalName']} exists in Azure"
            )
            return "Yes"
        elif response.status_code == 404:
            print("❌ User does not exist in azure.")
            return "No"
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(response.json())
    else:
        print("❌ Failed to acquire access token.")
        print(token_response.get("error_description"))
