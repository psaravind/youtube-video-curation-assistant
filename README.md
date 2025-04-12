# YouTube Video Curation Assistant

A Streamlit-based web application that helps you search, filter, and curate YouTube videos. The application provides an intuitive interface for searching YouTube videos with various filters and maintains a local search history.

## Features

- 🔍 **YouTube Video Search**: Search for videos using keywords
- 📅 **Date Filtering**: Filter videos by upload date (Last 7 days, 2 weeks, 1 month)
- 🌐 **Language Filtering**: Filter for English language videos only
- 📝 **Search History**: Maintains a local history of your searches
- 🏷️ **Suggested Topics**: Shows related topics based on search results
- 📊 **Interactive Results**: View and select videos in a dynamic data table
- 🔗 **Direct Links**: Click to watch videos directly from the results

## Prerequisites

- Python 3.10 or higher
- YouTube Data API v3 key
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-video-curation-assistant.git
cd youtube-video-curation-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your YouTube API key:
```
YOUTUBE_API_KEY=your_api_key_here
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to the provided URL (typically http://localhost:8502)

3. Enter a search term and use the filters to refine your search

4. Click on videos in the results to watch them directly

5. Use the sidebar to access your search history

## Project Structure

- `app.py`: Main Streamlit application
- `youtube_client.py`: YouTube API client implementation
- `search_history.py`: Local search history management
- `requirements.txt`: Project dependencies
- `.env`: Environment variables (not tracked in git)

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses [YouTube Data API v3](https://developers.google.com/youtube/v3)
- Inspired by the need for better YouTube video curation tools 