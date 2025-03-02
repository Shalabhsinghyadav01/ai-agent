from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from typing import Dict, List
import time
import json

class LinkedInScraper:
    def __init__(self, browser):
        self.browser = browser
        self.wait = WebDriverWait(self.browser, 10)
        self.data_science_keywords = [
            'data science', 'machine learning', 'artificial intelligence', 'AI', 'ML',
            'deep learning', 'data analytics', 'data engineering', 'python', 'data visualization',
            'big data', 'neural networks', 'data mining', 'statistics', 'predictive analytics',
            'NLP', 'computer vision', 'tensorflow', 'pytorch', 'scikit-learn'
        ]

    def login(self, email: str, password: str) -> bool:
        """
        Log into LinkedIn using provided credentials
        """
        try:
            self.browser.get('https://www.linkedin.com/login')
            
            # Enter email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(email)
            
            # Enter password
            password_field = self.browser.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            return True
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def _is_data_science_related(self, content: str) -> bool:
        """
        Check if the post content is related to data science
        """
        content_lower = content.lower()
        return any(keyword.lower() in content_lower for keyword in self.data_science_keywords)

    def get_trending_posts(self, num_posts: int = 10) -> List[Dict]:
        """
        Scrape trending posts from LinkedIn feed, focusing on data science content
        """
        trending_posts = []
        data_science_posts_found = 0
        try:
            # Navigate to LinkedIn feed
            self.browser.get('https://www.linkedin.com/feed/')
            time.sleep(5)  # Wait for feed to load
            
            # Keep scrolling until we find enough data science related posts
            while data_science_posts_found < num_posts:
                # Scroll to load more posts
                self._scroll_feed(num_posts)
                
                # Find all post containers
                posts = self.browser.find_elements(
                    By.CSS_SELECTOR, 
                    "div.feed-shared-update-v2"
                )
                
                for post in posts:
                    try:
                        # Extract post information
                        post_data = self._extract_post_data(post)
                        if post_data and self._is_data_science_related(post_data['content']):
                            if post_data not in trending_posts:  # Avoid duplicates
                                trending_posts.append(post_data)
                                data_science_posts_found += 1
                                if data_science_posts_found >= num_posts:
                                    break
                    except Exception as e:
                        print(f"Error extracting post data: {str(e)}")
                        continue
                        
        except Exception as e:
            print(f"Error scraping trending posts: {str(e)}")
            
        return trending_posts

    def _scroll_feed(self, num_posts: int):
        """
        Scroll the feed to load more posts
        """
        posts_loaded = 0
        max_scrolls = num_posts * 2  # Account for ads and other content
        scroll_count = 0
        
        while posts_loaded < num_posts and scroll_count < max_scrolls:
            self.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(2)
            
            posts = self.browser.find_elements(
                By.CSS_SELECTOR, 
                "div.feed-shared-update-v2"
            )
            posts_loaded = len(posts)
            scroll_count += 1

    def _extract_post_data(self, post_element) -> Dict:
        """
        Extract relevant data from a post element
        """
        try:
            # Get author information
            author_element = post_element.find_element(
                By.CSS_SELECTOR, 
                "span.feed-shared-actor__name"
            )
            author_name = author_element.text
            
            # Get post content
            content_element = post_element.find_element(
                By.CSS_SELECTOR, 
                "div.feed-shared-update-v2__description"
            )
            content = content_element.text
            
            # Get engagement metrics
            reactions = self._get_engagement_count(
                post_element, 
                "button.social-details-social-counts__reactions-count"
            )
            comments = self._get_engagement_count(
                post_element, 
                "button.social-details-social-counts__comments-count"
            )
            
            return {
                "author": author_name,
                "content": content,
                "reactions": reactions,
                "comments": comments,
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Error extracting post data: {str(e)}")
            return None

    def _get_engagement_count(self, element, selector: str) -> int:
        """
        Extract engagement count from a post
        """
        try:
            count_element = element.find_element(By.CSS_SELECTOR, selector)
            count_text = count_element.text.replace(',', '')
            return int(count_text) if count_text.isdigit() else 0
        except:
            return 0 