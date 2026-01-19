# SET_UP.md

## Overview
This project is an AI-powered web scraper that extracts news stories from Binghamton University's website and generates engaging LinkedIn posts using Llama 3.3 70B via Groq API.

---

## Prerequisites
- **Python**: 3.12 (recommended) or 3.10+
- **Git**: for cloning the repo
- **OS**: Windows/macOS/Linux
- **Network access** to the target website and the LLM provider (Groq API)

Optional:
- **Conda** (if you prefer conda environments)

---

## 1. Clone the repo
```bash
git clone https://github.com/yalwesa1/binghamton-news-scraper.git
cd binghamton-news-scraper
```

---

## 2. Create and activate a virtual environment

### Option A: Conda (Recommended)
```bash
conda create -n binghamton-news python=3.12 -y
conda activate binghamton-news
```

### Option B: venv
```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows Command Prompt
.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate
```

---

## 3. Install dependencies

### Current Requirements
The project uses the following packages (see `requirements.txt`):
- **Crawl4AI**: Async web crawling framework with LLM integration
- **python-dotenv**: Environment variable management from .env files
- **pydantic**: Data validation and schema modeling

Install all dependencies:
```bash
pip install -r requirements.txt
```

### Check for Latest Versions
To verify the latest available versions:
```bash
pip index versions crawl4ai
pip index versions python-dotenv
pip index versions pydantic
```

### Upgrade to Latest Versions (Optional)
To upgrade all dependencies to their latest versions:
```bash
pip install -U crawl4ai python-dotenv pydantic
```

To pin the versions after updating:
```bash
pip freeze > requirements.txt
```

---

## 4. Environment Variables
Create a `.env` file in the project root (`binghamton-news-scraper/`):

```env
GROQ_API_KEY=your_groq_api_key_here
```

**Getting a Groq API Key:**
1. Visit https://console.groq.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key to your `.env` file

**Note:** The `.env` file is in `.gitignore`, so it won't be pushed to version control.

---

## 5. Configure Scraper (Optional)
Edit `config.py` to customize the scraper behavior:
- **`BASE_URL`**: The URL of the news website to scrape
- **`CSS_SELECTOR`**: CSS selector to target news story containers
- **`REQUIRED_KEYS`**: List of required fields for a complete news story

Current Configuration:
```python
BASE_URL = "https://www.binghamton.edu/news/home"
CSS_SELECTOR = "article, .story, .news-item"
REQUIRED_KEYS = [
    "story_title",
    "story_category",
    "story_summary",
    "story_LinkedIn_post",
]
```

---

## 6. Run the Scraper
```bash
python main.py
```

**What happens:**
- The scraper will open a browser window (headless mode is disabled by default)
- It will fetch Binghamton University News homepage
- Extract news stories using Llama 3.3 70B LLM
- Generate LinkedIn posts for each story with hashtags
- Validate and deduplicate the results
- Save stories to `binghamton_news_stories.csv`
- Display LLM usage statistics (tokens used, cost)

**Output:**
- `binghamton_news_stories.csv` with columns:
  - `story_title` - News headline
  - `story_category` - Story category
  - `story_summary` - 2-3 sentence summary
  - `story_LinkedIn_post` - AI-generated post with hashtags

---

## 7. Testing & Verification
After running the scraper:
1. Check that `binghamton_news_stories.csv` was created
2. Verify the CSV contains all 4 columns (story_title, story_category, story_summary, story_LinkedIn_post)
3. Review the console output for any errors or warnings
4. Check the LLM usage statistics to monitor API consumption
5. Review the LinkedIn posts generated - they should be 100-150 words with relevant hashtags

---

## 8. Troubleshooting

### Browser Issues
- **If the browser window appears**: This is expected behavior (headless=False in browser config)
- **If Crawl4AI prompts for browser setup**: Follow the on-screen instructions to install browser dependencies

### API Issues
- **If LLM extraction fails**: Verify your `GROQ_API_KEY` is valid and has sufficient quota
- **Rate limiting**: Adjust the sleep time in `main.py` (line 62) to increase delays between requests

### Data Issues
- **No stories extracted**: Check if the CSS selector matches the target website's structure
- **Incomplete stories**: Review `REQUIRED_KEYS` in `config.py` - ensure all 4 fields are being extracted
- **Duplicates**: The system uses story titles for deduplication; adjust logic in `utils/data_utils.py` if needed
- **Poor LinkedIn posts**: Customize the LLM instructions in `utils/scraper_utils.py` line 40-50

### Dependencies Issues
- **Import errors**: Ensure all dependencies are installed: `pip list`
- **Version conflicts**: Try creating a fresh virtual environment
- **Crawl4AI installation**: May require additional system dependencies on some platforms

---

## 9. Project Structure
```
binghamton-news-scraper/
├── main.py                    # Main entry point
├── config.py                  # Configuration for Binghamton News
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
├── .gitignore                # Git ignore rules
├── README.MD                 # Project documentation
├── SET_UP.md                 # This file
├── road_map.md               # Project roadmap
├── generate_flow_chart.md   # 15 Mermaid diagrams
├── git_workflow_commit.md   # Git best practices
├── models/
│   ├── __init__.py
│   └── venue.py              # News Story Pydantic model
└── utils/
    ├── __init__.py
    ├── scraper_utils.py      # Scraper config & LinkedIn post generation
    └── data_utils.py         # Data validation & CSV export
```

---

## 10. Development Tips
- **Logging**: The project uses print statements. Consider integrating Python's `logging` module for production
- **Browser Mode**: Set `headless=True` in `utils/scraper_utils.py` line 27 for background operation
- **Rate Limiting**: Adjust sleep duration in `main.py` line 62 to be respectful of target websites
- **Customize LinkedIn Posts**: Modify LLM instructions in `utils/scraper_utils.py` to change post style/length
- **Multiple Sources**: Update `BASE_URL` in `config.py` to scrape different news websites
- **Add Fields**: Extend the News Story model in `models/venue.py` with additional fields (e.g., publish_date, author)

---

## 11. Next Steps
- Review the `road_map.md` for project evolution plans
- Check `generate_flow_chart.md` for visual understanding of the system flow
- Customize extraction instructions in `utils/scraper_utils.py` for your specific needs
- Consider adding database storage instead of CSV for larger datasets
