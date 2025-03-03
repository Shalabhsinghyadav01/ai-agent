import schedule
import time
import os
import logging
from dotenv import load_dotenv
from linkedin_agent import LinkedInAgent
from datetime import datetime, timedelta

def setup_logging():
    """Configure logging to file and console"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, "linkedin_agent.log")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def should_post_now(target_hour: int) -> bool:
    """Check if we should post now based on the target hour"""
    now = datetime.now()
    last_post_file = f"logs/last_post_{target_hour}.txt"
    
    try:
        if os.path.exists(last_post_file):
            with open(last_post_file, 'r') as f:
                last_post_str = f.read().strip()
                last_post = datetime.fromisoformat(last_post_str)
                
                # If last post was today and at/after target hour, skip
                if (last_post.date() == now.date() and 
                    last_post.hour >= target_hour):
                    return False
    except Exception as e:
        logging.warning(f"Error reading last post time: {e}")
    
    # Post if current hour is within 2 hours after target hour
    # This allows recovery from short interruptions while preventing duplicate posts
    return (now.hour >= target_hour and 
            now.hour < target_hour + 2)  # Changed from <= target_hour + 5

def record_post(target_hour: int):
    """Record the time of successful post"""
    try:
        with open(f"logs/last_post_{target_hour}.txt", 'w') as f:
            f.write(datetime.now().isoformat())
    except Exception as e:
        logging.error(f"Error recording post time: {e}")

def run_agent(target_hour: int = None):
    """
    Initialize and run the LinkedIn agent
    """
    try:
        # Skip if we shouldn't post now
        if target_hour is not None and not should_post_now(target_hour):
            logging.info(f"Skipping post for {target_hour}:00, already posted or too late")
            return

        logging.info(f"Starting agent run for {target_hour}:00" if target_hour else "Starting agent run")
        agent = LinkedInAgent()
        agent.run()
        logging.info("Agent run completed successfully")
        
        # Record successful post
        if target_hour is not None:
            record_post(target_hour)
            
    except Exception as e:
        logging.error(f"Error running agent: {str(e)}", exc_info=True)

def check_missed_posts():
    """Check and handle any missed posts"""
    now = datetime.now()
    target_hours = [10, 15]  # 10 AM and 3 PM
    
    for hour in target_hours:
        try:
            if should_post_now(hour):
                logging.info(f"Detected missed post for {hour}:00, running recovery")
                run_agent(hour)
        except Exception as e:
            logging.error(f"Error checking missed post for {hour}:00: {e}")

def main():
    """
    Main function to schedule and run the LinkedIn agent
    """
    try:
        load_dotenv()
        setup_logging()
        
        logging.info("Starting LinkedIn Agent Scheduler (posting twice daily at 10:00 AM and 3:00 PM)")
        
        # Schedule morning post (10:00 AM)
        schedule.every().day.at("10:00").do(run_agent, target_hour=10)
        
        # Schedule afternoon post (3:00 PM)
        schedule.every().day.at("15:00").do(run_agent, target_hour=15)
        
        # Check for missed posts on startup, but only if within recovery window
        now = datetime.now()
        if now.hour in [10, 11, 15, 16]:  # Only check during recovery windows
            check_missed_posts()
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check schedule every minute
            
            # Remove hourly checks for missed posts to prevent duplicates
            # The scheduled tasks will handle regular posting
            
    except Exception as e:
        logging.error(f"Critical error in scheduler: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 