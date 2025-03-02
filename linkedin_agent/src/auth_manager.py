import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import webbrowser
import requests
from datetime import datetime, timedelta
import pickle
from pathlib import Path
import socket
import secrets

class LinkedInAuthManager:
    def __init__(self):
        self.config = {
            'redirect_uri': 'http://localhost:8000/callback',
            'scope': 'openid profile email w_member_social',
            'session_file': '.linkedin_session'
        }
        self.session_data = None
        self._load_session()
        self.personal_profile_id = None

    def _load_session(self):
        """Load existing session if available"""
        session_path = Path(self.config['session_file'])
        if session_path.exists():
            try:
                with open(session_path, 'rb') as f:
                    self.session_data = pickle.load(f)
                if self._is_session_valid():
                    self._get_personal_profile_id()
                    return True
            except Exception:
                pass
        return False

    def _get_user_profile(self):
        """Get user profile information using OpenID"""
        if not self.session_data or 'access_token' not in self.session_data:
            return None

        headers = {
            'Authorization': f'Bearer {self.session_data["access_token"]}',
            'Content-Type': 'application/json'
        }

        # Get OpenID user info
        response = requests.get('https://api.linkedin.com/v2/userinfo', headers=headers)
        if response.status_code == 200:
            profile = response.json()
            return {
                'user_id': profile['sub'],
                'name': profile.get('name', 'Unknown User'),
                'email': profile.get('email')
            }
        return None

    def _get_personal_profile_id(self):
        """Get and store personal profile ID for posting"""
        if not self.session_data or 'access_token' not in self.session_data:
            return None

        headers = {
            'Authorization': f'Bearer {self.session_data["access_token"]}',
            'Content-Type': 'application/json'
        }

        # Get OpenID user info for profile ID
        response = requests.get('https://api.linkedin.com/v2/userinfo', headers=headers)
        if response.status_code == 200:
            profile = response.json()
            self.personal_profile_id = profile['sub']
            self.session_data['personal_profile_id'] = self.personal_profile_id
            self._save_session()
            return self.personal_profile_id
        return None

    def get_posting_profile(self):
        """Get the profile ID to use for posting"""
        return self.personal_profile_id or self.session_data.get('personal_profile_id')

    def _save_session(self):
        """Save session data"""
        with open(self.config['session_file'], 'wb') as f:
            pickle.dump(self.session_data, f)

    def _is_session_valid(self):
        """Check if current session is valid"""
        if not self.session_data:
            return False
        expiry = datetime.fromtimestamp(self.session_data.get('expires_at', 0))
        return datetime.now() < expiry

    def get_auth_url(self):
        """Generate LinkedIn authentication URL"""
        print("\nPlease follow these steps to authenticate with LinkedIn:")
        print("1. Go to https://www.linkedin.com/developers/apps")
        print("2. Click 'Create app' if you haven't already")
        print("3. Fill in the required information")
        print("4. Once created, copy the Client ID when shown\n")
        
        client_id = input("Please enter your LinkedIn Client ID: ").strip()
        
        # Store client_id temporarily for the session
        self.config['client_id'] = client_id
        
        # Generate state parameter for security
        state = secrets.token_urlsafe(16)
        self.config['state'] = state
        
        return (
            'https://www.linkedin.com/oauth/v2/authorization?'
            'response_type=code&'
            f'client_id={client_id}&'
            f'redirect_uri={self.config["redirect_uri"]}&'
            f'scope={self.config["scope"]}&'
            f'state={state}'
        )

    def handle_callback(self, authorization_code, state):
        """Exchange authorization code for access token"""
        if state != self.config.get('state'):
            print("State parameter mismatch! Possible security issue.")
            return False
            
        print("\nPlease enter your LinkedIn Client Secret.")
        print("You can find this in your LinkedIn App's settings page.")
        client_secret = input("Client Secret: ").strip()
        
        token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'client_id': self.config['client_id'],
            'client_secret': client_secret,
            'redirect_uri': self.config['redirect_uri']
        }

        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.session_data = {
                'access_token': token_data['access_token'],
                'expires_at': datetime.now().timestamp() + token_data['expires_in']
            }
            
            # Get user profile data and personal profile ID
            user_data = self._get_user_profile()
            if user_data:
                self.session_data.update(user_data)
            
            self._get_personal_profile_id()
            self._save_session()
            return True
        return False

    def get_credentials(self):
        """Get current credentials"""
        if self._is_session_valid():
            return self.session_data
        return None

class AuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if '/callback' in self.path:
            query_components = parse_qs(urlparse(self.path).query)
            
            if 'error' in query_components:
                self._send_error_response(f"Authentication error: {query_components['error'][0]}")
                return
                
            if 'code' in query_components and 'state' in query_components:
                auth_code = query_components['code'][0]
                state = query_components['state'][0]
                if self.server.auth_manager.handle_callback(auth_code, state):
                    self._send_success_response()
                else:
                    self._send_error_response("Failed to authenticate with LinkedIn")
            else:
                self._send_error_response("No authorization code received")

    def _send_success_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; text-align: center;">
            <h1 style="color: #0077B5;">Successfully Connected to LinkedIn!</h1>
            <p>You can now close this window and return to the application.</p>
            <script>
                setTimeout(function() {
                    window.close();
                }, 3000);
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def _send_error_response(self, error_message):
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; text-align: center;">
            <h1 style="color: #ff0000;">Authentication Error</h1>
            <p>{error_message}</p>
            <p>Please close this window and try again.</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

def authenticate():
    """Main authentication function"""
    auth_manager = LinkedInAuthManager()
    
    # Check for existing valid session
    if auth_manager.get_credentials():
        print("Using existing LinkedIn session")
        return auth_manager
    
    # Start local server for OAuth callback
    server = HTTPServer(('localhost', 8000), AuthCallbackHandler)
    server.auth_manager = auth_manager
    
    # Open browser for authentication
    auth_url = auth_manager.get_auth_url()
    print("\nOpening browser for LinkedIn authentication...")
    webbrowser.open(auth_url)
    
    # Handle callback
    print("Waiting for authentication...")
    server.handle_request()
    
    if auth_manager.get_credentials():
        print("Successfully authenticated with LinkedIn!")
        return auth_manager
    else:
        print("Failed to authenticate with LinkedIn")
        return None

if __name__ == "__main__":
    auth_manager = authenticate()
    if auth_manager:
        credentials = auth_manager.get_credentials()
        print(f"Authenticated as: {credentials.get('name', 'Unknown User')}") 