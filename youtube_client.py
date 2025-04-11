from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import streamlit as st
import re

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

    def search_videos(self, query, date_range="No date filter"):
        """
        Search for YouTube videos matching the query
        
        Args:
            query (str): Search term
            date_range (str): Date range filter
            
        Returns:
            list: List of video metadata dictionaries
        """
        # Prepare search parameters
        search_params = {
            'q': query,
            'part': 'snippet',
            'type': 'video',
            'maxResults': 50
        }

        # Add date filter if specified
        published_after = self._get_date_filter(date_range)
        if published_after:
            search_params['publishedAfter'] = published_after.isoformat() + 'Z'

        # Execute search
        search_response = self.youtube.search().list(**search_params).execute()
        
        # Get video IDs for detailed information
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        st.write(f"Found {len(video_ids)} videos in initial search")
        
        # Get detailed video information
        videos_response = self.youtube.videos().list(
            part='snippet,statistics,contentDetails',  # Added contentDetails for duration
            id=','.join(video_ids)
        ).execute()

        # Process and format results
        results = []
        for video in videos_response['items']:
            try:
                # Get duration with fallback
                duration = "N/A"
                if 'contentDetails' in video and 'duration' in video['contentDetails']:
                    duration = self._format_duration(video['contentDetails']['duration'])
                
                video_data = {
                    'title': video['snippet']['title'],
                    'video_url': f"https://www.youtube.com/watch?v={video['id']}",
                    'upload_date': video['snippet']['publishedAt'],
                    'channel_name': video['snippet']['channelTitle'],
                    'view_count': int(video['statistics'].get('viewCount', 0)),
                    'like_count': int(video['statistics'].get('likeCount', 0)),
                    'description': video['snippet']['description'],
                    'search_term': query,
                    'date_range': date_range,
                    'duration': duration  # Add duration to the results
                }
                results.append(video_data)
            except Exception as e:
                st.write(f"Error processing video {video.get('id', 'unknown')}: {str(e)}")
                st.write(f"Video data: {video.keys()}")  # Log available data
                continue

        st.write(f"Processed {len(results)} videos with detailed information")
        return results 