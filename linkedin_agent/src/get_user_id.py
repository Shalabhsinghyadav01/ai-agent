import requests
import os
from dotenv import load_dotenv

def get_linkedin_user_id():
    load_dotenv()
    
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    if not access_token:
        print("Please set your LINKEDIN_ACCESS_TOKEN in the .env file first!")
        return
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    try:
        # Make request to LinkedIn API
        response = requests.get(
            'https://api.linkedin.com/v2/me',
            headers=headers
        )
        
        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data['id']
            print(f"\nYour LinkedIn User ID is: {user_id}")
            print("Please add this to your .env file as LINKEDIN_USER_ID")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    get_linkedin_user_id() 