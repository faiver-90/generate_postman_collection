import requests

with open("postman_api_key.txt", "r") as f:
    api_key = f.read().strip()

response = requests.get(
    "https://api.getpostman.com/workspaces",
    headers={"X-Api-Key": api_key}
)

print(response.json())
