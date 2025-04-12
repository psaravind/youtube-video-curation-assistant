import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from youtube_client import YouTubeClient
from search_history import SearchHistoryManager

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

# Initialize YouTube client
def get_youtube_client():
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        st.error("YouTube API key not found. Please set YOUTUBE_API_KEY in your .env file.")
        return None
    return YouTubeClient()

# Initialize search history manager
search_history_manager = SearchHistoryManager()

# Function to update search history
def update_search_history(search_term):
    """Update the search history with a new search term."""
    search_history_manager.add_search_term(search_term)

# Function to get search history
@st.cache_data(ttl=10)  # Cache for 10 seconds
def get_search_history():
    """Get the search history as a DataFrame."""
    return search_history_manager.get_search_history()

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'selected_videos' not in st.session_state:
    st.session_state.selected_videos = set()
if 'video_tags' not in st.session_state:
    st.session_state.video_tags = []
if 'tag_to_search' not in st.session_state:
    st.session_state.tag_to_search = None

# Main content
st.title("YouTube Video Curation Assistant")

# Check if we need to perform a search from a tag click
if st.session_state.tag_to_search:
    search_term = st.session_state.tag_to_search
    # Store the current search term in session state
    st.session_state.current_search_term = search_term
    # Update search history when a tag is clicked
    update_search_history(search_term)
    st.session_state.tag_to_search = None  # Reset after using
else:
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
if st.button("Search", key="search_button"):
    if search_term:
        try:
            # Store the current search term in session state
            st.session_state.current_search_term = search_term
            
            # Update search history in local file
            update_search_history(search_term)
            
            # Get the current date filter and english_only settings from the UI
            date_filter = st.session_state.get('date_filter', "No date filter")
            english_only = st.session_state.get('english_only', True)
            
            # Perform YouTube search with current filter settings
            youtube_client = get_youtube_client()
            results, video_tags = youtube_client.search_videos(search_term, date_filter, english_only)
            
            # Convert results to DataFrame
            st.session_state.search_results = pd.DataFrame(results)
            st.session_state.selected_videos = set(range(len(results)))
            
            # Store video tags in session state
            st.session_state.video_tags = video_tags
            
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

# Display suggested topics if available
if 'video_tags' in st.session_state and st.session_state.video_tags:
    st.markdown("### Suggested Topics")
    
    # Create a container for the tags
    tag_container = st.container()
    
    # Display tags in a more compact form with 5 columns
    with tag_container:
        # Calculate how many rows we need (5 tags per row)
        tags = st.session_state.video_tags
        num_rows = (len(tags) + 4) // 5  # Round up division
        
        for row in range(num_rows):
            # Get the tags for this row
            start_idx = row * 5
            end_idx = min(start_idx + 5, len(tags))
            row_tags = tags[start_idx:end_idx]
            
            # Create columns for this row
            cols = st.columns(5)
            
            # Add tags to columns
            for i, tag in enumerate(row_tags):
                if cols[i].button(f"🔍 {tag}", key=f"tag_{tag}"):
                    # Instead of modifying search_input directly, set a flag
                    st.session_state.tag_to_search = tag
                    # Force refresh of search history
                    st.session_state.search_history = None  # Clear cached history
                    st.rerun()

# Display results if available
if st.session_state.search_results is not None:
    # Get the current search term and number of rows
    current_search_term = st.session_state.get('current_search_term', '')  # Get from session state
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

# Sidebar for previous searches
with st.sidebar:
    st.header("Previous Searches")
    
    # Get search history
    search_history = get_search_history()
    
    if not search_history.empty:
        # Display search history with clickable links
        for _, row in search_history.iterrows():
            search_term = row['search_term']
            count = row['count']
            button_key = f"history_{search_term}"
            
            # Create two columns for each search term
            cols = st.columns(2)
            if cols[0].button(f"🔍 {search_term} ({count} searches)", key=button_key):
                try:
                    # Store the current search term in session state
                    st.session_state.current_search_term = search_term
                    
                    # Update search history in local file
                    update_search_history(search_term)
                    
                    # Get the current date filter and english_only settings from the UI
                    date_filter = st.session_state.get('date_filter', "No date filter")
                    english_only = st.session_state.get('english_only', True)
                    
                    # Perform YouTube search with current filter settings
                    youtube_client = get_youtube_client()
                    results, video_tags = youtube_client.search_videos(search_term, date_filter, english_only)
                    
                    # Convert results to DataFrame
                    st.session_state.search_results = pd.DataFrame(results)
                    st.session_state.selected_videos = set(range(len(results)))
                    
                    # Store video tags in session state
                    st.session_state.video_tags = video_tags
                    
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
        st.info("No search history yet. Start searching to build your history!") 