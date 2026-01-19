# road_map.md

## Vision & Goals

### Mission
Automate the extraction of venue data from wedding marketplace websites using a repeatable, LLM-assisted crawler that outputs structured, validated data for analysis and decision-making.

### Key Objectives
1. **Efficiency**: Replace manual data collection with automated async crawling
2. **Accuracy**: Leverage LLM extraction for intelligent parsing of unstructured web content
3. **Data Quality**: Ensure completeness and eliminate duplicates through validation
4. **Scalability**: Design for expansion to multiple categories and locations
5. **Usability**: Provide clean CSV output for immediate use in analytics tools

---

## Core Components

### 1. Main Controller (`main.py`)
**Purpose**: Orchestrates the crawl loop and pagination  
**Key Functions**:
- Initialize browser and LLM configurations
- Manage page iteration and state
- Coordinate data collection across pages
- Handle graceful shutdown on "No Results Found"
- Export aggregated results to CSV
- Report usage statistics

### 2. Configuration (`config.py`)
**Purpose**: Centralized settings for crawler behavior  
**Key Settings**:
- `BASE_URL`: Target website URL
- `CSS_SELECTOR`: DOM element selector for venue containers
- `REQUIRED_KEYS`: Fields necessary for a complete venue record

### 3. Data Models (`models/venue.py`)
**Purpose**: Define structured schema for venue data  
**Features**:
- Pydantic BaseModel for type validation
- Schema generation for LLM extraction
- Fields: name, location, price, capacity, rating, reviews, description

### 4. Scraper Utilities (`utils/scraper_utils.py`)
**Purpose**: Configure and execute web crawling operations  
**Key Functions**:
- `get_browser_config()`: Browser settings (Chromium, headless mode, verbosity)
- `get_llm_strategy()`: LLM provider setup (Groq/DeepSeek) with extraction instructions
- `check_no_results()`: Detect end-of-pagination markers
- `fetch_and_process_page()`: Retrieve, extract, validate, and deduplicate page data

### 5. Data Utilities (`utils/data_utils.py`)
**Purpose**: Process and persist extracted data  
**Key Functions**:
- `is_complete_venue()`: Validate presence of required fields
- `is_duplicate_venue()`: Check against seen venue names
- `save_venues_to_csv()`: Export validated venues to CSV format

---

## High-Level Application Flow

### Initialization Phase
1. Load environment variables from `.env` (Groq API key)
2. Read configuration from `config.py`
3. Initialize browser configuration (Chromium, headless mode)
4. Set up LLM extraction strategy (DeepSeek model via Groq)
5. Create async web crawler session

### Crawling Phase (Loop)
1. Construct URL with current page number
2. Check for "No Results Found" message
   - If found → Exit loop
   - If not found → Continue
3. Fetch page with CSS selector and LLM extraction
4. Parse extracted JSON content
5. Iterate through extracted venues:
   - Remove spurious `error=false` flags
   - Validate required fields
   - Check for duplicates by name
   - Add valid venues to collection
6. Increment page number
7. Wait 2 seconds (rate limiting)
8. Repeat until no more results

### Output Phase
1. Check if any venues were collected
2. Write all venues to `complete_venues.csv`
3. Display LLM usage statistics (tokens, cost, etc.)
4. Log completion summary

---

## Data Flow Diagram (High-Level)

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       v
┌──────────────────────┐
│  Load Config & .env  │
└──────┬───────────────┘
       │
       v
┌─────────────────────────────┐
│  Init Browser & LLM Setup   │
└──────┬──────────────────────┘
       │
       v
┌─────────────────────────────┐
│  Open Async Crawler Session │
└──────┬──────────────────────┘
       │
       v
┌──────────────────────────────┐
│  Construct URL (page=N)      │
└──────┬───────────────────────┘
       │
       v
┌─────────────────────────────┐
│  Check "No Results Found"?  │
└──────┬───────────────────┬──┘
       │ No                │ Yes
       v                   v
┌──────────────────┐   ┌──────────────┐
│  Extract with    │   │  Exit Loop   │
│  LLM Strategy    │   └──────┬───────┘
└──────┬───────────┘          │
       │                      │
       v                      │
┌──────────────────┐          │
│  Parse JSON      │          │
└──────┬───────────┘          │
       │                      │
       v                      │
