# App Adjustment & Extension Guide

> **Senior Engineering Perspective**: This guide ensures systematic, maintainable changes across the entire application stack. Follow this framework whenever adding features, modifying data models, or changing application behavior.

---

## 📋 Table of Contents

1. [Change Impact Framework](#change-impact-framework)
2. [Systematic Update Checklist](#systematic-update-checklist)
3. [Feature 1: Add Story URL to LinkedIn Posts](#feature-1-add-story-url-to-linkedin-posts)
4. [Feature 2: Streamlit Dashboard](#feature-2-streamlit-dashboard)
5. [Testing & Validation](#testing--validation)
6. [Documentation Updates](#documentation-updates)

---

## Change Impact Framework

### Understanding the Application Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                          │
│                   (Streamlit Dashboard)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                              │
│                     (main.py)                                │
└────────┬───────────────────────────────┬────────────────────┘
         │                               │
         ▼                               ▼
┌────────────────────┐          ┌────────────────────┐
│   CONFIGURATION    │          │   DATA MODEL       │
│    (config.py)     │          │ (models/venue.py)  │
└────────────────────┘          └────────────────────┘
         │                               │
         ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC                            │
│              (utils/scraper_utils.py)                        │
│              (utils/data_utils.py)                           │
└────────┬───────────────────────────────┬────────────────────┘
         │                               │
         ▼                               ▼
┌────────────────────┐          ┌────────────────────┐
│   EXTERNAL APIs    │          │   DATA STORAGE     │
│  - Crawl4AI        │          │  - CSV Files       │
│  - Groq LLM        │          │  - Database (TBD)  │
└────────────────────┘          └────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    DOCUMENTATION                             │
│  README.MD | SET_UP.md | road_map.md | flow_charts.md       │
└─────────────────────────────────────────────────────────────┘
```

---

## Systematic Update Checklist

### 🔄 For ANY Change to the Application

When making **any** change, follow this checklist:

#### Phase 1: Planning
- [ ] **Identify Impact Scope**: Which layers are affected?
- [ ] **Review Dependencies**: What files import/use the changed component?
- [ ] **Assess Data Flow**: How does data move through the change?
- [ ] **Check LLM Integration**: Does this affect prompts or extraction logic?

#### Phase 2: Implementation
- [ ] **Update Data Model** (`models/venue.py`) - if data structure changes
- [ ] **Update Configuration** (`config.py`) - if new settings needed
- [ ] **Update Business Logic** (`utils/*.py`) - if processing changes
- [ ] **Update Orchestrator** (`main.py`) - if workflow changes
- [ ] **Update LLM Prompts** (`utils/scraper_utils.py`) - if extraction changes

#### Phase 3: Documentation
- [ ] **Update README.MD** - if user-facing features change
- [ ] **Update SET_UP.md** - if setup process changes
- [ ] **Update road_map.md** - if architecture changes
- [ ] **Update flow charts** - if data flow changes
- [ ] **Update this file** - document the extension pattern

#### Phase 4: Validation
- [ ] **Test Data Model** - ensure Pydantic validation works
- [ ] **Test LLM Extraction** - verify LLM returns expected format
- [ ] **Test CSV Output** - check file structure and content
- [ ] **Test End-to-End** - run full scraper workflow
- [ ] **Check Git Status** - review all changed files

---

## Feature 1: Add Story URL to LinkedIn Posts

### 🎯 Objective
Add the story URL to each LinkedIn post so users can click to read the full article.

### Impact Analysis

| Component | Change Required | File(s) | Complexity |
|-----------|----------------|---------|------------|
| Data Model | ✅ Add `story_url` field | `models/venue.py` | Low |
| Configuration | ✅ Update required keys | `config.py` | Low |
| LLM Prompt | ✅ Instruct to extract URL | `utils/scraper_utils.py` | Medium |
| LinkedIn Post | ✅ Append URL to post | `utils/scraper_utils.py` | Low |
| CSV Export | ✅ Add URL column | Auto-handled by Pydantic | Low |
| Documentation | ✅ Update examples | README.MD, SET_UP.md | Low |

### Step-by-Step Implementation

#### Step 1: Update Data Model

**File:** `models/venue.py`

```python
from pydantic import BaseModel, HttpUrl
from typing import Optional


class Venue(BaseModel):
    """
    Represents the data structure of a News Story from Binghamton University.
    All fields are required for complete story extraction.
    """

    story_title: str
    story_category: str
    story_summary: str
    story_url: str  # NEW: URL to the full story
    story_LinkedIn_post: str
```

**Why:** Pydantic model defines the contract for all data flowing through the system.

---

#### Step 2: Update Configuration

**File:** `config.py`

```python
# config.py

# BINGHAMTON UNIVERSITY NEWS CONFIGURATION
BASE_URL = "https://www.binghamton.edu/news/home"
CSS_SELECTOR = "article, .story, .news-item"
REQUIRED_KEYS = [
    "story_title",
    "story_category",
    "story_summary",
    "story_url",        # NEW: Added URL to required fields
    "story_LinkedIn_post",
]
```

**Why:** Ensures validation logic checks for URL presence.

---

#### Step 3: Update LLM Extraction Instructions

**File:** `utils/scraper_utils.py`

**Location:** Line ~40-50 in `get_llm_strategy()` function

```python
def get_llm_strategy() -> LLMExtractionStrategy:
    """
    Returns the configuration for the language model extraction strategy.
    """
    return LLMExtractionStrategy(
        provider="groq/llama-3.3-70b-versatile",
        api_token=os.getenv("GROQ_API_KEY"),
        schema=Venue.model_json_schema(),
        extraction_type="schema",
        instruction=(
            "Extract all news stories from the Binghamton University news page. For each story, provide:\n"
            "1. story_title: The headline or title of the news story\n"
            "2. story_category: The category or topic (e.g., 'Arts & Culture', 'Athletics', 'Business', 'Health', 'Science & Technology', 'Campus News', etc.)\n"
            "3. story_summary: A brief 2-3 sentence summary of the story\n"
            "4. story_url: The COMPLETE URL link to the full story (must include https:// and full domain)\n"  # NEW
            "5. story_LinkedIn_post: Create an engaging LinkedIn post (100-150 words) about this story. "
            "Include relevant hashtags and make it professional yet engaging. "
            "At the END of the post, add 'Read more: [story_url]' so people can click to read the full article.\n\n"  # MODIFIED
            "Return as many news stories as you can find in the content."
        ),
        input_format="markdown",
        verbose=True,
    )
```

**Why:** LLM needs explicit instructions to extract URLs and append them to posts.

---

#### Step 4: Test & Validate

```bash
# Run the scraper
python main.py

# Check the CSV output
# Should now have story_url column
# LinkedIn posts should end with "Read more: [url]"
```

**Validation Checklist:**
- [ ] CSV has `story_url` column
- [ ] All URLs are complete (include https://)
- [ ] LinkedIn posts end with "Read more: [url]"
- [ ] No extraction errors from LLM

---

### 🔧 Troubleshooting

**Problem:** LLM doesn't extract URLs correctly

**Solutions:**
1. Check if URLs are visible in the page HTML
2. Modify CSS selector to capture link elements
3. Post-process extracted data to build URLs from relative paths
4. Add URL construction logic in `fetch_and_process_page()`

**Example URL Construction:**

```python
# In utils/scraper_utils.py, after extraction
for venue in extracted_data:
    # If URL is relative, make it absolute
    if venue.get("story_url") and not venue["story_url"].startswith("http"):
        venue["story_url"] = f"https://www.binghamton.edu{venue['story_url']}"
```

---

## Feature 2: Streamlit Dashboard

### 🎯 Objective
Create an interactive dashboard to visualize scraped stories and trigger new scrapes.

### Dashboard Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Binghamton News Dashboard                             │
├──────────────┬──────────────────────────────────────────────────────────┤
│              │  📰 Latest News Stories (13)                              │
│  SIDEBAR     │                                                           │
│              │  ┌────────────────┐  ┌────────────────┐                  │
│ [🔄 Refresh] │  │ Story Card 1   │  │ Story Card 2   │                  │
│              │  │ Title: ...     │  │ Title: ...     │                  │
│ Last Updated │  │ Category: ...  │  │ Category: ...  │                  │
│ 2 mins ago   │  │ LinkedIn Post  │  │ LinkedIn Post  │                  │
│              │  │ [Read More]    │  │ [Read More]    │                  │
│ Stats:       │  └────────────────┘  └────────────────┘                  │
│ • 13 stories │                                                           │
│ • 5 cats     │  ┌────────────────┐  ┌────────────────┐                  │
│ • Updated    │  │ Story Card 3   │  │ Story Card 4   │                  │
│              │  │ ...            │  │ ...            │                  │
│ [Export CSV] │  └────────────────┘  └────────────────┘                  │
│              │                                                           │
│ [⚙️ Settings]│  ... more cards ...                                      │
│              │                                                           │
└──────────────┴──────────────────────────────────────────────────────────┘
```

### Impact Analysis

| Component | Change Required | New File(s) | Complexity |
|-----------|----------------|-------------|------------|
| Streamlit App | ✅ Create dashboard | `app.py` | Medium |
| Dependencies | ✅ Add Streamlit | `requirements.txt` | Low |
| Main Logic | ✅ Refactor for reusability | `main.py` | Medium |
| Data Persistence | ✅ Cache/database | `utils/data_utils.py` | Medium |
| Styling | ✅ CSS customization | `app.py` | Low |

### Step-by-Step Implementation

#### Step 1: Update Requirements

**File:** `requirements.txt`

```txt
Crawl4AI
python-dotenv
pydantic
streamlit>=1.30.0
pandas
```

**Install:**
```bash
pip install -r requirements.txt
```

---

#### Step 2: Refactor Main Logic for Reusability

**File:** `main.py`

Add a function that returns stories instead of just printing:

```python
async def crawl_venues() -> list[dict]:
    """
    Main function to crawl venue data from the website.
    Returns the list of stories instead of just saving to CSV.
    """
    # ... existing code ...
    
    # At the end, return the stories
    return all_venues  # Return instead of just saving


async def main():
    """
    Entry point of the script.
    """
    stories = await crawl_venues()
    
    # Save to CSV (optional - dashboard might handle this)
    if stories:
        save_venues_to_csv(stories, "binghamton_news_stories.csv")
    
    return stories


def run_scraper():
    """
    Synchronous wrapper for async scraper - used by Streamlit.
    """
    return asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
```

---

#### Step 3: Create Streamlit Dashboard

**File:** `app.py` (NEW FILE)

```python
import streamlit as st
import pandas as pd
from datetime import datetime
import asyncio
from pathlib import Path
import json

# Import our scraper
from main import run_scraper

# Page configuration
st.set_page_config(
    page_title="Binghamton News Dashboard",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better card styling
st.markdown("""
<style>
    .story-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 100%;
    }
    .story-title {
        font-size: 18px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .story-category {
        display: inline-block;
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
        margin-bottom: 10px;
    }
    .linkedin-post {
        font-size: 14px;
        color: #333;
        line-height: 1.6;
        margin-top: 10px;
        padding: 10px;
        background-color: white;
        border-left: 3px solid #0077B5;
        border-radius: 5px;
    }
    .refresh-button {
        width: 100%;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'stories' not in st.session_state:
    st.session_state.stories = []
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = None
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

# Helper function to load existing stories
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

# Load existing stories on first run
if not st.session_state.stories:
    st.session_state.stories = load_existing_stories()
    if st.session_state.stories:
        st.session_state.last_updated = datetime.now()

# Sidebar
with st.sidebar:
    st.title("📰 Binghamton News")
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh Stories", use_container_width=True, type="primary"):
        st.session_state.is_loading = True
        with st.spinner("Scraping latest news..."):
            try:
                stories = run_scraper()
                st.session_state.stories = stories
                st.session_state.last_updated = datetime.now()
                st.success(f"✅ Loaded {len(stories)} stories!")
            except Exception as e:
                st.error(f"❌ Error: {e}")
            finally:
                st.session_state.is_loading = False
    
    # Stats
    st.markdown("---")
    st.subheader("📊 Statistics")
    
    if st.session_state.stories:
        num_stories = len(st.session_state.stories)
        categories = set(story.get('story_category', 'Unknown') for story in st.session_state.stories)
        
        st.metric("Total Stories", num_stories)
        st.metric("Categories", len(categories))
        
        if st.session_state.last_updated:
            time_diff = datetime.now() - st.session_state.last_updated
            mins_ago = int(time_diff.total_seconds() / 60)
            st.metric("Last Updated", f"{mins_ago} mins ago" if mins_ago < 60 else f"{int(mins_ago/60)} hrs ago")
    
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
    
    # Settings
    st.markdown("---")
    with st.expander("⚙️ Settings"):
        card_columns = st.slider("Cards per row", 1, 4, 2)
        show_summaries = st.checkbox("Show summaries", value=True)
        show_categories = st.checkbox("Show categories", value=True)

# Main content area
st.title("📰 Binghamton University News Dashboard")
st.markdown("---")

# Display stories
if not st.session_state.stories:
    st.info("👋 Click 'Refresh Stories' in the sidebar to load the latest news!")
else:
    # Category filter
    all_categories = ['All'] + sorted(set(story.get('story_category', 'Unknown') for story in st.session_state.stories))
    selected_category = st.selectbox("Filter by category:", all_categories)
    
    # Filter stories
    filtered_stories = st.session_state.stories
    if selected_category != 'All':
        filtered_stories = [s for s in st.session_state.stories if s.get('story_category') == selected_category]
    
    st.markdown(f"### Showing {len(filtered_stories)} stories")
    
    # Display stories in cards (grid layout)
    card_columns = st.sidebar.slider("Cards per row", 1, 4, 2) if 'card_columns' not in locals() else card_columns
    
    # Create columns for grid layout
    cols_per_row = card_columns
    rows = (len(filtered_stories) + cols_per_row - 1) // cols_per_row
    
    for row_idx in range(rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            story_idx = row_idx * cols_per_row + col_idx
            if story_idx < len(filtered_stories):
                story = filtered_stories[story_idx]
                
                with cols[col_idx]:
                    # Story card
                    with st.container():
                        # Title
                        st.markdown(f"""
                        <div class="story-card">
                            <div class="story-title">{story.get('story_title', 'No Title')}</div>
                        """, unsafe_allow_html=True)
                        
                        # Category badge
                        if show_categories:
                            st.markdown(f"""
                            <span class="story-category">{story.get('story_category', 'Uncategorized')}</span>
                            """, unsafe_allow_html=True)
                        
                        # Summary
                        if show_summaries:
                            st.markdown(f"**Summary:** {story.get('story_summary', 'No summary available')}")
                        
                        # LinkedIn post
                        st.markdown(f"""
                        <div class="linkedin-post">
                            <strong>📱 LinkedIn Post:</strong><br>
                            {story.get('story_LinkedIn_post', 'No post available')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Read more button (if URL available)
                        if story.get('story_url'):
                            st.link_button("🔗 Read Full Story", story['story_url'], use_container_width=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    Built with ❤️ for Binghamton University<br>
    Powered by AI (Llama 3.3 70B) | <a href='https://github.com/yalwesa1/binghamton-news-scraper'>GitHub</a>
</div>
""", unsafe_allow_html=True)
```

---

#### Step 4: Run the Dashboard

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

### 🎨 Dashboard Features

#### Implemented:
- ✅ **Refresh Button**: Click to scrape latest stories
- ✅ **Story Cards**: Grid layout with customizable columns
- ✅ **Category Filter**: Filter stories by category
- ✅ **Statistics**: Real-time metrics (story count, categories, last updated)
- ✅ **Export Options**: Download as CSV or JSON
- ✅ **Responsive Design**: Adjustable card layout
- ✅ **Professional Styling**: Clean, modern UI

#### Suggested Enhancements:
- 📊 **Analytics Tab**: Story trends over time
- 🔍 **Search Function**: Search by title or keywords
- 📅 **Date Filter**: Filter by date range
- 🔔 **Notifications**: Alert when new stories are found
- 📧 **Email Integration**: Send LinkedIn posts via email
- 🤖 **Auto-Refresh**: Schedule automatic scraping
- 💾 **Database Backend**: SQLite/PostgreSQL for history
- 📈 **Engagement Metrics**: Track which stories perform best

---

## Testing & Validation

### Feature 1: Story URLs

```bash
# Test 1: Run scraper
python main.py

# Test 2: Check CSV
# Verify story_url column exists and URLs are complete

# Test 3: Check LinkedIn posts
# Verify posts end with "Read more: [url]"
```

### Feature 2: Streamlit Dashboard

```bash
# Test 1: Install dependencies
pip install -r requirements.txt

# Test 2: Run dashboard
streamlit run app.py

# Test 3: Test refresh button
# Click refresh and verify stories load

# Test 4: Test filters
# Filter by category and verify results

# Test 5: Test export
# Download CSV and JSON and verify content
```

---

## Documentation Updates

After implementing both features:

### Files to Update:

1. **README.MD**
   - Add Streamlit dashboard section
   - Update usage instructions
   - Add screenshot of dashboard
   - Update features list

2. **SET_UP.md**
   - Add Streamlit installation steps
   - Add dashboard running instructions
   - Update troubleshooting section

3. **road_map.md**
   - Mark dashboard as completed in Phase 1
   - Update architecture diagram
   - Add dashboard to components section

4. **generate_flow_chart.md**
   - Add Streamlit app flow diagram
   - Update system architecture diagram
   - Add UI interaction flows

---

## Commit Strategy

### Commit 1: Add Story URLs
```bash
git add models/venue.py config.py utils/scraper_utils.py
git commit -m "feat: add story URLs to LinkedIn posts

- Add story_url field to Venue model
- Update LLM extraction to capture URLs
- Append 'Read more: [url]' to LinkedIn posts
- Update REQUIRED_KEYS to include story_url

Enables users to click through from LinkedIn posts to full stories."
```

### Commit 2: Add Streamlit Dashboard
```bash
git add app.py requirements.txt main.py
git commit -m "feat: add Streamlit dashboard for news visualization

- Create interactive dashboard with story cards
- Add refresh button to trigger new scrapes
- Implement category filtering and search
- Add export options (CSV, JSON)
- Include statistics and last updated tracking

Dashboard provides visual interface for managing and sharing news stories."
```

### Commit 3: Update Documentation
```bash
git add README.MD SET_UP.md road_map.md
git commit -m "docs: update for story URLs and Streamlit dashboard

- Document new story_url field usage
- Add Streamlit setup and usage instructions
- Update architecture diagrams
- Add dashboard screenshots and features list"
```

---

## Questions & Suggestions

### Your Questions Answered:

**Q: Should I add anything else to the LinkedIn post?**
**A:** Consider adding:
- Emoji at the start for visual appeal (e.g., 📰 🎓 🔬)
- Call-to-action phrases (e.g., "Check out..." "Discover how...")
- University branding (e.g., "#BearcardsUnite" or Binghamton-specific hashtags)

**Q: Any other dashboard features?**
**A:** Definitely! See suggestions below.

### Recommended Dashboard Enhancements:

#### Priority 1 (High Value, Low Effort):
1. **Copy LinkedIn Post Button**: One-click copy to clipboard
2. **Dark Mode Toggle**: For better viewing experience
3. **Story Sorting**: Sort by date, category, or title
4. **Expandable Cards**: Click to see full summary

#### Priority 2 (High Value, Medium Effort):
5. **Auto-Refresh**: Schedule scraping (every hour, daily)
6. **Story History**: Track stories over time with database
7. **Duplicate Detection Dashboard**: Show which stories were skipped
8. **LinkedIn API Integration**: Post directly from dashboard

#### Priority 3 (Nice to Have):
9. **Analytics Dashboard**: Story performance metrics
10. **Multi-Source Support**: Add other universities
11. **Email Digest**: Send daily summary of stories
12. **Mobile App**: PWA for mobile access

---

## Best Practices Checklist

### Before Making Any Change:
- [ ] Read this guide completely
- [ ] Identify all affected files
- [ ] Plan the change sequence
- [ ] Create a feature branch

### During Implementation:
- [ ] Update data model first (if needed)
- [ ] Update configuration second
- [ ] Update business logic third
- [ ] Test incrementally at each step
- [ ] Update LLM prompts carefully

### After Implementation:
- [ ] Run end-to-end tests
- [ ] Update all documentation
- [ ] Create meaningful commits
- [ ] Test the Streamlit dashboard (if applicable)
- [ ] Update this guide with new patterns

---

## Senior Engineer Tips

### 1. **Single Responsibility Principle**
Each function should do one thing well. If `crawl_venues()` does too much, break it into smaller functions.

### 2. **DRY (Don't Repeat Yourself)**
If you're copy-pasting code, create a shared function instead.

### 3. **Configuration Over Code**
Put magic numbers and strings in `config.py`, not scattered in code.

### 4. **Error Handling**
Always handle exceptions gracefully, especially in the dashboard where users see errors.

### 5. **Type Hints**
Use type hints everywhere - they're documentation and validation in one.

### 6. **Logging Over Print**
Replace `print()` statements with proper logging for production code.

### 7. **Testing**
Write tests for new features, even simple ones. Future you will be grateful.

### 8. **Documentation**
Update docs **immediately** after changing code. Don't wait.

---

## Conclusion

This guide provides a systematic framework for extending the Binghamton News Scraper. Follow the checklists, update all relevant files, and maintain consistency across the codebase.

**Remember:** Good software engineering is about maintainability, not just functionality. Every change should make the codebase better, not more complicated.

---

**Author:** Senior Engineering Team  
**Last Updated:** January 2026  
**Version:** 1.0
