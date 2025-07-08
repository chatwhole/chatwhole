import requests

ZENDESK_SUBDOMAIN = "your_subdomain"
ZENDESK_EMAIL = "your_email"
ZENDESK_API_TOKEN = "your_api_token"

BASE_URL = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2"

def create_ticket(subject: str, description: str, requester_email: str):
    url = f"{BASE_URL}/tickets.json"
    headers = {
        "Content-Type": "application/json"
    }
    auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)
    data = {
        "ticket": {
            "subject": subject,
            "comment": {"body": description},
            "requester": {"email": requester_email}
        }
    }
    response = requests.post(url, json=data, headers=headers, auth=auth)
    response.raise_for_status()
    return response.json()

# Additional Zendesk API integration functions can be added here
