import requests
import os
from dotenv import load_dotenv
import secrets
import string

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
GITLAB_API_URL = os.getenv("GITLAB_API_URL")


def fetch_user_details(mailId):
    url = f"{GITLAB_API_URL}/users"
    headers = {"PRIVATE-TOKEN": API_TOKEN}
    params = {"search": mailId}
    # Make a GET request to the API endpoint
    responses = requests.get(url, headers=headers, params=params)
    # print(responses.json())
    return responses.json()


def get_user_status(responses):
    for response in responses:
        UserStatus = response.get("state")
        user_id = response.get("id")
    return UserStatus, user_id


def fetch_user_ssh_keys(user_id):
    url = f"{GITLAB_API_URL}/users/{user_id}/keys"
    headers = {"PRIVATE-TOKEN": API_TOKEN}
    response = requests.get(url, headers=headers)
    # response.raise_for_status()
    ssh_ids = []
    if response.json():
        ssh_ids = []
        for ssh_key in response.json():
            ssh_id = ssh_key.get("id")
            ssh_ids.append(ssh_id)
    return ssh_ids


def delete_ssh_key(ssh_id, user_id):
    url = f"{GITLAB_API_URL}/users/{user_id}/keys/{ssh_id}"
    headers = {"PRIVATE-TOKEN": API_TOKEN}
    response = requests.delete(url, headers=headers)
    # response.raise_for_status()
    if response.status_code == 204:
        print(f"SSH key {ssh_id} deleted successfully.")
        return True
    else:
        print(f"Failed to delete SSH key {ssh_id}. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False


def generate_password(length=16):
    if length < 8:
        raise ValueError(
            "Password length should be at least 8 characters for security."
        )

    # Define the character set
    characters = string.ascii_letters + string.digits + string.punctuation

    # Generate a secure password
    password = "".join(secrets.choice(characters) for _ in range(length))
    return password


def reset_password(user_id, new_password):
    url = f"{GITLAB_API_URL}/users/{user_id}"
    headers = {"PRIVATE-TOKEN": API_TOKEN}
    payload = {"password": new_password}
    response = requests.put(url, headers=headers, data=payload)
    # response.raise_for_status()
    if response.status_code == 200:
        print(f"✅ Gitlab password for user has been reset successfully.")
        return "Done"
    else:
        print(
            f"❌ Failed to reset gitlab password. Status Code: {response.status_code}"
        )
        return "Failed to reset the password"


def block_user(USER_ID):

    prompt = input("Would you like to block the user? (yes/no):")
    if prompt.lower() != "yes" or prompt.lower() != "y":
        print("User block operation cancelled.")
        return
    else:
        url = f"{GITLAB_API_URL}/users/{USER_ID}/block"
        headers = {"PRIVATE-TOKEN": API_TOKEN}
        response = requests.post(url, headers=headers)

        if response.status_code == 201:
            print(f"User {USER_ID} has been blocked successfully.")
        elif response.status_code == 403:
            print("Permission denied: Make sure your token has admin privileges.")
        elif response.status_code == 404:
            print("User not found.")
        else:
            print(f"Failed to block user. Status code: {response.status_code}")
            print(response.text)


def fetch_username():
    script_root = os.path.dirname(os.path.abspath(__file__))
    userFile = os.path.join(script_root, "users.txt")
    with open(userFile, "r") as f:
        names = [line.strip() for line in f if line.strip()]
    return names

