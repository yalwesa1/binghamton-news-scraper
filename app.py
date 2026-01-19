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
import plotly.graph_objects as go
import pyperclip
import os
from dotenv import load_dotenv

# Import our scraper
from main import run_scraper

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Binghamton News Dashboard",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'stories' not in st.session_state:
    st.session_state.stories = []
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = None
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'history' not in st.session_state:
    st.session_state.history = []

# Custom CSS for styling
def load_css():
    mode_colors = {
        'bg': '#0E1117' if st.session_state.dark_mode else '#FFFFFF',
        'card_bg': '#262730' if st.session_state.dark_mode else '#F0F2F6',
        'text': '#FAFAFA' if st.session_state.dark_mode else '#262730',
        'border': '#4A4A4A' if st.session_state.dark_mode else '#E0E0E0'
    }
    
    st.markdown(f"""
    <style>
        .story-card {{
            background-color: {mode_colors['card_bg']};
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            height: 100%;
            border: 1px solid {mode_colors['border']};
        }}
        .story-title {{
            font-size: 18px;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 10px;
        }}
        .story-category {{
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            margin-bottom: 10px;
        }}
        .linkedin-post {{
            font-size: 14px;
            color: {mode_colors['text']};
            line-height: 1.6;
            margin-top: 10px;
            padding: 15px;
            background-color: {mode_colors['bg']};
            border-left: 3px solid #0077B5;
            border-radius: 5px;
        }}
        .analytics-box {{
            background-color: {mode_colors['card_bg']};
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border: 1px solid {mode_colors['border']};
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #1f77b4;
        }}
        .copy-notification {{
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            text-align: center;
        }}
    </style>
    """, unsafe_allow_html=True)

load_css()

# Helper functions
def load_existing_stories():
    """Load stories from CSV if available"""
    csv_path = Path("binghamton_news_stories.csv")
    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            return df.to_dict('records')
        except Exception as e:
            st.error(f"Error loading stories: {e}")
            return []
    return []

def extract_keywords(stories, top_n=20):
    """Extract most common keywords from stories"""
    # Combine all summaries and titles
    text = " ".join([s.get('story_summary', '') + " " + s.get('story_title', '') for s in stories])
    
    # Remove common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'that', 'this', 'these', 'those', 'with', 'from', 'as', 'by'}
    
    # Extract words
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    filtered_words = [w for w in words if w not in stop_words]
    
    # Count frequencies
    word_counts = Counter(filtered_words)
    return word_counts.most_common(top_n)

def calculate_text_stats(stories):
    """Calculate text statistics"""
    if not stories:
        return {}
    
    summaries = [len(s.get('story_summary', '')) for s in stories]
    posts = [len(s.get('story_LinkedIn_post', '')) for s in stories]
    
    return {
        'avg_summary_length': sum(summaries) / len(summaries) if summaries else 0,
        'avg_post_length': sum(posts) / len(posts) if posts else 0,
        'total_stories': len(stories)
    }

