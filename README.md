# YouTube Video Curation Assistant

A Streamlit application that helps you search, analyze, and curate YouTube videos using AI-powered insights.

## Features

- **YouTube Search**: Search for videos using keywords and filters
- **Date Range Filtering**: Filter videos by upload date (Last 7 days, Last 2 weeks, Last 1 month)
- **Language Filtering**: Option to filter for English language videos only (checks both title and description)
- **Video Duration**: View video length in the metadata preview
- **Local Search History**: 
  - Track search history with timestamps and search counts
  - Stored locally in a CSV file
- **Previous Searches**: View and reuse your past searches from the sidebar
- **Suggested Topics**: Discover related topics based on video tags from search results
- **Video Preview**: Watch videos directly in the app
- **Metadata Display**: View detailed video information including duration, views, and likes
- **Dynamic Results Display**: Results table adjusts height based on the number of videos found
- **Clean UI**: Streamlined interface with title and description combined for better readability

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
YOUTUBE_API_KEY=your_youtube_api_key
```

## Project Structure

```
youtube-video-curation-assistant/
├── app.py                 # Main Streamlit application
├── youtube_client.py      # YouTube API integration
├── search_history.py      # Local search history management
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in repo)
└── data/                  # Data directory
    └── search_history.csv # Local search history file
```

## Running the App

```bash
streamlit run app.py
```

## Requirements

- Python 3.10+
- YouTube Data API v3 key

## Dependencies

- streamlit==1.32.0
- google-api-python-client==2.118.0
- python-dotenv==1.0.1
- pandas==2.2.1
- langdetect==1.0.9
- isodate==0.6.1

## Usage

1. **Search for Videos**:
   - Enter a search term in the search box
   - Select a date range filter (optional)
   - Toggle "English Only" to filter for English language videos
   - Click "Search" to find videos

2. **View Results**:
   - Results show video title with description, duration, upload date, channel, views, and likes
   - Click on the "Video" link to watch the video
   - Upload dates are displayed in a clean YYYY-MM-DD HH:MM format

3. **Discover Related Topics**:
   - After a search, suggested topics appear based on video tags
   - Click on any suggested topic to perform a new search with that term
   - Topics are sorted alphabetically for easy browsing

4. **Previous Searches**:
   - View your search history in the sidebar
   - Click on any previous search to quickly perform that search again
   - Search history shows the number of times each term was searched

## Recent Updates

- **Improved English Language Filtering**: Now checks both video title and description for language detection
- **Local Search History**: Replaced Google Sheets integration with local CSV storage for better privacy and simplicity
- **Dynamic Search Results Header**: Shows the current search term and number of videos found
- **Fixed Timestamp Handling**: Improved handling of ISO format timestamps in search history
- **Streamlined UI**: Combined title and description into a single column for better readability
- **Formatted Upload Dates**: Cleaner display of video upload dates in YYYY-MM-DD HH:MM format

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 