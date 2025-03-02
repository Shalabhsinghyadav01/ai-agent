import schedule
import time
import os
from dotenv import load_dotenv
from linkedin_agent import LinkedInAgent
from datetime import datetime

def run_agent():
    """
    Initialize and run the LinkedIn agent
    """
    try:
        agent = LinkedInAgent()
        
        # Get current hour to determine which set of posts to use
        current_hour = datetime.now().hour
        
        # Morning post (more technical/tutorial content)
        if 9 <= current_hour < 12:
            print("Executing morning post (technical content)")
            trending_posts = agent.scrape_trending_posts(num_posts=3)  # Get more posts to choose from
            if trending_posts:
                # Select the most detailed/technical post
                selected_post = max(trending_posts, key=lambda x: len(x['content']))
                new_content = agent.analyze_post(selected_post['content'])
                if new_content:
                    agent.create_post(new_content)
                    
        # Evening post (case studies/practical applications)
        elif 14 <= current_hour < 17:
            print("Executing evening post (practical applications)")
            trending_posts = agent.scrape_trending_posts(num_posts=3)  # Get more posts to choose from
            if trending_posts:
                # Select the most detailed/technical post
                selected_post = max(trending_posts, key=lambda x: len(x['content']))
                new_content = agent.analyze_post(selected_post['content'])
                if new_content:
                    agent.create_post(new_content)
    except Exception as e:
        print(f"Error running agent: {str(e)}")

def main():
    """
    Main function to schedule and run the LinkedIn agent
    """
    load_dotenv()
    
    print("Starting LinkedIn Agent Scheduler (posting twice daily)")
    
    # Schedule morning post (around 10 AM)
    schedule.every().day.at("10:00").do(run_agent)
    
    # Schedule evening post (around 3 PM)
    schedule.every().day.at("15:00").do(run_agent)
    
    # Run the agent once immediately if within posting hours
    current_hour = datetime.now().hour
    if (9 <= current_hour < 12) or (14 <= current_hour < 17):
        run_agent()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check schedule every minute

if __name__ == "__main__":
    main() 