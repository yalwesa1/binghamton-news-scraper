import streamlit as st
import pandas as pd
from datetime import datetime
import asyncio
from pathlib import Path
import json
from collections import Counter
import re
from wordcloud import WordCloud
import plotly.express as px
import os
import sys
import subprocess
from dotenv import load_dotenv
import pyperclip

# Load environment variables
load_dotenv()

# Binghamton University Official Colors
BU_GREEN = "#005A43"
BU_WHITE = "#FFFFFF"

# Page configuration
st.set_page_config(
    page_title="Binghamton News Feed",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Binghamton Branding
def load_bu_theme():
    st.markdown(f"""
    <style>
        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: {BU_GREEN};
            color: white;
        }}
        [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p {{
            color: white !important;
        }}
        
        /* Main Page Headers */
        h1, h2, h3 {{
            color: {BU_GREEN} !important;
            font-family: 'Georgia', serif;
        }}
        
        /* Category Sections */
        .category-header {{
            background-color: {BU_GREEN};
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            margin-top: 30px;
            margin-bottom: 20px;
            font-size: 24px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* Story Styling */
        .story-container {{
            border-bottom: 1px solid #e0e0e0;
            padding: 20px 0;
            margin-bottom: 10px;
        }}
        .story-title {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }}
        .linkedin-content {{
            font-size: 16px;
            color: #444;
            line-height: 1.6;
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid {BU_GREEN};
            margin: 10px 0;
            white-space: pre-wrap;
        }}
        
        /* Link Buttons */
        .stLinkButton > a {{
            background-color: {BU_GREEN} !important;
            color: white !important;
            border-radius: 5px !important;
            border: none !important;
        }}
        
        /* Sidebar Buttons - Primary Type */
        [data-testid="stSidebar"] button[kind="primary"] {{
            background-color: {BU_GREEN} !important;
            color: white !important;
            font-weight: bold !important;
            border: 2px solid white !important;
            border-radius: 5px !important;
        }}
        
        [data-testid="stSidebar"] button[kind="primary"]:hover {{
            background-color: #003d2e !important;
            border: 2px solid white !important;
        }}
        
        /* Copy Button Styling - Match Link Button */
        button[kind="primary"] {{
            background-color: {BU_GREEN} !important;
            color: white !important;
            border: none !important;
            border-radius: 5px !important;
        }}
        
        button[kind="primary"]:hover {{
            background-color: #003d2e !important;
        }}
        
        /* Dark Mode Adjustments */
        @media (prefers-color-scheme: dark) {{
            .linkedin-content {{
                background-color: #1e1e1e;
                color: #ddd;
            }}
            .story-title {{
                color: #eee;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)

load_bu_theme()

# Initialize session state
if 'stories' not in st.session_state:
    st.session_state.stories = []
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = None
if 'history' not in st.session_state:
    st.session_state.history = []

# Helper functions
def load_existing_stories():
    csv_path = Path("binghamton_news_stories.csv")
    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            return df.to_dict('records')
        except Exception as e:
            return []
    return []

def run_scraper_subprocess():
    """
    Run the scraper as a subprocess - avoids event loop conflicts on Windows.
    The scraper runs in its own Python process with a clean event loop.
    """
    # Get the path to the main.py file
    script_dir = Path(__file__).parent
    main_py = script_dir / "main.py"
    
    # Run main.py as a subprocess
    # Use the same Python interpreter that's running Streamlit
    python_exe = sys.executable
    env = os.environ.copy()
    
    # Set UTF-8 encoding for Windows console
    env['PYTHONIOENCODING'] = 'utf-8'
    
    try:
        result = subprocess.run(
            [python_exe, str(main_py)],
            cwd=str(script_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Scraper failed with return code {result.returncode}\n{result.stderr}")
        
        # After scraper completes, reload the CSV file
        return load_existing_stories()
    
    except subprocess.TimeoutExpired:
        raise TimeoutError("Scraper timed out after 10 minutes")
    except Exception as e:
        raise RuntimeError(f"Error running scraper: {str(e)}")

def extract_keywords(stories, top_n=20):
    text = " ".join([s.get('story_summary', '') + " " + s.get('story_title', '') for s in stories])
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'that', 'this', 'these', 'those', 'with', 'from', 'as', 'by'}
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    filtered_words = [w for w in words if w not in stop_words]
    return Counter(filtered_words).most_common(top_n)

# Load existing data
if not st.session_state.stories:
    st.session_state.stories = load_existing_stories()
    if st.session_state.stories:
        st.session_state.last_updated = datetime.now()

# Sidebar (Full BU Green)
with st.sidebar:
    st.markdown(f"""
        <h1 style='color: white; font-size: 20px; text-align: center; margin-bottom: 20px;'>
            Binghamton University<br>News AI Scraper
        </h1>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # User-controlled refresh - runs scraper as subprocess to avoid event loop conflicts
    if st.button("🔄 REFRESH SCRAPER", key="refresh_btn", type="primary"):
        with st.spinner("Connecting to BU News... This may take a minute."):
            try:
                # Run scraper as a subprocess - creates fresh Python process with clean event loop
                stories = run_scraper_subprocess()
                
                if stories:
                    st.session_state.stories = stories
                    st.session_state.last_updated = datetime.now()
                    st.session_state.history.append({'timestamp': datetime.now(), 'count': len(stories)})
                    st.success(f"✅ Successfully scraped {len(stories)} stories!")
                    st.rerun()
                else:
                    st.warning("⚠️ No stories were found. Please check your connection or try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)  # Show full traceback for debugging
    
    st.markdown("---")
    st.markdown("<h3 style='color: white; font-size: 18px;'>📊 Current Scrape Stats</h3>", unsafe_allow_html=True)
    if st.session_state.stories:
        st.markdown(f"<p style='color: white;'>Total Stories: <strong>{len(st.session_state.stories)}</strong></p>", unsafe_allow_html=True)
        if st.session_state.last_updated:
            st.markdown(f"<p style='color: white;'>Updated: {st.session_state.last_updated.strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    # Simple Export with dark green styling
    if st.session_state.stories:
        csv = pd.DataFrame(st.session_state.stories).to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download CSV Report", 
            data=csv, 
            file_name="bu_news_report.csv",
            key="download_csv",
            type="primary"
        )

# Main Content Area - Header with Logo and Title
col_logo, col_title = st.columns([1, 2])
with col_logo:
    # Use the Binghamton logo here. Path should be relative to the root.
    # If the user saved the logo image as 'logo.png' in the root:
    if Path("logo.png").exists():
        st.image("logo.png", width=300)
    else:
        # Fallback to text header if logo not found
        st.markdown(f"<h1 style='color: {BU_GREEN}; margin-top: 0;'>BINGHAMTON</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: {BU_GREEN}; font-weight: bold;'>STATE UNIVERSITY OF NEW YORK</p>", unsafe_allow_html=True)

with col_title:
    # Main title
    st.markdown(f"""
        <div style='margin-top: 40px;'>
            <h1 style='color: {BU_GREEN}; font-size: 32px; font-weight: bold; margin-bottom: 10px;'>
                Smarter AI Scraper: Binghamton University News
            </h1>
            <p style='color: #666; font-size: 16px; margin-top: 5px;'>
                Developed by Yaseen Alwesabi
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

if not st.session_state.stories:
    st.info("No data available. Please click 'REFRESH SCRAPER' in the sidebar to begin.")
else:
    tab1, tab2, tab3 = st.tabs(["📰 NEWS FEED", "📊 CATEGORY ANALYTICS", "💡 TEXT INSIGHTS"])
    
    with tab1:
        # Step 1: Group and Sort - ensure all categories are strings
        grouped_data = {}
        for s in st.session_state.stories:
            cat = str(s.get('story_category', 'General'))
            if cat not in grouped_data:
                grouped_data[cat] = []
            grouped_data[cat].append(s)
        
        # Sort Categories Alphabetically
        sorted_categories = sorted(grouped_data.keys())
        
        # Step 2: Display categorized feed
        for category in sorted_categories:
            st.markdown(f'<div class="category-header">{category}</div>', unsafe_allow_html=True)
            
            # Sort stories in category alphabetically by title
            category_stories = sorted(grouped_data[category], key=lambda x: x.get('story_title', '').lower())
            
            for idx, story in enumerate(category_stories):
                with st.container():
                    st.markdown(f'<div class="story-title">{story.get("story_title", "Untitled Story")}</div>', unsafe_allow_html=True)
                    
                    # Clean LinkedIn post display
                    post_content = story.get('story_LinkedIn_post', '')
                    st.markdown(f'<div class="linkedin-content">{post_content}</div>', unsafe_allow_html=True)
                    
                    # Buttons: Read More Link + Copy Button
                    if story.get('story_url'):
                        col1, col2, col3 = st.columns([3, 1, 6])
                        with col1:
                            st.link_button("🔗 Read Details on Binghamton News Site", story['story_url'])
                        with col2:
                            if st.button("📋", key=f"copy_{category}_{idx}", help="Copy LinkedIn post", type="primary"):
                                try:
                                    # Use Streamlit's session state to trigger copy
                                    st.session_state[f'copied_{category}_{idx}'] = True
                                    # Show success message
                                    st.toast("✅ LinkedIn post copied to clipboard!", icon="✅")
                                    # Copy to clipboard (note: this works in local environment)
                                    pyperclip.copy(post_content)
                                except:
                                    # Fallback: show the content in a text area for manual copy
                                    st.info("Copy the text below:")
                                    st.code(post_content, language=None)
                    
                    st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)

    with tab2:
        st.subheader("Binghamton News Distribution")
        # Ensure all categories are strings for counting
        category_counts = Counter([str(s.get('story_category', 'Unknown')) for s in st.session_state.stories])
        
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(values=list(category_counts.values()), names=list(category_counts.keys()), 
                            color_discrete_sequence=[BU_GREEN, "#00A3AD", "#85714D", "#000000"],
                            title="Stories by Category")
            st.plotly_chart(fig_pie, width='stretch')
        with col2:
            fig_bar = px.bar(x=list(category_counts.keys()), y=list(category_counts.values()),
                            labels={'x': 'Category', 'y': 'Count'},
                            color_discrete_sequence=[BU_GREEN],
                            title="Story Volume by Category")
            st.plotly_chart(fig_bar, width='stretch')

    with tab3:
        st.subheader("Text Insights & Trending Topics")
        keywords = extract_keywords(st.session_state.stories, top_n=100)
        
        if keywords:
            wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='Greens').generate_from_frequencies(dict(keywords))
            st.image(wordcloud.to_array(), width='stretch')
            
            st.markdown("### Top Keywords Found")
            cols = st.columns(5)
            for i, (kw, count) in enumerate(extract_keywords(st.session_state.stories, top_n=15)):
                cols[i % 5].metric(kw, count)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: gray; padding: 20px;'>
    University News Dashboard | Powered by Llama 3.3 AI<br>
    <span style='color: {BU_GREEN}; font-weight: bold;'>Binghamton University</span> News Scraper
</div>
""", unsafe_allow_html=True)
