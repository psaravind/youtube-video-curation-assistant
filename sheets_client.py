import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv
from datetime import datetime
import traceback

# Load environment variables
load_dotenv()

class SheetsClient:
    def __init__(self):
        """Initialize Google Sheets client"""
        try:
            # Get credentials from service account file
            creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', 'creds/youtube-video-curation-456516-76975cfec573.json')
            
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"Google Sheets credentials not found at {creds_path}")
            
            # Set up credentials
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/spreadsheets'
            ]
            credentials = Credentials.from_service_account_file(creds_path, scopes=scope)
            
            # Initialize client
            self.client = gspread.authorize(credentials)
            
            # Get spreadsheet ID from environment
            self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
            
            if not self.spreadsheet_id:
                raise ValueError("Google Sheets ID not found in environment variables")
            
            # Get or create worksheet
            self.sheet = self._get_or_create_worksheet()
            
            # Get or create search history worksheet
            self.search_history_sheet = self._get_or_create_search_history_worksheet()
            
        except Exception as e:
            error_msg = f"Error initializing Google Sheets client: {str(e)}\n"
            error_msg += f"Credentials path: {creds_path}\n"
            error_msg += f"Spreadsheet ID: {self.spreadsheet_id}\n"
            error_msg += f"Traceback: {traceback.format_exc()}"
            raise Exception(error_msg)

    def _get_or_create_worksheet(self):
        """Get or create the worksheet for video data"""
        try:
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            worksheet = spreadsheet.worksheet('YouTube Videos')
            return worksheet
        except gspread.exceptions.WorksheetNotFound:
            # Create new worksheet if it doesn't exist
            worksheet = spreadsheet.add_worksheet('YouTube Videos', 1000, 20)
            # Add headers
            headers = [
                'Title', 'Video URL', 'Upload Date', 'Channel Name',
                'View Count', 'Like Count', 'Description',
                'Search Term', 'Date Range', 'Added Date'
            ]
            worksheet.append_row(headers)
            return worksheet
        except Exception as e:
            error_msg = f"Error accessing worksheet: {str(e)}\n"
            error_msg += f"Spreadsheet ID: {self.spreadsheet_id}\n"
            error_msg += f"Traceback: {traceback.format_exc()}"
            raise Exception(error_msg)
            
    def _get_or_create_search_history_worksheet(self):
        """Get or create the worksheet for search history"""
        try:
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            worksheet = spreadsheet.worksheet('Search_History')
            return worksheet
        except gspread.exceptions.WorksheetNotFound:
            # Create new worksheet if it doesn't exist
            worksheet = spreadsheet.add_worksheet('Search_History', 1000, 3)
            # Add headers
            headers = ['Search Term', 'Timestamp', 'Count']
            worksheet.append_row(headers)
            return worksheet
        except Exception as e:
            error_msg = f"Error accessing search history worksheet: {str(e)}\n"
            error_msg += f"Spreadsheet ID: {self.spreadsheet_id}\n"
            error_msg += f"Traceback: {traceback.format_exc()}"
            raise Exception(error_msg)
            
    def add_search_term(self, search_term):
        """
        Add a search term to the search history
        
        Args:
            search_term (str): The search term to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current timestamp
            timestamp = datetime.now().isoformat()
            
            # Check if search term already exists
            try:
                cell = self.search_history_sheet.find(search_term)
                
                # If cell is None, the search term wasn't found
                if cell is None:
                    # Add new search term if it doesn't exist
                    self.search_history_sheet.append_row([search_term, timestamp, 1])
                else:
                    # Update count if search term exists
                    count_cell = self.search_history_sheet.cell(cell.row, 3)
                    count = int(count_cell.value) + 1
                    self.search_history_sheet.update_cell(cell.row, 3, count)
                    # Update timestamp
                    self.search_history_sheet.update_cell(cell.row, 2, timestamp)
            except Exception as e:
                # If there's any error finding the cell, just add a new row
                self.search_history_sheet.append_row([search_term, timestamp, 1])
                
            return True
        except Exception as e:
            error_msg = f"Error adding search term: {str(e)}\n"
            error_msg += f"Search term: {search_term}\n"
            error_msg += f"Traceback: {traceback.format_exc()}"
            raise Exception(error_msg)
            
    def get_search_history(self):
        """
        Get search history from Google Sheets
        
        Returns:
            list: List of dictionaries containing search history data
        """
        try:
            # Get all values from the search history worksheet
            values = self.search_history_sheet.get_all_records()
            
            # Sort by timestamp (newest first)
            sorted_values = sorted(values, key=lambda x: x['Timestamp'], reverse=True)
            
            # Return the full search history data
            return sorted_values
        except Exception as e:
            error_msg = f"Error getting search history: {str(e)}\n"
            error_msg += f"Traceback: {traceback.format_exc()}"
            raise Exception(error_msg)

    def insert_videos(self, videos):
        """
        Insert video data into Google Sheets
        
        Args:
            videos (list): List of video metadata dictionaries
            
        Returns:
            int: Number of rows inserted
        """
        if not videos:
            return 0
            
        try:
            # Prepare data for insertion
            rows = []
            for video in videos:
                row = [
                    video.get('title', ''),
                    video.get('video_url', ''),
                    video.get('upload_date', ''),
                    video.get('channel_name', ''),
                    video.get('view_count', 0),
                    video.get('like_count', 0),
                    video.get('description', ''),
                    video.get('search_term', ''),
                    video.get('date_range', ''),
                    datetime.now().isoformat()
                ]
                rows.append(row)
            
            # Insert data
            self.sheet.append_rows(rows)
            return len(rows)
            
        except Exception as e:
            error_msg = f"Error inserting videos: {str(e)}\n"
            error_msg += f"Number of videos: {len(videos)}\n"
            error_msg += f"First video data: {videos[0] if videos else 'No videos'}\n"
            error_msg += f"Traceback: {traceback.format_exc()}"
            raise Exception(error_msg) 