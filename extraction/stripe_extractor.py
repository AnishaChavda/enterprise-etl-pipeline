import requests
import json

print("Stripe Extraction Started")

# Public practice API
url = "https://jsonplaceholder.typicode.com/users"

# Send GET request
response = requests.get(url)

# Print status code
print("Status Code:", response.status_code)

# Convert response to JSON
data = response.json()

# Print data
print("Total Records:", len(data))
print("First User:", data[0]["name"])

# Save JSON file
with open("data/raw/stripe/users.json", "w") as file:
    json.dump(data, file, indent=4)

print("Data saved successfully")