import base64
import requests
import pandas as pd
import string
import random

def update_github_file(
    token: str,
    repo_owner: str,
    repo_name: str,
    file_path: str,
    new_content: str,
    commit_message: str = "Update file via API",
    committer_name: str = "Dev",
    committer_email: str = "dev@example.com"
):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    # Get the current file SHA
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json()["sha"]
    elif response.status_code == 404:
        sha = None  # File doesn't exist yet
    else:
        raise Exception(f"Failed to get file SHA: {response.text}")

    # Encode new content to base64
    encoded_content = base64.b64encode(new_content.encode()).decode()

    data = {
        "message": commit_message,
        "content": encoded_content,
        "committer": {
            "name": committer_name,
            "email": committer_email
        },
        "sha": sha  # optional if file doesn't exist yet
    }

    put_response = requests.put(url, headers=headers, json=data)

    if put_response.status_code in [200, 201]:
        print("✅ File updated successfully!")
        return put_response.json()
    else:
        raise Exception(f"❌ Failed to update file: {put_response.status_code} - {put_response.text}")
        print('Failed to update GIT')
        return 'Failed GIT'

def generate_random_key_git(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def get_existing_keys_git(csv_url):
    try:
        # Use the *raw* GitHub URL, not the edit URL!
        df = pd.read_csv(csv_url)
        first_col = df.columns[0]
        return set(df[first_col].astype(str).values)
    except Exception as e:
        print("❌ Error reading CSV:", e)
        return set()

def generate_unique_key_git(csv_url, max_attempts=20):
    existing_keys = get_existing_keys_git(csv_url)
    
    for _ in range(max_attempts):
        key = generate_random_key_git()
        if key not in existing_keys:
            return key
    
    raise Exception("💥 Failed to generate a unique key after many tries.")

              
