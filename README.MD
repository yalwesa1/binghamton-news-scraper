# Deep Seek Crawler

This project is an asynchronous Python web crawler that extracts venue data (wedding reception venues) from websites using Crawl4AI and LLM-powered extraction. It utilizes DeepSeek R1 (via Groq API) for intelligent parsing of unstructured web content and exports validated, deduplicated data to CSV.

## Features

- ⚡ **Asynchronous web crawling** using [Crawl4AI](https://pypi.org/project/Crawl4AI/)
- 🤖 **LLM-powered data extraction** (DeepSeek R1 via Groq API)
- ✅ **Smart validation** with required field checking
- 🔍 **Automatic deduplication** by venue name
- 📊 **CSV export** of extracted venue information
- 🎯 **Pagination support** with automatic "no results" detection
- 📦 **Modular code structure** ideal for beginners and extensibility

## Quick Start

1. **Clone and setup environment:**
   ```bash
   conda create -n deep-seek-crawler python=3.12 -y
   conda activate deep-seek-crawler
   pip install -r requirements.txt
   ```

2. **Create `.env` file with your API key:**
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
   Get your API key at: https://console.groq.com/

3. **Run the crawler:**
   ```bash
   python main.py
   ```

📖 **For detailed setup instructions, see [SET_UP.md](SET_UP.md)**

## Documentation

- **[SET_UP.md](SET_UP.md)** - Comprehensive environment setup guide with troubleshooting
- **[road_map.md](road_map.md)** - Project vision, architecture, and development roadmap
- **[generate_flow_chart.md](generate_flow_chart.md)** - Visual flow charts using Mermaid diagrams

## Project Structure
```
deepseek-ai-web-crawler/
├── main.py                 # Main entry point for the crawler
├── config.py              # Configuration constants (Base URL, CSS selectors, etc.)
├── requirements.txt       # Python package dependencies
├── .env                   # Environment variables (create this - not in repo)
├── .gitignore            # Git ignore file
├── README.MD             # This file
├── SET_UP.md             # Detailed setup instructions
├── road_map.md           # Project roadmap and architecture
├── generate_flow_chart.md # Mermaid flow diagrams
├── models/
│   ├── __init__.py
│   └── venue.py          # Pydantic Venue data model
└── utils/
    ├── __init__.py
    ├── data_utils.py     # Data validation and CSV export
    └── scraper_utils.py  # Crawler configuration and extraction logic
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
2. 📄 Iterates through paginated results
3. 🤖 Extracts venue data using LLM strategy
4. ✅ Validates required fields and removes duplicates
5. 💾 Saves results to `complete_venues.csv`
6. 📊 Displays LLM usage statistics (tokens, cost)

**Output:** `complete_venues.csv` with columns: name, location, price, capacity, rating, reviews, description

## Configuration

Edit `config.py` to customize crawler behavior:

```python
# Target website
BASE_URL = "https://www.theknot.com/marketplace/wedding-reception-venues-atlanta-ga"

# CSS selector to target venue containers
CSS_SELECTOR = "[class^='info-container']"

# Required fields for complete venue records
REQUIRED_KEYS = ["name", "price", "location", "capacity", "rating", "reviews", "description"]
```

**Customization options:**
- Change `BASE_URL` for different locations or categories
- Adjust `CSS_SELECTOR` if website structure changes
- Modify `REQUIRED_KEYS` to require different fields
- Edit rate limiting (sleep time) in `main.py` line 62

## How It Works

### Data Flow
```
Website → Crawl4AI → CSS Filter → LLM (DeepSeek R1) → Validation → Deduplication → CSV
```

### Key Components
- **`main.py`**: Orchestrates crawl loop, pagination, and output
- **`models/venue.py`**: Pydantic schema for type-safe venue data
- **`utils/scraper_utils.py`**: Browser config, LLM strategy, extraction logic
- **`utils/data_utils.py`**: Validation, deduplication, CSV export

### LLM Extraction
The crawler uses DeepSeek R1 Distill (70B) via Groq API to intelligently extract structured data from unstructured HTML. The LLM receives markdown-converted content and returns JSON matching the Venue schema.

## Roadmap

**Current (Phase 1):** ✅ MVP with async crawling, LLM extraction, validation, CSV export

**Planned:**
- 🔄 **Phase 2**: Structured logging, retry logic, monitoring
- 📊 **Phase 3**: Enhanced validation, price normalization, fuzzy deduplication
- 🚀 **Phase 4**: Multi-source support, parallel crawling, database storage
- 🧠 **Phase 5**: Sentiment analysis, venue recommendations, trend detection

**See [road_map.md](road_map.md) for complete roadmap.**

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Browser window appears | Expected behavior (headless=False by default) |
| LLM extraction fails | Verify `GROQ_API_KEY` is valid and has quota |
| No venues extracted | Check if CSS selector matches website structure |
| Import errors | Reinstall dependencies: `pip install -r requirements.txt` |

**For comprehensive troubleshooting, see [SET_UP.md](SET_UP.md).**

## Contributing

This project uses a modular structure for easy extension:
- Add new data fields in `models/venue.py`
- Customize extraction logic in `utils/scraper_utils.py`
- Extend validation in `utils/data_utils.py`
- See `generate_flow_chart.md` for system architecture

## Resources

- **[Crawl4AI Documentation](https://docs.crawl4ai.com/)** - Official crawler framework docs
- **[Groq API Console](https://console.groq.com/)** - Get your API key
- **[Pydantic Documentation](https://docs.pydantic.dev/)** - Data validation library
- **[Mermaid Diagrams](https://mermaid.js.org/)** - View flow charts in generate_flow_chart.md

## License

To be determined.

---

**Last Updated:** January 2026  
**Python Version:** 3.12+  
**Status:** Active Development
