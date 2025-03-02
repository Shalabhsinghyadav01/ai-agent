# LinkedIn AI Agent

An AI-powered agent that automatically scrapes trending LinkedIn posts, analyzes them using GPT-4, and reposts modified versions to your LinkedIn account.

## Features

- Automated scraping of trending LinkedIn posts
- AI-powered content analysis and generation using GPT-4
- Scheduled reposting at customizable intervals
- Engagement metrics tracking
- Headless browser operation

## Prerequisites

- Python 3.8+
- Chrome browser installed
- LinkedIn Developer Account
- OpenAI API key
- LinkedIn API credentials

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd linkedin_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the `config` directory:
```bash
cp config/.env.example config/.env
```

4. Configure your environment variables in `.env`:
- `LINKEDIN_CLIENT_ID`: Your LinkedIn API Client ID
- `LINKEDIN_CLIENT_SECRET`: Your LinkedIn API Client Secret
- `LINKEDIN_ACCESS_TOKEN`: Your LinkedIn Access Token
- `LINKEDIN_USER_ID`: Your LinkedIn User ID
- `OPENAI_API_KEY`: Your OpenAI API key
- `POSTS_PER_FETCH`: Number of posts to fetch per run (default: 10)
- `REPOST_INTERVAL_HOURS`: Hours between each run (default: 4)

## Usage

Run the agent scheduler:
```bash
python src/scheduler.py
```

The agent will:
1. Scrape trending posts from LinkedIn
2. Analyze each post using GPT-4
3. Generate new, unique content while maintaining the core message
4. Automatically post to your LinkedIn account
5. Repeat the process at the specified interval

## Security Notes

- Never commit your `.env` file
- Keep your API keys and credentials secure
- Monitor your LinkedIn account for any unusual activity
- Review and adjust the posting frequency as needed

## Limitations

- LinkedIn API rate limits apply
- Content generation depends on OpenAI API availability
- Scraping may be affected by LinkedIn UI changes
- Some posts may not be suitable for reposting

## Contributing

Feel free to submit issues and enhancement requests! 