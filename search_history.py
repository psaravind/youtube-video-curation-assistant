import os
import csv
import pandas as pd
from datetime import datetime

class SearchHistoryManager:
    """Manages search history using a local CSV file."""
    
    def __init__(self, file_path="data/search_history.csv"):
        """Initialize the search history manager.
        
        Args:
            file_path (str): Path to the CSV file for storing search history
        """
        self.file_path = file_path
        self._ensure_data_directory()
        self._ensure_file_exists()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
    
    def _ensure_file_exists(self):
        """Ensure the search history file exists with proper headers."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['search_term', 'timestamp', 'count'])
    
    def add_search_term(self, search_term):
        """Add a search term to the history.
        
        Args:
            search_term (str): The search term to add
        """
        # Read existing data
        df = self.get_search_history()
        
        # Check if search term already exists
        if search_term in df['search_term'].values:
            # Update count for existing term
            df.loc[df['search_term'] == search_term, 'count'] += 1
            df.loc[df['search_term'] == search_term, 'timestamp'] = datetime.now().isoformat()
        else:
            # Add new search term
            new_row = pd.DataFrame({
                'search_term': [search_term],
                'timestamp': [datetime.now().isoformat()],
                'count': [1]
            })
            df = pd.concat([df, new_row], ignore_index=True)
        
        # Save updated data
        df.to_csv(self.file_path, index=False)
    
    def get_search_history(self):
        """Get the search history as a DataFrame.
        
        Returns:
            pandas.DataFrame: DataFrame with search history
        """
        try:
            df = pd.read_csv(self.file_path)
            # Convert timestamp to datetime using ISO format
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
            # Sort by timestamp (newest first)
            df = df.sort_values('timestamp', ascending=False)
            return df
        except Exception as e:
            print(f"Error reading search history: {str(e)}")
            # Return empty DataFrame with correct columns
            return pd.DataFrame(columns=['search_term', 'timestamp', 'count'])
    
    def clear_history(self):
        """Clear the search history."""
        self._ensure_file_exists()  # This will reset the file with just headers 