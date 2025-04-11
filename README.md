# YouTube Video Curation Assistant

A Streamlit application that helps you search for YouTube videos, preview their metadata, and save selected entries to Google Sheets.

## Features

- Search YouTube videos with customizable date filters
- Preview video metadata including title, URL, upload date, channel name, view count, like count, and duration
- Select/deselect videos for saving
- Save selected videos to Google Sheets
- Track search history in Google Sheets with timestamps and search counts
- Re-run past searches with one click
- Display up to 50 search results at once

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root with:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key
   GOOGLE_SHEETS_ID=your_spreadsheet_id
   GOOGLE_SHEETS_CREDENTIALS_PATH=creds/youtube-video-curation-456516-76975cfec573.json
   ```

4. Set up Google Sheets API:
   - Create a Google Cloud Project
   - Enable YouTube Data API v3 and Google Sheets API
   - Create a service account and download credentials
   - Place the credentials file in the `creds` directory
   - Share your Google Sheet with the service account email

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Enter a search term and select a date range
3. Click "Search" to find videos
4. Review the results and deselect any unwanted videos
5. Click "Save Selected to Google Sheets" to save selected videos

## Google Sheets Integration

The app creates and manages two tabs in your Google Sheet:

1. **YouTube Videos**: Stores video metadata for saved videos
   - Columns: Title, Video URL, Upload Date, Channel Name, View Count, Like Count, Description, Search Term, Date Range, Added Date

2. **Search_History**: Tracks your search history
   - Columns: Search Term, Timestamp, Count (number of times searched)

## Project Structure

```
project-root/
├── app.py                    # Main Streamlit app
├── youtube_client.py         # YouTube API search logic
├── sheets_client.py          # Google Sheets writer
├── data/                     # Local data storage
├── creds/                    # Google API credentials
│   └── youtube-video-curation-456516-76975cfec573.json
└── requirements.txt          # Python dependencies
```

## Requirements

- Python 3.8+
- Streamlit 1.32.0
- Google API Python Client 2.118.0
- gspread 5.12.4
- pandas 2.2.1
- python-dotenv 1.0.1 

# Environment variables
.env

# Python cache files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual environment
venv/
ENV/
.venv/

# IDE files
.idea/
.vscode/
*.swp
*.swo

# OS specific files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db 