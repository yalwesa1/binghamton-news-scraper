# Binghamton University News Scraper

This project is an AI-powered web scraper that automatically extracts news stories from Binghamton University's news website and generates engaging LinkedIn posts. Built with Python using Crawl4AI and LLM-powered extraction via Groq API (Llama 3.3 70B), it transforms university news into structured data with ready-to-publish social media content.

## Features

- ⚡ **Asynchronous web crawling** using [Crawl4AI](https://pypi.org/project/Crawl4AI/)
- 🤖 **LLM-powered data extraction** (Llama 3.3 70B via Groq API)
- 📱 **AI-generated LinkedIn posts** with hashtags for each story
- ✅ **Smart validation** with required field checking
- 🔍 **Automatic deduplication** by story title
- 📊 **CSV export** of news stories with LinkedIn posts
- 🎯 **Pagination support** with automatic "no results" detection
- 📦 **Modular code structure** ideal for customization and extensibility

## Quick Start

1. **Clone and setup environment:**
   ```bash
   git clone https://github.com/yalwesa1/binghamton-news-scraper.git
   cd binghamton-news-scraper
   conda create -n binghamton-news python=3.12 -y
   conda activate binghamton-news
   pip install -r requirements.txt
   ```

2. **Create `.env` file with your API key:**
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
   Get your free API key at: https://console.groq.com/

3. **Run the scraper:**
   ```bash
   python main.py
   ```
   
   This will extract news stories from Binghamton University and save them to `binghamton_news_stories.csv`

📖 **For detailed setup instructions, see [SET_UP.md](SET_UP.md)**

## Documentation

- **[SET_UP.md](SET_UP.md)** - Comprehensive environment setup guide with troubleshooting
- **[road_map.md](road_map.md)** - Project vision, architecture, and development roadmap
- **[generate_flow_chart.md](generate_flow_chart.md)** - Visual flow charts using Mermaid diagrams

## Project Structure
```
binghamton-news-scraper/
├── main.py                    # Main entry point for the scraper
├── config.py                  # Configuration (Binghamton News URL, selectors)
├── requirements.txt           # Python package dependencies
├── .env                       # Environment variables (create this - not in repo)
├── .gitignore                # Git ignore file
├── README.MD                 # This file
├── SET_UP.md                 # Detailed setup instructions
├── road_map.md               # Project roadmap and architecture
├── generate_flow_chart.md   # 15 Mermaid flow diagrams
├── git_workflow_commit.md   # Git best practices template
├── models/
│   ├── __init__.py
│   └── venue.py              # Pydantic News Story data model
└── utils/
    ├── __init__.py
    ├── data_utils.py         # Data validation and CSV export
    └── scraper_utils.py      # Crawler config and LLM extraction logic
```

## Requirements

- **Python**: 3.12 (recommended) or 3.10+
- **Dependencies**: 
  - `Crawl4AI` - Async web crawling framework
  - `python-dotenv` - Environment variable management
  - `pydantic` - Data validation and schemas
- **API Key**: Groq API key for LLM extraction (free tier available)

## Installation

### Quick Install

```bash
# Create virtual environment (conda or venv)
conda create -n deep-seek-crawler python=3.12 -y
conda activate deep-seek-crawler

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

### Detailed Setup

For comprehensive installation instructions, including:
- Both conda and venv setup options
- Checking for latest package versions
- Troubleshooting common issues
- Platform-specific instructions

**See [SET_UP.md](SET_UP.md) for complete details.**

## Usage

```bash
python main.py
```

**What happens:**
1. 🌐 Opens browser session (Chromium via Crawl4AI)
2. 📄 Fetches Binghamton University News homepage
3. 🤖 Extracts news stories using Llama 3.3 70B LLM
4. 📱 AI generates LinkedIn posts for each story with hashtags
5. ✅ Validates required fields and removes duplicates
6. 💾 Saves results to `binghamton_news_stories.csv`
7. 📊 Displays LLM usage statistics (tokens, cost)

**Output:** `binghamton_news_stories.csv` with columns:
- `story_title` - The headline of the news story
- `story_category` - Category (Arts & Culture, Health, Science & Technology, etc.)
- `story_summary` - 2-3 sentence summary of the story
- `story_LinkedIn_post` - AI-generated LinkedIn post with hashtags

## Configuration

Edit `config.py` to customize scraper behavior:

```python
# Target website
BASE_URL = "https://www.binghamton.edu/news/home"

# CSS selector to target news story containers
CSS_SELECTOR = "article, .story, .news-item"

# Required fields for complete news story records
REQUIRED_KEYS = ["story_title", "story_category", "story_summary", "story_LinkedIn_post"]
```

**Customization options:**
- Change `BASE_URL` to scrape different news sources
- Adjust `CSS_SELECTOR` if website structure changes
- Modify `REQUIRED_KEYS` to require different fields
- Edit rate limiting (sleep time) in `main.py` line 62
- Customize LLM instructions in `utils/scraper_utils.py` for different content types

## How It Works

### Data Flow
```
Binghamton News → Crawl4AI → CSS Filter → LLM (Llama 3.3 70B) → Story Extraction → LinkedIn Post Generation → Validation → CSV
```

### Key Components
- **`main.py`**: Orchestrates scraping, pagination, and CSV output
- **`models/venue.py`**: Pydantic schema for news story data structure
- **`utils/scraper_utils.py`**: Browser config, LLM strategy, extraction & LinkedIn post generation
- **`utils/data_utils.py`**: Validation, deduplication, CSV export

### AI-Powered Features
The scraper uses **Llama 3.3 70B** via Groq API to:
1. **Extract structured data** from unstructured HTML content
2. **Generate engaging LinkedIn posts** (100-150 words) for each story
3. **Add relevant hashtags** automatically
4. **Categorize stories** by topic (Arts & Culture, Health, Science & Technology, etc.)

The LLM receives markdown-converted content and returns JSON with complete story data plus ready-to-publish social media content.

## Roadmap

**Current (Phase 1):** ✅ Binghamton News scraper with AI-generated LinkedIn posts

**Completed:**
- ✅ Async web crawling with Crawl4AI
- ✅ LLM-powered news extraction (Llama 3.3 70B)
- ✅ AI-generated LinkedIn posts with hashtags
- ✅ CSV export with story data
- ✅ Comprehensive documentation with flow charts

**Planned:**
- 🔄 **Phase 2**: Multi-source news scraping (other universities, news sites)
- 📊 **Phase 3**: Sentiment analysis, trending topics detection
- 🚀 **Phase 4**: Automated scheduling and posting to LinkedIn
- 🧠 **Phase 5**: Story categorization, content recommendations, analytics dashboard

**See [road_map.md](road_map.md) for complete roadmap.**

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Browser window appears | Expected behavior (headless=False by default) |
| LLM extraction fails | Verify `GROQ_API_KEY` is valid and has quota |
| No stories extracted | Check if CSS selector matches website structure |
| Import errors | Reinstall dependencies: `pip install -r requirements.txt` |
| Playwright errors | Run: `python -m playwright install` |

**For comprehensive troubleshooting, see [SET_UP.md](SET_UP.md).**

## Use Cases

This scraper is perfect for:
- 📱 **Social Media Managers** - Automate LinkedIn content creation for university news
- 📊 **Communications Teams** - Monitor and share university news efficiently
- 🎓 **Alumni Relations** - Keep alumni engaged with automated updates
- 📈 **Analytics** - Track news trends and story categories over time
- 🤖 **AI/LLM Projects** - Template for building content generation tools

## Contributing

This project uses a modular structure for easy extension:
- Add new data fields in `models/venue.py`
- Customize LLM instructions in `utils/scraper_utils.py`
- Extend validation rules in `utils/data_utils.py`
- See `generate_flow_chart.md` for 15 detailed system diagrams
- Check `git_workflow_commit.md` for contribution guidelines

## Resources

- **[Crawl4AI Documentation](https://docs.crawl4ai.com/)** - Official crawler framework docs
- **[Groq API Console](https://console.groq.com/)** - Get your API key
- **[Pydantic Documentation](https://docs.pydantic.dev/)** - Data validation library
- **[Mermaid Diagrams](https://mermaid.js.org/)** - View flow charts in generate_flow_chart.md

## License

To be determined.

---

**Author:** Yaseen Alwesabi ([GitHub](https://github.com/yalwesa1) | [LinkedIn](https://linkedin.com/in/yaseen-al-wesabi-43164478))  
**Affiliation:** Binghamton University  
**Last Updated:** January 2026  
**Python Version:** 3.12+  
**Status:** Active Development
