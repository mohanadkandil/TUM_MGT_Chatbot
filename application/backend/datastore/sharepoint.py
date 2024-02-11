import requests


def get_access_token():
    url = "https://login.microsoftonline.com/5d7b49e9-50d2-40dc-bab1-14a2d903542c/oauth2/v2.0/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": "67c0753e-5041-4357-8016-c92be90a4538",
        "client_secret": "MrD8Q~oyj7kCNy2jnJobOvTpWCjuKyGU4YUKla9B",
        "scope": "https://graph.microsoft.com/.default",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        # Assuming the response is a JSON token response
        token_response = response.json()
        access_token = token_response.get("access_token", "")
        return access_token
    else:
        raise Exception(
            f"Failed to obtain access token, status code {response.status_code}"
        )


# Example usage:
access_token = get_access_token()
print(access_token)


import requests


def get_sharepoint_drive(bearer_token):
    url = "https://graph.microsoft.com/v1.0/sites/tumde.sharepoint.com,d739bc85-bbc4-421c-971b-246e1a0a75e5,fd3afd60-4c56-43e0-b822-bfdd83ae4a11/drive"

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Failed to retrieve SharePoint drive information, status code {response.status_code}"
        )


# Example usage:
bearer_token = get_access_token()
drive_info = get_sharepoint_drive(bearer_token)
print(drive_info)

import requests


def get_sharepoint_list_id(site_url, bearer_token):
    # Prepare the headers for the request
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    # Retrieve the site-id
    site_endpoint = f"https://graph.microsoft.com/v1.0/sites/tumde.sharepoint.com,d739bc85-bbc4-421c-971b-246e1a0a75e5,fd3afd60-4c56-43e0-b822-bfdd83ae4a11"
    site_response = requests.get(site_endpoint, headers=headers)

    if site_response.status_code != 200:
        raise Exception(
            f"Failed to retrieve SharePoint site information, status code {site_response.status_code}"
        )

    site_id = site_response.json().get("id")

    # Once we have the site-id, we can list the document libraries
    files_endpoint = f"https://graph.microsoft.com/v1.0/drives/b!hbw518S7HEKXGyRuGgp15WD9Ov1WTOBDuCK_3YOuShGyU2MPunGjTIaMwT45A-Fy/items/root/children"
    lists_response = requests.get(files_endpoint, headers=headers)
    print(lists_response.json())


# Example usage:
site_url = "tumde.sharepoint.com:/sites/MGTChatbot"
bearer_token = get_access_token()
list_id = get_sharepoint_list_id(site_url, bearer_token)
print(list_id)