┌──────────────────────────┐  │
│  For Each Venue:         │  │
│   - Validate fields      │  │
│   - Check duplicates     │  │
│   - Add to collection    │  │
└──────┬───────────────────┘  │
       │                      │
       v                      │
┌──────────────────┐          │
│  page_number++   │          │
└──────┬───────────┘          │
       │                      │
       v                      │
┌──────────────────┐          │
│  Sleep 2 sec     │          │
└──────┬───────────┘          │
       │                      │
       └──────────────────────┘
       │
       v
┌────────────────────────────┐
│  Write complete_venues.csv │
└──────┬─────────────────────┘
       │
       v
┌────────────────────────────┐
│  Show LLM Usage Stats      │
└──────┬─────────────────────┘
       │
       v
┌──────────────┐
│     DONE     │
└──────────────┘
```

---

## Roadmap & Milestones

### Phase 1: MVP (Current) ✅
**Status**: Complete  
**Features**:
- ✅ Async web crawling with Crawl4AI
- ✅ LLM-powered data extraction
- ✅ Pydantic schema validation
- ✅ Pagination handling
- ✅ Duplicate detection by venue name
- ✅ CSV export
- ✅ Basic error handling

**Limitations**:
- Single target URL
- Print-based logging
- Fixed CSS selector
- Name-only deduplication
- No retry logic

---

### Phase 2: Reliability & Observability 🔄
**Target**: Enhanced production readiness  
**Planned Features**:
- [ ] Structured logging (Python `logging` module)
- [ ] Retry logic with exponential backoff
- [ ] Per-page metrics (duration, success rate)
- [ ] Error categorization and reporting
- [ ] Progress bars for user feedback
- [ ] Health checks and monitoring hooks
- [ ] Configurable timeout settings

**Benefits**:
- Better debugging and troubleshooting
- Resilience to transient failures
- Operational visibility

---

### Phase 3: Data Quality & Validation 📊
**Target**: Improved accuracy and consistency  
**Planned Features**:
- [ ] Enhanced venue deduplication (fuzzy matching, address comparison)
- [ ] Price normalization and parsing (extract numeric values, currency)
- [ ] Capacity normalization (handle ranges, multiple values)
- [ ] Rating validation (ensure 0-5 scale)
- [ ] Description quality checks (min/max length, language detection)
- [ ] Schema versioning for data evolution
- [ ] Custom validation rules per field

**Benefits**:
- Higher quality output data
- Easier downstream analysis
- Reduced manual cleanup

---

### Phase 4: Scale & Extensibility 🚀
**Target**: Multi-source, high-volume crawling  
**Planned Features**:
- [ ] Multi-category support (multiple venue types)
- [ ] Multi-location support (cities, regions, countries)
- [ ] Parallel page crawling with rate limiting
- [ ] Database storage (PostgreSQL, MongoDB) as alternative to CSV
- [ ] JSON output option
- [ ] Incremental updates (only fetch new/changed venues)
- [ ] Configurable LLM providers (OpenAI, Anthropic, local models)
- [ ] Plugin architecture for custom extractors

**Benefits**:
- Handle larger datasets
- Flexibility for different use cases
- Reusable across projects

---

### Phase 5: Intelligence & Enrichment 🧠
**Target**: Add analytical capabilities  
**Planned Features**:
- [ ] Sentiment analysis on reviews
- [ ] Category classification (luxury, budget, outdoor, etc.)
- [ ] Price prediction models
- [ ] Venue recommendation engine
- [ ] Geographic clustering and mapping
- [ ] Trend analysis over time
- [ ] Integration with external data sources (Google Places, Yelp)

**Benefits**:
- Transform raw data into insights
- Support decision-making workflows
- Create competitive intelligence

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    User / Scheduler                      │
└───────────────────────┬─────────────────────────────────┘
                        │
                        v
┌─────────────────────────────────────────────────────────┐
│                     main.py                              │
│  (Orchestrator: manages crawl loop, state, output)       │
└───────┬──────────────────────────────────┬──────────────┘
        │                                  │
        v                                  v
┌─────────────────────┐          ┌──────────────────────┐
│   config.py         │          │   .env               │
│   (Settings)        │          │   (Secrets)          │
└─────────────────────┘          └──────────────────────┘
        │
        v
┌─────────────────────────────────────────────────────────┐
│              utils/scraper_utils.py                      │
│  - Browser config                                        │
│  - LLM extraction strategy                               │
│  - Page fetch & process logic                            │
└───────┬─────────────────────────────────────┬───────────┘
        │                                     │
        v                                     v
┌─────────────────────┐            ┌────────────────────┐
│   Crawl4AI          │            │  Groq API          │
│   (Web Crawler)     │            │  (LLM Provider)    │
└─────────┬───────────┘            └────────┬───────────┘
          │                                 │
          v                                 v
┌─────────────────────┐            ┌────────────────────┐
│  Target Website     │            │  DeepSeek Model    │
│  (theknot.com)      │            │  (R1 Distill 70B)  │
└─────────────────────┘            └────────────────────┘
        │
        v
┌─────────────────────────────────────────────────────────┐
│              models/venue.py                             │
│  (Pydantic schema for validation)                        │
└───────────────────────────┬─────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────┐
│              utils/data_utils.py                         │
│  - Validation (completeness, deduplication)              │
│  - CSV export                                            │
└───────────────────────────┬─────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────┐
│              complete_venues.csv                         │
│  (Final output)                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Dependencies & External Services

### Python Packages
| Package | Purpose | Version (Current) | Notes |
|---------|---------|-------------------|-------|
| Crawl4AI | Async web crawling framework | Latest | Core crawler engine |
| python-dotenv | Environment variable management | Latest | Load .env files |
| pydantic | Data validation & schemas | Latest | Type-safe models |

### External Services
| Service | Purpose | Cost | Required |
|---------|---------|------|----------|
| Groq API | LLM inference for extraction | Pay-per-token | Yes |
| Target Website | Data source | Free | Yes |

### System Requirements
- Python 3.10+
- Chromium browser (auto-installed by Crawl4AI)
- Network access (HTTPS)
- ~100MB disk space for dependencies

---

## Risks & Considerations

### Technical Risks
- **Website structure changes**: CSS selectors may break if target site updates layout
- **Rate limiting**: Target site may block or throttle requests
- **LLM accuracy**: Extraction quality depends on model performance and prompt engineering
- **API costs**: LLM usage can accumulate charges on large datasets
- **Browser dependencies**: Crawl4AI requires system-level browser components

### Mitigation Strategies
- Regular CSS selector validation
- Implement polite crawling (delays, user-agent headers)
- Test LLM extraction on sample pages before full runs
- Monitor API usage and set budget alerts
- Document browser setup for different platforms

### Legal & Ethical Considerations
- **Terms of Service**: Verify crawling is permitted by target website
- **robots.txt**: Respect site crawling guidelines
- **Data privacy**: Handle personal information (if any) responsibly
- **Fair use**: Don't overload target servers

---

## Success Metrics (KPIs)

### Operational Metrics
- **Crawl Success Rate**: % of pages successfully processed
- **Extraction Accuracy**: % of venues with complete data
- **Deduplication Rate**: % of duplicates caught
- **Throughput**: Venues extracted per minute
- **Error Rate**: % of failed requests or extractions

### Data Quality Metrics
- **Field Completeness**: % of required fields populated
- **Data Consistency**: Variance in field formats
- **Update Frequency**: How often data is refreshed

### Cost Metrics
- **LLM Token Usage**: Tokens consumed per venue
- **Cost per Venue**: API charges per extracted record
- **Time per Page**: Average crawl duration

---

## Contributing & Development

### Code Standards
- Follow PEP 8 style guidelines
- Type hints for all function signatures
- Docstrings for modules and functions
- Keep functions small and focused

### Testing Strategy (Future)
- Unit tests for data validation logic
- Integration tests for crawler workflows
- Mock LLM responses for predictable testing
- Sample fixture data for edge cases

### Documentation
- Update README.MD for user-facing changes
- Maintain inline code comments
- Document configuration options
- Version change logs

---

## Contact & Support

For questions, issues, or contributions:
- Check the README.MD for basic usage
- Review SET_UP.md for environment setup
- See generate_flow_chart.md for visual system understanding
- File issues in the project repository (if applicable)

---

**Last Updated**: January 2026
