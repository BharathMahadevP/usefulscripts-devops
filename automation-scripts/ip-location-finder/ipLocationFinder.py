import requests
from dotenv import load_dotenv
import os

load_dotenv()

# sign in and generate a token from https://ipinfo.io/dashboard/token and add it to .env filein the same directory
API_TOKEN = os.getenv("API_TOKEN") 
API_URL = "https://ipinfo.io/{ip}/json"


def fetch_ip_from_user():
    # Fetch IP address from user input.
    ip = input("Enter the IP address: ")
    return ip


def fetch_ip_details(ip, API_TOKEN, API_URL):
    print(f"Fetching details for IP: {ip}")
    try:
        response = requests.get(
            API_URL.format(ip=ip), headers={"Authorization": f"Bearer {API_TOKEN}"}
        )
        data = response.json()
        return data
    except Exception as e:
        print(f"Error fetching data for {ip}: {e}")
        return "N/A", "N/A"


def parsingPrint_ip_details(data):
    # Parse the IP details and return them.
    print()
    region = data.get("region", "N/A")
    country = data.get("country", "N/A")
    org = data.get("org", "N/A")

    print(f"Region: {region}")
    print(f"Country: {country}")
    print(f"Org: {org}")


def display_ip_details(API_TOKEN, API_URL):
    ip = fetch_ip_from_user()
    data = fetch_ip_details(ip, API_TOKEN, API_URL)
    parsingPrint_ip_details(data)


display_ip_details(API_TOKEN, API_URL)