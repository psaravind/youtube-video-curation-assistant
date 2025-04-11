# YouTube Video Curation Assistant

A Streamlit application that helps you search, analyze, and curate YouTube videos using AI-powered insights.

## Features

- **YouTube Search**: Search for videos using keywords and filters
- **AI-Powered Analysis**: Get AI-generated insights about each video
- **Video Duration**: View video length in the metadata preview
- **Google Sheets Integration**: 
  - Save selected videos to Google Sheets
  - Track search history with timestamps
- **Search History**: View and manage your past searches (stored in Google Sheets)
- **Video Preview**: Watch videos directly in the app
- **Metadata Display**: View detailed video information including duration

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-video-curation-assistant.git
cd youtube-video-curation-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your API keys and configuration:
```
OPENAI_API_KEY=your_openai_api_key
YOUTUBE_API_KEY=your_youtube_api_key
GOOGLE_SHEETS_ID=your_google_sheets_id
GOOGLE_SHEETS_CREDENTIALS_PATH=creds/youtube-video-curation-456516-76975cfec573.json
```

5. Set up Google Sheets:
   - Create a Google Cloud project
   - Enable YouTube Data API v3 and Google Sheets API
   - Create a service account and download credentials
   - Place the credentials file in the `creds` directory
   - Share your Google Sheet with the service account email

## Google Sheets Integration

The app uses two tabs in your Google Sheet:
1. **YouTube Videos**: Stores saved video metadata
2. **Search_History**: Tracks search terms with timestamps and counts

## Project Structure

```
youtube-video-curation-assistant/
├── app.py                 # Main Streamlit application
├── youtube_client.py      # YouTube API integration
├── sheets_client.py       # Google Sheets integration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in repo)
└── creds/                 # Credentials directory (not in repo)
    └── youtube-video-curation-456516-76975cfec573.json
```

## Running the App

```bash
streamlit run app.py
```

## Requirements

- Python 3.10+
- OpenAI API key
- YouTube Data API v3 key
- Google Cloud project with:
  - YouTube Data API v3 enabled
  - Google Sheets API enabled
  - Service account credentials

## Dependencies

- streamlit==1.32.0
- openai==1.12.0
- google-api-python-client==2.118.0
- google-auth-httplib2==0.2.0
- google-auth-oauthlib==1.2.0
- gspread==6.0.2
- python-dotenv==1.0.1
- pandas==2.2.1
- numpy==1.26.4

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 