import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from youtube_client import YouTubeClient
from sheets_client import SheetsClient

# Load environment variables
load_dotenv()

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="YouTube Video Curation Assistant",
    page_icon="🎥",
    layout="wide"
)

# Custom CSS for text wrapping and link styling
st.markdown("""
    <style>
    div[data-testid="stDataFrame"] div[data-testid="stDataFrameCell"] {
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }
    div[data-testid="stDataFrame"] div[data-testid="stDataFrameCell"] a {
        color: #0066cc !important;
        text-decoration: none !important;
    }
    div[data-testid="stDataFrame"] div[data-testid="stDataFrameCell"] a:hover {
        text-decoration: underline !important;
    }
    /* Ensure data editor takes full width */
    div[data-testid="stDataFrame"] {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Add some spacing between rows */
    div[data-testid="stDataFrame"] div[data-testid="stDataFrameCell"] {
        padding: 8px !important;
    }
    /* Make the data editor container scrollable if needed */
    div[data-testid="stDataFrame"] > div {
        max-height: none !important;
        overflow: visible !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize clients
@st.cache_resource
def get_youtube_client():
    return YouTubeClient()

@st.cache_resource
def get_sheets_client():
    return SheetsClient()

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'selected_videos' not in st.session_state:
    st.session_state.selected_videos = set()

# Function to update search history in Google Sheets
def update_search_history(search_term):
    """Update search history with new search term"""
    try:
        sheets_client = get_sheets_client()
        sheets_client.add_search_term(search_term)
    except Exception as e:
        st.error(f"Error updating search history: {str(e)}")

# Function to get search history from Google Sheets
@st.cache_data(ttl=10)  # Cache for 10 seconds to allow for more frequent updates
def get_search_history():
    """Get search history from Google Sheets"""
    try:
        sheets_client = get_sheets_client()
        history = sheets_client.get_search_history()
        if history:
            # Convert list of dictionaries to DataFrame
            df = pd.DataFrame(history)
            
            # Rename columns to match expected format
            df = df.rename(columns={
                'Search Term': 'search_term',
                'Timestamp': 'timestamp',
                'Count': 'count'
            })
            
            # Convert timestamp string to datetime if it exists
            if 'timestamp' in df.columns and df['timestamp'].notna().any():
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            else:
                # If no timestamp, use current time
                df['timestamp'] = pd.Timestamp.now()
            
            # Ensure count is numeric
            if 'count' in df.columns:
                df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(1)
            
            return df
        return pd.DataFrame(columns=['search_term', 'count', 'timestamp'])
    except Exception as e:
        st.error(f"Error getting search history: {str(e)}")
        return pd.DataFrame(columns=['search_term', 'count', 'timestamp'])

# Sidebar with search history
with st.sidebar:
    st.header("Previous Searches")
    
    # Get search history from Google Sheets
    search_history = get_search_history()
    
    # Display search history with clickable links
    if not search_history.empty:
        for idx, row in search_history.iterrows():
            search_term = row['search_term']
            if pd.isna(search_term):  # Skip if search_term is None or NaN
                continue
                
            count = row.get('count', 1)
            if pd.isna(count):  # Handle None count
                count = 1
                
            # Create a unique key using both index and search term
            button_key = f"history_{idx}_{search_term}"
            
            if st.button(f"🔍 {search_term} ({count} searches)", key=button_key):
                try:
                    # Update search history in Google Sheets
                    update_search_history(search_term)
                    
                    # Get the current date filter and english_only settings from the UI
                    date_filter = st.session_state.get('date_filter', "No date filter")
                    english_only = st.session_state.get('english_only', True)
                    
                    # Store the search term in session state
                    st.session_state.search_input = search_term
                    
                    # Perform YouTube search with current filter settings
                    youtube_client = get_youtube_client()
                    results = youtube_client.search_videos(search_term, date_filter, english_only)
                    
                    # Convert results to DataFrame
                    st.session_state.search_results = pd.DataFrame(results)
                    st.session_state.selected_videos = set(range(len(results)))
                    
                    # Force refresh of search history
                    st.session_state.search_history = None  # Clear cached history
                    
                    # Display filtering statistics if available
                    if results and 'filtering_stats' in results[0]:
                        stats = results[0]['filtering_stats']
                        if stats['filtered_out'] > 0:
                            st.info(f"Found {stats['total_videos']} videos, filtered out {stats['filtered_out']} non-English videos.")
                    
                    # Rerun to refresh the page
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error performing search: {str(e)}")
    else:
        st.info("No previous searches yet. Start searching to build your history!")

# Main content
st.title("YouTube Video Curation Assistant")

# Search input and filters
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    search_term = st.text_input("Enter search term", key="search_input")
with col2:
    date_filter = st.selectbox(
        "Date Range",
        ["Last 7 days", "Last 2 weeks", "Last 1 month", "No date filter"],
        key="date_filter"  # Add key to store in session state
    )
with col3:
    english_only = st.checkbox("English Only", value=True, help="Filter for English language videos only", key="english_only")  # Add key to store in session state

# Search button
if st.button("Search"):
    if search_term:
        try:
            # Update search history in Google Sheets
            update_search_history(search_term)
            
            # Perform YouTube search
            youtube_client = get_youtube_client()
            results = youtube_client.search_videos(search_term, date_filter, english_only)
            
            # Convert results to DataFrame
            st.session_state.search_results = pd.DataFrame(results)
            st.session_state.selected_videos = set(range(len(results)))
            
            # Force refresh of search history
            st.session_state.search_history = None  # Clear cached history
            
            # Display filtering statistics if available
            if results and 'filtering_stats' in results[0]:
                stats = results[0]['filtering_stats']
                if stats['filtered_out'] > 0:
                    st.info(f"Found {stats['total_videos']} videos, filtered out {stats['filtered_out']} non-English videos.")
            
            # Rerun to refresh the page
            st.rerun()
            
        except Exception as e:
            st.error(f"Error performing search: {str(e)}")
    else:
        st.warning("Please enter a search term")

# Display results if available
if st.session_state.search_results is not None:
    # Get the current search term and number of rows
    current_search_term = st.session_state.get('search_input', '')
    num_rows = len(st.session_state.search_results)
    
    # Display header with search term and result count
    st.header(f"Search Results for '{current_search_term}' ({num_rows} videos found)")
    
    # Create a copy of the results for display
    display_df = st.session_state.search_results.copy()
    
    # Filter out any rows where all values are empty or NaN
    display_df = display_df.dropna(how='all')
    
    # Add selection column
    display_df['selected'] = [i in st.session_state.selected_videos for i in range(len(display_df))]
    
    # Create a clickable link column
    display_df['watch'] = display_df['video_url']
    
    # Ensure all required columns exist with default values
    required_columns = {
        'title': '',
        'watch': '',
        'duration': 'N/A',  # Default value for duration
        'upload_date': '',
        'channel_name': '',
        'view_count': 0,
        'like_count': 0,
        'description': '',
        'search_term': search_term if 'search_term' in locals() else '',
        'date_range': date_filter if 'date_filter' in locals() else ''
    }
    
    for col, default_value in required_columns.items():
        if col not in display_df.columns:
            display_df[col] = default_value
    
    # Convert numeric columns to appropriate types
    try:
        display_df['view_count'] = pd.to_numeric(display_df['view_count'], errors='coerce').fillna(0).astype(int)
        display_df['like_count'] = pd.to_numeric(display_df['like_count'], errors='coerce').fillna(0).astype(int)
    except Exception as e:
        st.warning(f"Error converting numeric columns: {str(e)}")
        display_df['view_count'] = 0
        display_df['like_count'] = 0
    
    # Display interactive dataframe
    try:
        # Calculate height based on number of rows (50px per row + 100px for header)
        num_rows = len(display_df)
        height = min(max(num_rows * 50 + 100, 200), 2000)  # Minimum 200px, maximum 2000px
        
        edited_df = st.data_editor(
            display_df,
            column_config={
                "selected": st.column_config.CheckboxColumn(
                    "Select",
                    help="Select videos to save",
                    default=True,
                    width="small"
                ),
                "title": st.column_config.Column(
                    "Title",
                    help="Video title",
                    width="large"
                ),
                "watch": st.column_config.LinkColumn(
                    "Video",
                    help="Click to watch",
                    width="small"
                ),
                "duration": st.column_config.Column(
                    "Duration",
                    help="Video length",
                    width="small"
                ),
                "upload_date": st.column_config.Column(
                    "Upload Date",
                    width="medium"
                ),
                "channel_name": st.column_config.Column(
                    "Channel",
                    width="medium"
                ),
                "view_count": st.column_config.NumberColumn(
                    "Views",
                    width="small",
                    format="%d"
                ),
                "like_count": st.column_config.NumberColumn(
                    "Likes",
                    width="small",
                    format="%d"
                ),
                "description": st.column_config.Column(
                    "Description",
                    width="large"
                ),
                "search_term": st.column_config.Column(
                    "Search Term",
                    width="medium"
                ),
                "date_range": st.column_config.Column(
                    "Date Range",
                    width="medium"
                )
            },
            hide_index=True,
            use_container_width=True,
            disabled=["title", "watch", "upload_date", "channel_name", "view_count", "like_count", "description", "search_term", "date_range", "duration"],
            column_order=[
                "selected",
                "title",
                "watch",
                "duration",
                "upload_date",
                "channel_name",
                "view_count",
                "like_count",
                "description",
                "search_term",
                "date_range"
            ],
            height=height,  # Dynamic height based on number of rows
            num_rows="fixed"  # Prevent showing empty rows
        )
        
        # Update selected videos
        if edited_df is not None:
            st.session_state.selected_videos = set(edited_df[edited_df['selected']].index)
    
    except Exception as e:
        st.error(f"Error displaying data: {str(e)}")
        st.write("Debug information:")
        st.write("Columns in DataFrame:", display_df.columns.tolist())
        st.write("Data types:", display_df.dtypes)

# Save to Google Sheets button
if st.button("Save Selected to Google Sheets"):
    if st.session_state.selected_videos:
        try:
            # Get selected videos
            selected_results = st.session_state.search_results.iloc[list(st.session_state.selected_videos)]
            
            # Convert DataFrame to list of dictionaries
            videos_to_save = selected_results.to_dict('records')
            
            # Save to Google Sheets
            sheets_client = get_sheets_client()
            num_inserted = sheets_client.insert_videos(videos_to_save)
            
            st.success(f"Successfully saved {num_inserted} videos to Google Sheets!")
            
            # Clear selection after saving
            st.session_state.selected_videos = set()
            
        except Exception as e:
            st.error("Error saving to Google Sheets:")
            st.error(str(e))
            st.error("Please make sure:")
            st.error("1. The Google Sheet exists and is accessible")
            st.error("2. The service account has been given access to the sheet")
            st.error("3. The credentials file is correct")
            st.error("4. The spreadsheet ID in .env is correct")
    else:
        st.warning("Please select at least one video to save") 