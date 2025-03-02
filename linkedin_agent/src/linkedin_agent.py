import os
import time
from datetime import datetime, timedelta
from typing import Dict, List
import requests
from linkedin_api import Linkedin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from auth_manager import authenticate, LinkedInAuthManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import google.generativeai as genai

class LinkedInAgent:
    def __init__(self):
        load_dotenv()
        self.auth_manager = LinkedInAuthManager()
        credentials = self.auth_manager.get_credentials()
        if not credentials:
            raise Exception("LinkedIn authentication required")
        
        self.access_token = credentials['access_token']
        self.personal_profile_id = credentials.get('personal_profile_id')
        if not self.personal_profile_id:
            raise Exception("Could not determine personal profile ID")
            
        # Initialize headers for API calls
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Define data science related keywords and topics
        self.primary_keywords = [
            'data science', 'machine learning', 'artificial intelligence', 'deep learning',
            'python', 'data analytics', 'big data', 'data engineering',
            'mlops', 'data infrastructure', 'data tools', 'analytics'
        ]
        
        self.secondary_keywords = [
            'jupyter', 'pytorch', 'tensorflow', 'pandas', 'scikit-learn', 'numpy', 'matplotlib',
            'databricks', 'snowflake', 'airflow', 'kubernetes', 'docker', 'spark', 'kafka',
            'streamlit', 'plotly', 'hugging face', 'aws', 'azure', 'gcp', 'dbt', 'mlflow',
            'vscode', 'git', 'github', 'gitlab', 'power bi', 'tableau', 'looker',
            'python library', 'framework', 'platform', 'tool', 'software', 'application'
        ]
        
        self.excluded_keywords = [
            'visa', 'immigration', 'job posting', 'hiring', 'recruitment',
            'work permit', 'vacancy', 'job opportunity', 'course selling', 'bootcamp'
        ]
        
        # Add technical indicators for content filtering
        self.technical_indicators = [
            'how to', 'tutorial', 'guide', 'learn', 'implement', 'setup',
            'configuration', 'best practices', 'tips', 'tricks', 'comparison',
            'benchmark', 'performance', 'optimization', 'automation', 'deployment',
            'integration', 'workflow', 'architecture', 'features', 'updates',
            'released', 'announced', 'introducing', 'new version', 'latest'
        ]
        
        self.setup_gemini()
        self.setup_browser()

    def setup_credentials(self):
        """Initialize credentials using OAuth authentication"""
        auth_manager = authenticate()
        if not auth_manager:
            raise ValueError("Failed to authenticate with LinkedIn")
        
        credentials = auth_manager.get_credentials()
        self.access_token = credentials['access_token']
        self.user_id = credentials['user_id']
        self.user_name = credentials['name']
        
        # Initialize LinkedIn API client
        self.linkedin_client = Linkedin(
            access_token=self.access_token
        )
        
        print(f"Authenticated as: {self.user_name}")

    def setup_gemini(self):
        """Initialize Google Gemini API configuration"""
        self.gemini_api_key = os.getenv('GOOGLE_API_KEY')
        if not self.gemini_api_key:
            raise ValueError("Missing Google API key in environment variables")
        
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-001')

    def setup_browser(self):
        """Initialize browser for scraping with authentication"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        self.browser = webdriver.Chrome(service=service, options=chrome_options)
        
        # Login to LinkedIn
        self.browser.get('https://www.linkedin.com/login')
        time.sleep(2)
        
        # Get LinkedIn credentials from environment variables
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')
        
        if not email or not password:
            raise ValueError("LinkedIn credentials not found in environment variables")
        
        # Find and fill email field
        email_field = self.browser.find_element(By.ID, 'username')
        email_field.send_keys(email)
        
        # Find and fill password field
        password_field = self.browser.find_element(By.ID, 'password')
        password_field.send_keys(password)
        
        # Click sign in button
        sign_in_button = self.browser.find_element(By.CLASS_NAME, 'login__form_action_container')
        sign_in_button.click()
        
        # Wait for login to complete
        time.sleep(5)

    def is_relevant_data_science_content(self, content: str, author: str) -> bool:
        """
        Check if the content is relevant to data science tools and technologies
        """
        content_lower = content.lower()
        
        # Check for excluded topics first
        if any(keyword in content_lower for keyword in self.excluded_keywords):
            return False
            
        # Must contain at least one primary keyword
        has_primary = any(keyword in content_lower for keyword in self.primary_keywords)
        
        # Should contain specific tool mentions or technical depth
        has_secondary = any(keyword in content_lower for keyword in self.secondary_keywords)
        
        # Content should be substantial (at least 100 characters)
        is_substantial = len(content) >= 100
        
        # Check for technical indicators
        is_technical = any(indicator in content_lower for indicator in self.technical_indicators)
        
        # Return True if content meets our quality criteria
        # Now requiring either (primary + secondary) OR (primary + technical indicator)
        return is_substantial and has_primary and (has_secondary or is_technical)

    def scrape_trending_posts(self, num_posts: int = 10) -> List[Dict]:
        """Scrape trending posts using web scraping since API access is limited"""
        try:
            # Use selenium to scrape LinkedIn feed
            self.browser.get('https://www.linkedin.com/feed/')
            wait = WebDriverWait(self.browser, 10)
            
            # Wait for feed to load and scroll to load more posts
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.feed-shared-update-v2')))
            
            # Scroll more times to find quality content
            for _ in range(5):  # Increased from 3 to 5 scrolls
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            posts = self.browser.find_elements(By.CSS_SELECTOR, 'div.feed-shared-update-v2')
            trending_posts = []
            
            for post in posts:
                try:
                    content = self._extract_post_content(post)
                    author = self._extract_post_author(post)
                    
                    if content and self.is_relevant_data_science_content(content, author):
                        post_data = {
                            'content': content,
                            'author': author,
                            'timestamp': time.time()
                        }
                        trending_posts.append(post_data)
                        print(f"Found relevant data science post by {author}")
                        
                        # Break if we have enough quality posts
                        if len(trending_posts) >= num_posts:
                            break
                            
                except Exception as e:
                    print(f"Error processing post: {str(e)}")
                    continue
                    
            print(f"Found {len(trending_posts)} relevant data science posts")
            return trending_posts
            
        except Exception as e:
            print(f"Error fetching feed: {str(e)}")
            return []

    def _extract_post_content(self, post) -> str:
        """Extract content from a post with multiple selector attempts"""
        content_selectors = [
            'span.break-words',
            'div.feed-shared-text',
            'div.feed-shared-text-view',
            'div.feed-shared-update-v2__description-wrapper'
        ]
        
        for selector in content_selectors:
            try:
                content_elem = post.find_element(By.CSS_SELECTOR, selector)
                content = content_elem.text
                if content:
                    return content
            except:
                continue
        return None

    def _extract_post_author(self, post) -> str:
        """Extract author from a post with multiple selector attempts"""
        author_selectors = [
            'span.feed-shared-actor__name',
            'span.update-components-actor__name',
            'a.app-aware-link span'
        ]
        
        for selector in author_selectors:
            try:
                author_elem = post.find_element(By.CSS_SELECTOR, selector)
                author = author_elem.text
                if author:
                    return author
            except:
                continue
        return "Unknown Author"

    def analyze_post(self, post_content: str) -> str:
        """
        Analyze post content using Google Gemini API and generate a new version
        that is more descriptive and includes relevant hashtags
        """
        try:
            prompt = """You are a professional data science technology writer for LinkedIn. Create engaging, well-formatted posts about data science tools, technologies, and practical insights following these strict guidelines:

            1. Post Structure:
               - Start with a compelling headline about a specific tool or technology
               - Add 2 relevant emojis (e.g., 🛠️ 📊 or 💻 ⚡)
               - Skip a line after the headline
               - First paragraph: Introduce the tool/technology and its main purpose
               - Second paragraph: Share specific features, tips, or practical insights
               - Use bullet points for key technical details or best practices
               - End with a practical takeaway or pro tip
               - Skip a line before hashtags
               - End with 3-4 relevant hashtags combining tool name and concept

            2. Content Focus:
               - Emphasize practical tool usage and technical insights
               - Include specific features or capabilities
               - Share tips, tricks, or best practices
               - Mention version numbers or updates when relevant
               - Compare with other tools when appropriate
               - Focus on real-world applications
               - Include performance tips or optimization advice

            3. Formatting Rules:
               - Use actual bullet points (•) NOT asterisks
               - Keep paragraphs short and technical
               - Use clear spacing between sections
               - Maximum length: 1300 characters
               - Keep the tone professional but enthusiastic about technology

            Transform this content into a technical LinkedIn post following the above format:
            """

            # Clean up the input content
            cleaned_content = post_content.replace('**', '').replace('*', '').replace('#', '')
            
            response = self.model.generate_content(prompt + "\n\n" + cleaned_content)
            
            if response.text:
                # Clean up formatting
                final_content = response.text.strip()
                
                # Replace any remaining asterisks with bullet points
                final_content = final_content.replace('* ', '• ')
                final_content = final_content.replace('**', '')
                final_content = final_content.replace('*', '')
                
                # Ensure proper spacing
                final_content = final_content.replace('\n\n\n', '\n\n')
                
                # Ensure hashtags are properly formatted and at the end
                lines = final_content.split('\n')
                content_lines = []
                hashtags = []
                
                for line in lines:
                    if line.strip().startswith('#'):
                        # Collect hashtags
                        tags = line.strip().split()
                        hashtags.extend([tag for tag in tags if tag.startswith('#')])
                    else:
                        # Clean up any remaining asterisks in the line
                        cleaned_line = line.replace('**', '').replace('*', '')
                        if cleaned_line.strip():
                            content_lines.append(cleaned_line)
                
                # Reconstruct the post with proper spacing and hashtags at the end
                final_content = '\n'.join(content_lines).strip()
                if hashtags:
                    final_content += '\n\n' + ' '.join(hashtags[:4])  # Limit to 4 hashtags
                
                return final_content
            else:
                print("Gemini API returned empty response")
                return None

        except Exception as e:
            print(f"Error in analyzing post: {str(e)}")
            return None

    def create_post(self, content: str) -> bool:
        """Create a new post on LinkedIn using the basic post API"""
        try:
            # Ensure the content doesn't exceed LinkedIn's character limit
            if len(content) > 3000:
                content = content[:2997] + "..."

            url = 'https://api.linkedin.com/v2/ugcPosts'
            post_data = {
                "author": f"urn:li:person:{self.personal_profile_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            response = requests.post(url, headers=self.headers, json=post_data)
            if response.status_code in [201, 200]:
                print(f"Successfully created post at {datetime.now()}")
                return True
            else:
                print(f"Failed to create post: {response.text}")
                return False

        except Exception as e:
            print(f"Error in creating post: {str(e)}")
            return False

    def run(self):
        """
        Main execution method for the LinkedIn agent
        """
        try:
            # Get trending posts
            trending_posts = self.scrape_trending_posts(
                num_posts=int(os.getenv('POSTS_PER_FETCH', 10))
            )

            for post in trending_posts:
                # Analyze and generate new post content
                new_content = self.analyze_post(post['content'])
                
                if new_content:
                    # Create new post
                    success = self.create_post(new_content)
                    
                    if success:
                        print(f"Successfully reposted content at {datetime.now()}")
                    else:
                        print(f"Failed to create post at {datetime.now()}")
                    
                    # Wait between posts to avoid rate limiting
                    time.sleep(60)  # 1-minute delay between posts

        except Exception as e:
            print(f"Error in agent execution: {str(e)}")
        finally:
            self.browser.quit()

if __name__ == "__main__":
    agent = LinkedInAgent()
    agent.run() 