from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import streamlit as st
import re
from langdetect import detect, LangDetectException
from collections import Counter
import isodate

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

    def _get_video_tags(self, video_ids):
        """Get tags for a list of videos."""
        try:
            # Split video IDs into chunks of 50 (API limit)
            chunk_size = 50
            all_tags = []
            
            for i in range(0, len(video_ids), chunk_size):
                chunk = video_ids[i:i + chunk_size]
                response = self.youtube.videos().list(
                    part='snippet',
                    id=','.join(chunk)
                ).execute()
                
                # Extract tags from each video
                for item in response.get('items', []):
                    tags = item['snippet'].get('tags', [])
                    all_tags.extend(tags)
            
            # Clean and deduplicate tags
            cleaned_tags = [tag.lower().strip() for tag in all_tags if tag.strip()]
            tag_counts = Counter(cleaned_tags)
            
            # Get top 50 most common tags and sort them alphabetically
            top_tags = [tag for tag, count in tag_counts.most_common(50)]
            return sorted(top_tags)
            
        except Exception as e:
            print(f"Error fetching video tags: {str(e)}")
            return []

    def search_videos(self, query, date_filter="No date filter", english_only=True):
        """Search for YouTube videos with the given query and filters."""
        try:
            # Calculate date range
            date_range = self._get_date_filter(date_filter)
            
            # Prepare search parameters
            search_params = {
                'q': query,
                'type': 'video',
                'part': 'id,snippet',
                'maxResults': 50,
                'videoDuration': 'any',
                'relevanceLanguage': 'en' if english_only else None
            }
            
            # Add date filter if specified
            if date_range:
                search_params['publishedAfter'] = date_range.isoformat() + 'Z'
            
            # Perform search
            search_response = self.youtube.search().list(**search_params).execute()
            
            # Extract video IDs for detailed info
            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            
            # Get video tags
            video_tags = self._get_video_tags(video_ids)
            
            # Get detailed video information
            videos_response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            ).execute()
            
            # Process results
            results = []
            total_videos = len(video_ids)
            filtered_out = 0
            
            for item in videos_response.get('items', []):
                try:
                    # Extract video details
                    video_id = item['id']
                    snippet = item['snippet']
                    statistics = item.get('statistics', {})
                    content_details = item.get('contentDetails', {})
                    
                    # Check language if english_only is True
                    if english_only:
                        # Check both title and description
                        title = snippet.get('title', '')
                        description = snippet.get('description', '')
                        
                        # Skip if either title or description is not in English
                        try:
                            title_lang = detect(title)
                            desc_lang = detect(description)
                            if title_lang != 'en' or desc_lang != 'en':
                                filtered_out += 1
                                continue
                        except LangDetectException:
                            # If language detection fails for either, skip the video
                            filtered_out += 1
                            continue
                    
                    # Format duration
                    duration = content_details.get('duration', 'PT0S')
                    try:
                        duration_obj = isodate.parse_duration(duration)
                        hours = duration_obj.seconds // 3600
                        minutes = (duration_obj.seconds % 3600) // 60
                        seconds = duration_obj.seconds % 60
                        if hours > 0:
                            duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
                        else:
                            duration_str = f"{minutes}:{seconds:02d}"
                    except:
                        duration_str = "N/A"
                    
                    # Create video object
                    video = {
                        'video_id': video_id,
                        'title': title,
                        'description': description,
                        'channel_name': snippet.get('channelTitle', ''),
                        'upload_date': snippet.get('publishedAt', ''),
                        'view_count': int(statistics.get('viewCount', 0)),
                        'like_count': int(statistics.get('likeCount', 0)),
                        'duration': duration_str,
                        'video_url': f"https://www.youtube.com/watch?v={video_id}",
                        'search_term': query,
                        'date_range': date_filter,
                        'filtering_stats': {
                            'total_videos': total_videos,
                            'filtered_out': filtered_out
                        }
                    }
                    results.append(video)
                    
                except Exception as e:
                    print(f"Error processing video {video_id}: {str(e)}")
                    continue
            
            return results, video_tags
            
        except Exception as e:
            print(f"Error performing search: {str(e)}")
            return [], [] 