def improve_linkedin_post(original_post, story_title, category):
    """Use LLM to improve LinkedIn post for better engagement"""
    try:
        from litellm import completion
        
        prompt = f"""You are a social media expert specializing in LinkedIn content for universities.

Review this LinkedIn post and make it MORE ENGAGING, STUDENT-FRIENDLY, and ATTRACTIVE.

Story Title: {story_title}
Category: {category}
Original Post:
{original_post}

Guidelines:
1. Keep it 100-150 words
2. Make it relatable to students and young professionals
3. Use engaging language (questions, calls-to-action)
4. Add 2-3 relevant emojis naturally
5. Keep all hashtags
6. Keep the "Read more:" link at the end
7. Make it exciting and shareable!

Return ONLY the improved post, nothing else."""

        response = completion(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        improved_post = response.choices[0].message.content.strip()
        return improved_post
        
    except Exception as e:
        st.error(f"Error improving post: {e}")
        return original_post

# Load existing stories on first run
if not st.session_state.stories:
    st.session_state.stories = load_existing_stories()
    if st.session_state.stories:
        st.session_state.last_updated = datetime.now()

# Sidebar
with st.sidebar:
    st.title("📰 Binghamton News")
    
    # Dark mode toggle
    dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        load_css()
        st.rerun()
    
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh Stories", use_container_width=True, type="primary"):
        st.session_state.is_loading = True
        with st.spinner("Scraping latest news..."):
            try:
                stories = run_scraper()
                if stories:
                    st.session_state.stories = stories
                    st.session_state.last_updated = datetime.now()
                    
                    # Save to history
                    st.session_state.history.append({
                        'timestamp': datetime.now(),
                        'count': len(stories),
                        'categories': [s.get('story_category', 'Unknown') for s in stories]
                    })
                    
                    st.success(f"✅ Loaded {len(stories)} stories!")
                else:
                    st.warning("No stories found")
            except Exception as e:
                st.error(f"❌ Error: {e}")
            finally:
                st.session_state.is_loading = False
                st.rerun()
    
    # Stats
    st.markdown("---")
    st.subheader("📊 Statistics")
    
    if st.session_state.stories:
        num_stories = len(st.session_state.stories)
        categories = list(set(story.get('story_category', 'Unknown') for story in st.session_state.stories))
        
        st.metric("Total Stories", num_stories)
        st.metric("Categories", len(categories))
        
        if st.session_state.last_updated:
            time_diff = datetime.now() - st.session_state.last_updated
            mins_ago = int(time_diff.total_seconds() / 60)
            time_str = f"{mins_ago} mins ago" if mins_ago < 60 else f"{int(mins_ago/60)} hrs ago"
            st.metric("Last Updated", time_str)
    
    # Export options
    st.markdown("---")
    st.subheader("⬇️ Export")
    
    if st.session_state.stories:
        # Export as CSV
        df = pd.DataFrame(st.session_state.stories)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"binghamton_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Export as JSON
        json_str = json.dumps(st.session_state.stories, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"binghamton_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# Main content area
st.title("📰 Binghamton University News Dashboard")
st.markdown("---")

# Display stories or prompt
if not st.session_state.stories:
    st.info("👋 Click 'Refresh Stories' in the sidebar to load the latest news!")
else:
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📰 Stories", "📊 Analytics", "💡 Text Insights"])
    
    with tab1:
        # Category filter
        all_categories = ['All'] + sorted(set(story.get('story_category', 'Unknown') for story in st.session_state.stories))
        selected_category = st.selectbox("Filter by category:", all_categories)
        
        # Filter stories
        filtered_stories = st.session_state.stories
        if selected_category != 'All':
            filtered_stories = [s for s in st.session_state.stories if s.get('story_category') == selected_category]
        
        st.markdown(f"### Showing {len(filtered_stories)} stories")
        
        # Display stories in cards
        card_columns = st.selectbox("Cards per row:", [1, 2, 3], index=1)
        
        # Create grid layout
        rows = (len(filtered_stories) + card_columns - 1) // card_columns
        
        for row_idx in range(rows):
            cols = st.columns(card_columns)
            for col_idx in range(card_columns):
                story_idx = row_idx * card_columns + col_idx
                if story_idx < len(filtered_stories):
                    story = filtered_stories[story_idx]
                    
                    with cols[col_idx]:
                        # Story card
                        with st.container():
                            st.markdown(f"""
                            <div class="story-card">
                                <div class="story-title">{story.get('story_title', 'No Title')}</div>
                                <span class="story-category">{story.get('story_category', 'Uncategorized')}</span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Summary
                            with st.expander("📄 Summary", expanded=False):
                                st.markdown(f"**{story.get('story_summary', 'No summary available')}**")
                            
                            # LinkedIn post
                            st.markdown("**📱 LinkedIn Post:**")
                            linkedin_post = story.get('story_LinkedIn_post', 'No post available')
                            st.markdown(f"""
                            <div class="linkedin-post">
                                {linkedin_post}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Action buttons
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if st.button("📋 Copy", key=f"copy_{story_idx}", use_container_width=True):
                                    try:
                                        # Try using pyperclip
                                        pyperclip.copy(linkedin_post)
                                        st.success("✅ Copied!")
                                    except:
                                        # Fallback: show text area
                                        st.text_area("Copy this:", linkedin_post, height=100, key=f"fallback_{story_idx}")
                            
                            with col2:
                                if story.get('story_url'):
                                    st.link_button("🔗 Read More", story['story_url'], use_container_width=True)
                            
                            with col3:
                                if st.button("✨ Improve", key=f"improve_{story_idx}", use_container_width=True):
                                    with st.spinner("AI improving post..."):
                                        improved = improve_linkedin_post(
                                            linkedin_post,
                                            story.get('story_title', ''),
                                            story.get('story_category', '')
                                        )
                                        st.session_state[f"improved_{story_idx}"] = improved
                            
                            # Show improved version if available
                            if f"improved_{story_idx}" in st.session_state:
                                st.markdown("**✨ AI-Improved Version:**")
                                st.info(st.session_state[f"improved_{story_idx}"])
                                if st.button("📋 Copy Improved", key=f"copy_improved_{story_idx}"):
                                    try:
                                        pyperclip.copy(st.session_state[f"improved_{story_idx}"])
                                        st.success("✅ Copied improved version!")
                                    except:
                                        st.text_area("Copy this:", st.session_state[f"improved_{story_idx}"], height=100)
    
    with tab2:
        st.subheader("📊 Analytics Dashboard")
        
        # Story count over time (if we have history)
        if len(st.session_state.history) > 1:
            st.markdown("### 📈 Story Count Over Time")
            history_df = pd.DataFrame([
                {'Time': h['timestamp'].strftime('%H:%M'), 'Stories': h['count']}
                for h in st.session_state.history
            ])
            fig_line = px.line(history_df, x='Time', y='Stories', 
                              title='Stories Scraped Over Time',
                              markers=True)
            fig_line.update_layout(height=400)
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("📈 Story trends will appear after multiple scrapes")
        
        # Category distribution
        st.markdown("### 🎯 Category Distribution")
        category_counts = Counter([s.get('story_category', 'Unknown') for s in st.session_state.stories])
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Pie chart
            fig_pie = px.pie(
                values=list(category_counts.values()),
                names=list(category_counts.keys()),
                title='Stories by Category'
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Bar chart
            fig_bar = px.bar(
                x=list(category_counts.keys()),
                y=list(category_counts.values()),
                title='Story Count by Category',
                labels={'x': 'Category', 'y': 'Count'}
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab3:
        st.subheader("💡 Text Insights")
        
        # Text statistics
        stats = calculate_text_stats(st.session_state.stories)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="analytics-box">
                <div>Average Summary Length</div>
                <div class="metric-value">{stats.get('avg_summary_length', 0):.0f}</div>
                <div>characters</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="analytics-box">
                <div>Average Post Length</div>
                <div class="metric-value">{stats.get('avg_post_length', 0):.0f}</div>
                <div>characters</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="analytics-box">
                <div>Total Stories</div>
                <div class="metric-value">{stats.get('total_stories', 0)}</div>
                <div>analyzed</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Keywords and word cloud
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 🔑 Top Keywords")
            keywords = extract_keywords(st.session_state.stories, top_n=15)
            
            if keywords:
                # Display as table
                keywords_df = pd.DataFrame(keywords, columns=['Keyword', 'Frequency'])
                st.dataframe(keywords_df, use_container_width=True, height=400)
        
        with col2:
            st.markdown("### ☁️ Word Cloud")
            keywords = extract_keywords(st.session_state.stories, top_n=100)
            
            if keywords:
                # Generate word cloud
                wordcloud = WordCloud(
                    width=800, 
                    height=400,
                    background_color='white' if not st.session_state.dark_mode else 'black',
                    colormap='viridis'
                ).generate_from_frequencies(dict(keywords))
                
                st.image(wordcloud.to_array(), use_column_width=True)
        
        # Trending topics
        st.markdown("---")
        st.markdown("### 📌 Trending Topics This Month")
        
        # Get top keywords as trending topics
        top_keywords = extract_keywords(st.session_state.stories, top_n=8)
        if top_keywords:
            # Display as pills/badges
            topics_html = " ".join([
                f'<span style="background-color: #1f77b4; color: white; padding: 8px 15px; border-radius: 20px; margin: 5px; display: inline-block;">{kw[0]} ({kw[1]})</span>'
                for kw in top_keywords
            ])
            st.markdown(topics_html, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    Built with ❤️ for Binghamton University<br>
    Powered by AI (Llama 3.3 70B) | <a href='https://github.com/yalwesa1/binghamton-news-scraper'>GitHub</a>
</div>
""", unsafe_allow_html=True)
