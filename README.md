# LinkedIn Content Agent 🤖

An intelligent automated content management system for LinkedIn that leverages Google's Gemini AI to curate, analyze, and post high-quality data science content.

## 🌟 Features

- **AI-Powered Content Curation**: Utilizes Google's Gemini-1.5-pro-001 model for intelligent content analysis and generation
- **Automated Posting Schedule**: Posts twice daily (10 AM and 3 PM) with smart recovery for missed posts
- **Data Science Focus**: Specialized in curating technical content related to data science, machine learning, and AI
- **Professional Formatting**: Ensures business-appropriate content with proper structure and formatting
- **Smart Recovery System**: Handles system interruptions (sleep/shutdown) by tracking and recovering missed posts
- **Secure Credential Management**: Uses environment variables for secure storage of API keys and credentials

## 🛠️ Technical Architecture

### Components
1. **LinkedIn Agent (`linkedin_agent.py`)**
   - Handles LinkedIn authentication and interaction
   - Implements content scraping and filtering
   - Manages post analysis and creation
   - Ensures professional content formatting

2. **Scheduler (`scheduler.py`)**
   - Manages posting schedule (10 AM and 3 PM)
   - Implements smart recovery for missed posts
   - Handles background process management
   - Maintains logging and status tracking

3. **Authentication Manager (`auth_manager.py`)**
   - Manages LinkedIn OAuth authentication
   - Handles session management
   - Secures credential storage

## 🚀 Setup and Installation

### Prerequisites
- Python 3.8+
- LinkedIn Developer Account
- Google Cloud Account (for Gemini API)

### Environment Setup
1. Clone the repository
```bash
git clone [repository-url]
cd linkedin-agent
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment variables
Create a `.env` file with:
```
GOOGLE_API_KEY=your_gemini_api_key
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password
POSTS_PER_FETCH=10
REPOST_INTERVAL_HOURS=4
MIN_ENGAGEMENT_THRESHOLD=50
```

### LinkedIn Authentication
1. Create an app on LinkedIn Developer Portal
2. Run the authentication manager:
```bash
python3 src/auth_manager.py
```
3. Follow the prompts to complete OAuth authentication

## 🎯 Usage

### Starting the Agent
Run the agent in the background:
```bash
./run_agent.sh start
```

### Checking Status
```bash
./run_agent.sh status
```

### Stopping the Agent
```bash
./run_agent.sh stop
```

### Monitoring Logs
```bash
tail -f logs/linkedin_agent.log
```

## 📊 Content Strategy

The agent implements a sophisticated content strategy:

1. **Morning Posts (10 AM)**
   - Focus on technical content
   - In-depth analysis of data science topics
   - Educational content and tutorials

2. **Afternoon Posts (3 PM)**
   - Case studies and practical applications
   - Industry trends and insights
   - Real-world implementations

### Content Filtering
- Primary keywords focus on data science, machine learning, AI
- Secondary keywords ensure technical relevance
- Exclusion filters for non-relevant content
- Quality checks for content length and depth

## 🔒 Security

- Credentials stored in environment variables
- Session management for secure authentication
- No hardcoded sensitive information
- Secure OAuth implementation

## 📝 Logging and Monitoring

- Comprehensive logging system
- Post tracking and verification
- Recovery status monitoring
- Performance metrics tracking

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for content analysis
- LinkedIn API for platform integration
- Open source community for various dependencies

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

---
Built with ❤️ for the Data Science Community 