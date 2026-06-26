import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Salesforce credentials
CLIENT_ID = os.getenv("SF_CLIENT_ID")
CLIENT_SECRET = os.getenv("SF_CLIENT_SECRET")
USERNAME = os.getenv("SF_USERNAME")
PASSWORD = os.getenv("SF_PASSWORD")
SECURITY_TOKEN = os.getenv("SF_SECURITY_TOKEN")

print("Connecting to Salesforce...")

# OAuth URL
url = "https://test.salesforce.com/services/oauth2/token"

print("USERNAME:", USERNAME)
print("PASSWORD:", PASSWORD)
print("TOKEN:", SECURITY_TOKEN)
print("CLIENT ID:", CLIENT_ID[:10])
# Request payload
payload = {
    "grant_type": "password",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "username": USERNAME,
    "password": PASSWORD + SECURITY_TOKEN
}

try:
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        data = response.json()

        print("Salesforce Connected Successfully")
        print("Access Token Received")
        print("Instance URL:", data["instance_url"])

    else:
        print("Connection Failed")
        print("Status Code:", response.status_code)
        print(response.text)

except Exception as e:
    print("Error:", e)