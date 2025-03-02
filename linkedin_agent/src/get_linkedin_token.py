from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import webbrowser
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8000/callback'
PORT = 8000

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if '/callback' in self.path:
            # Get the authorization code from the callback URL
            query_components = parse_qs(urlparse(self.path).query)
            authorization_code = query_components['code'][0]

            # Exchange authorization code for access token
            token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
            data = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI
            }

            response = requests.post(token_url, data=data)
            if response.status_code == 200:
                access_token = response.json()['access_token']
                
                # Display the access token
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = f"""
                <html>
                <body>
                    <h1>LinkedIn Access Token Retrieved Successfully!</h1>
                    <p>Your access token is:</p>
                    <textarea rows="5" cols="50" onclick="this.select()">{access_token}</textarea>
                    <p>Please copy this token and add it to your .env file as LINKEDIN_ACCESS_TOKEN</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
            else:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'Failed to get access token')

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Please set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in your .env file first!")
        return

    # Start local server
    server = HTTPServer(('localhost', PORT), AuthHandler)
    print(f"Starting server at http://localhost:{PORT}")

    # Generate authorization URL
    auth_url = (
        'https://www.linkedin.com/oauth/v2/authorization?'
        f'response_type=code&'
        f'client_id={CLIENT_ID}&'
        f'redirect_uri={REDIRECT_URI}&'
        'scope=r_liteprofile%20r_emailaddress%20w_member_social'
    )

    # Open browser for authentication
    print("Opening browser for LinkedIn authentication...")
    webbrowser.open(auth_url)

    # Handle callback
    print("Waiting for authentication callback...")
    server.handle_request()
    
    print("\nServer stopped. You can close this window.")

if __name__ == '__main__':
    main() 