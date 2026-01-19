# SET_UP.md

## Overview
This project is an async Python web crawler that uses Crawl4AI plus an LLM extraction strategy to collect wedding reception venue data and save it to CSV.

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
git clone <repo-url>
cd deepseek-ai-web-crawler
```

---

## 2. Create and activate a virtual environment

### Option A: Conda (Recommended)
```bash
conda create -n deep-seek-crawler python=3.12 -y
conda activate deep-seek-crawler
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
Create a `.env` file in the project root (`deepseek-ai-web-crawler/`):

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

## 5. Configure Crawl Targets (Optional)
Edit `config.py` to customize the crawler behavior:
- **`BASE_URL`**: The URL of the website to scrape
- **`CSS_SELECTOR`**: CSS selector to target venue content
- **`REQUIRED_KEYS`**: List of required fields for a venue to be considered complete

Example:
```python
BASE_URL = "https://www.theknot.com/marketplace/wedding-reception-venues-atlanta-ga"
CSS_SELECTOR = "[class^='info-container']"
REQUIRED_KEYS = [
    "name",
    "price",
    "location",
    "capacity",
    "rating",
    "reviews",
    "description",
]
```

---

## 6. Run the Crawler
```bash
python main.py
```

**What happens:**
- The crawler will open a browser window (headless mode is disabled by default)
- It will iterate through pages on the configured website
- Extract venue data using the LLM strategy
- Validate and deduplicate the results
- Save complete venues to `complete_venues.csv`
- Display LLM usage statistics

**Output:**
- `complete_venues.csv` in the project root directory

---

## 7. Testing & Verification
After running the crawler:
1. Check that `complete_venues.csv` was created
2. Verify the CSV contains the expected columns (name, price, location, etc.)
3. Review the console output for any errors or warnings
4. Check the LLM usage statistics to monitor API consumption

---

## 8. Troubleshooting

### Browser Issues
- **If the browser window appears**: This is expected behavior (headless=False in browser config)
- **If Crawl4AI prompts for browser setup**: Follow the on-screen instructions to install browser dependencies

### API Issues
- **If LLM extraction fails**: Verify your `GROQ_API_KEY` is valid and has sufficient quota
- **Rate limiting**: Adjust the sleep time in `main.py` (line 62) to increase delays between requests

### Data Issues
- **No venues extracted**: Check if the CSS selector matches the target website's structure
- **Incomplete venues**: Review `REQUIRED_KEYS` in `config.py` - some fields may not always be available
- **Duplicates**: The system uses venue names for deduplication; adjust logic in `utils/data_utils.py` if needed

### Dependencies Issues
- **Import errors**: Ensure all dependencies are installed: `pip list`
- **Version conflicts**: Try creating a fresh virtual environment
- **Crawl4AI installation**: May require additional system dependencies on some platforms

---

## 9. Project Structure
```
deepseek-ai-web-crawler/
├── main.py                 # Main entry point
├── config.py              # Configuration constants
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore rules
├── README.MD             # Project documentation
├── models/
│   ├── __init__.py
│   └── venue.py          # Pydantic Venue model
└── utils/
    ├── __init__.py
    ├── scraper_utils.py  # Crawler configuration & extraction
    └── data_utils.py     # Data processing & CSV export
```

---

## 10. Development Tips
- **Logging**: The project uses print statements. Consider integrating Python's `logging` module for production
- **Browser Mode**: Set `headless=True` in `utils/scraper_utils.py` for background operation
- **Rate Limiting**: Adjust sleep duration in `main.py` to be respectful of target websites
- **Data Validation**: Extend the Venue model in `models/venue.py` with additional validation rules
- **Multiple Sources**: Modify `config.py` or create multiple config files for different crawl targets

---

## 11. Next Steps
- Review the `road_map.md` for project evolution plans
- Check `generate_flow_chart.md` for visual understanding of the system flow
- Customize extraction instructions in `utils/scraper_utils.py` for your specific needs
- Consider adding database storage instead of CSV for larger datasets
