from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import streamlit as st
import re
from langdetect import detect, LangDetectException

# Load environment variables
load_dotenv()

class YouTubeClient:
    def __init__(self):
        """Initialize YouTube API client"""
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YouTube API key not found in environment variables")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def _get_date_filter(self, date_range):
        """Convert date range selection to datetime object"""
        now = datetime.now()
        if date_range == "Last 7 days":
            return now - timedelta(days=7)
        elif date_range == "Last 2 weeks":
            return now - timedelta(weeks=2)
        elif date_range == "Last 1 month":
            return now - timedelta(days=30)
        return None

    def _format_duration(self, duration):
        """Convert ISO 8601 duration to human-readable format"""
        try:
            # Extract hours, minutes, and seconds using regex
            hours = re.search(r'(\d+)H', duration)
            minutes = re.search(r'(\d+)M', duration)
            seconds = re.search(r'(\d+)S', duration)
            
            # Convert to integers, default to 0 if not found
            h = int(hours.group(1)) if hours else 0
            m = int(minutes.group(1)) if minutes else 0
            s = int(seconds.group(1)) if seconds else 0
            
            # Format the duration
            if h > 0:
                return f"{h}:{m:02d}:{s:02d}"
            else:
                return f"{m}:{s:02d}"
        except Exception as e:
            st.write(f"Error formatting duration: {str(e)}")
            return "N/A"  # Return N/A if duration formatting fails

    def is_english(self, text):
        """Check if the given text is in English"""
        try:
            return detect(text) == 'en'
        except LangDetectException:
            return False

    def search_videos(self, query, date_filter="No date filter", english_only=True):
        """
        Search for YouTube videos with optional date filtering and language filtering
        Args:
            query (str): Search query
            date_filter (str): Date filter option
            english_only (bool): Whether to filter for English videos only
        Returns:
            list: List of video metadata dictionaries
        """
        # Calculate date range
        if date_filter == "Last 7 days":
            published_after = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
        elif date_filter == "Last 2 weeks":
            published_after = (datetime.now() - timedelta(days=14)).isoformat() + 'Z'
        elif date_filter == "Last 1 month":
            published_after = (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
        else:
            published_after = None

        # Prepare search parameters
        search_params = {
            'q': query,
            'part': 'snippet',
            'maxResults': 50,
            'type': 'video',
            'relevanceLanguage': 'en',
            'regionCode': 'US'
        }
        
        if published_after:
            search_params['publishedAfter'] = published_after

        # Execute search
        search_response = self.youtube.search().list(**search_params).execute()
        
        # Get video IDs for detailed information
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        
        # Get detailed video information
        videos_response = self.youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=','.join(video_ids)
        ).execute()

        # Process and filter results
        results = []
        filtered_count = 0
        
        for video in videos_response['items']:
            snippet = video['snippet']
            statistics = video.get('statistics', {})
            
            # Combine title and description for language detection
            text_to_check = f"{snippet['title']} {snippet.get('description', '')}"
            
            # Skip non-English videos if english_only is True
            if english_only and not self.is_english(text_to_check):
                filtered_count += 1
                continue
            
            # Format duration using the helper method
            try:
                formatted_duration = self._format_duration(video['contentDetails']['duration'])
            except Exception as e:
                st.write(f"Error formatting duration: {str(e)}")
                formatted_duration = "N/A"
            
            # Create video metadata dictionary
            video_data = {
                'title': snippet['title'],
                'video_url': f"https://www.youtube.com/watch?v={video['id']}",
                'duration': formatted_duration,
                'upload_date': snippet['publishedAt'].split('T')[0],
                'channel_name': snippet['channelTitle'],
                'view_count': statistics.get('viewCount', '0'),
                'like_count': statistics.get('likeCount', '0'),
                'description': snippet.get('description', ''),
                'search_term': query,
                'date_range': date_filter
            }
            
            results.append(video_data)
        
        # Add filtering statistics to the first result
        if results:
            results[0]['filtering_stats'] = {
                'total_videos': len(video_ids),
                'filtered_out': filtered_count,
                'english_only': english_only
            }
        
        return results 