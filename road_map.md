# road_map.md

## Vision & Goals

### Mission
Automate the extraction of news stories from Binghamton University's website and generate engaging LinkedIn posts using AI, enabling efficient content distribution for university communications and social media management.

### Key Objectives
1. **Automation**: Replace manual content curation with AI-powered scraping and post generation
2. **Intelligence**: Leverage LLM (Llama 3.3 70B) for story extraction and LinkedIn content creation
3. **Quality**: Ensure completeness with validation and deduplication
4. **Engagement**: Generate professional, hashtag-optimized LinkedIn posts automatically
5. **Usability**: Provide clean CSV output ready for social media scheduling tools

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
**Purpose**: Centralized settings for scraper behavior  
**Key Settings**:
- `BASE_URL`: Binghamton University News homepage
- `CSS_SELECTOR`: DOM element selector for news story containers
- `REQUIRED_KEYS`: Fields necessary for a complete news story record

### 3. Data Models (`models/venue.py`)
**Purpose**: Define structured schema for news story data  
**Features**:
- Pydantic BaseModel for type validation
- Schema generation for LLM extraction
- Fields: story_title, story_category, story_summary, story_LinkedIn_post

### 4. Scraper Utilities (`utils/scraper_utils.py`)
**Purpose**: Configure and execute web crawling and AI content generation  
**Key Functions**:
- `get_browser_config()`: Browser settings with stealth headers for bot evasion
- `get_llm_strategy()`: LLM provider setup (Groq/Llama 3.3 70B) with LinkedIn post generation instructions
- `check_no_results()`: Detect end-of-pagination markers
- `fetch_and_process_page()`: Retrieve, extract stories, generate LinkedIn posts, validate, and deduplicate

### 5. Data Utilities (`utils/data_utils.py`)
**Purpose**: Process and persist extracted news data  
**Key Functions**:
- `is_complete_venue()`: Validate presence of all required story fields
- `is_duplicate_venue()`: Check against seen story titles
- `save_venues_to_csv()`: Export validated news stories with LinkedIn posts to CSV format

---

## High-Level Application Flow

### Initialization Phase
1. Load environment variables from `.env` (Groq API key)
2. Read configuration from `config.py`
3. Initialize browser configuration with stealth headers
4. Set up LLM extraction strategy (Llama 3.3 70B via Groq) with LinkedIn post generation
5. Create async web crawler session

### Scraping Phase
1. Construct Binghamton News URL
2. Check for "No Results Found" message
   - If found → Exit
   - If not found → Continue
3. Fetch page with CSS selector and LLM extraction
4. LLM extracts and generates:
   - Story title, category, and summary
   - AI-generated LinkedIn post with hashtags (100-150 words)
5. Parse extracted JSON content
6. Iterate through extracted stories:
   - Remove spurious `error=false` flags
   - Validate all required fields
   - Check for duplicates by story title
   - Add valid stories to collection
7. Wait 2 seconds (rate limiting) if pagination exists

### Output Phase
1. Check if any news stories were collected
2. Write all stories to `binghamton_news_stories.csv`
3. Display LLM usage statistics (tokens, cost, etc.)
4. Log completion summary with story count

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

### Phase 1: Binghamton News Scraper (Current) ✅
**Status**: Complete  
**Features**:
- ✅ Async web crawling with Crawl4AI
- ✅ LLM-powered news extraction (Llama 3.3 70B)
- ✅ AI-generated LinkedIn posts with hashtags
- ✅ Pydantic schema validation
- ✅ Story categorization (Arts & Culture, Health, Science & Technology, etc.)
- ✅ Duplicate detection by story title
- ✅ CSV export with complete story data
- ✅ Comprehensive documentation (SET_UP.md, road_map.md, flow charts)
- ✅ Bot evasion with stealth headers

**Current Capabilities**:
- Extracts 13+ stories per run from Binghamton University News
- Generates professional LinkedIn posts automatically
- Ready-to-use CSV output for social media scheduling

---

### Phase 2: Multi-Source & Scheduling 🔄
**Target**: Expand to multiple news sources and automate posting  
**Planned Features**:
- [ ] Multi-university support (SUNY schools, Ivy League, etc.)
- [ ] Scheduled scraping (daily, weekly runs)
- [ ] Direct LinkedIn API integration for posting
- [ ] Email notifications with story summaries
- [ ] Database storage (SQLite/PostgreSQL) for history tracking
- [ ] Web dashboard for monitoring and management

**Benefits**:
- Centralized news aggregation across multiple sources
- Fully automated content pipeline
- Historical tracking and analytics

---

### Phase 3: AI Enhancement & Analytics 📊
**Target**: Smarter content generation and insights  
**Planned Features**:
- [ ] Sentiment analysis on news stories
- [ ] Trending topics detection across universities
- [ ] Multiple LinkedIn post variations (casual, professional, academic)
- [ ] Automatic image generation for posts (DALL-E, Stable Diffusion)
- [ ] Story engagement prediction (which stories will perform best)
- [ ] A/B testing for post formats
- [ ] Analytics dashboard with story performance metrics

**Benefits**:
- More engaging social media content
- Data-driven content strategy
- Better understanding of audience preferences

---

### Phase 4: Enterprise Features 🚀
**Target**: Production-ready for university communications teams  
**Planned Features**:
- [ ] Multi-user authentication and permissions
- [ ] Content approval workflow (draft → review → publish)
- [ ] Template library for different post styles
- [ ] Brand voice customization per institution
- [ ] Compliance checks (verify information, fact-checking)
- [ ] Integration with content calendars (Hootsuite, Buffer)
- [ ] Mobile app for on-the-go management
- [ ] API for third-party integrations

**Benefits**:
- Enterprise-grade content management
- Team collaboration features
- Scalable for multiple departments

---

### Phase 5: Intelligence & Innovation 🧠
**Target**: Advanced AI capabilities  
**Planned Features**:
- [ ] Multi-lingual support (translate stories and posts)
- [ ] Video script generation for TikTok/Instagram Reels
- [ ] Podcast episode notes from news stories
- [ ] Newsletter generation with story roundups
- [ ] Press release drafting from news stories
- [ ] Alumni engagement content (personalized by graduation year/major)
- [ ] Chatbot for answering questions about news stories
- [ ] Predictive content recommendations

**Benefits**:
- Multi-channel content distribution
- Personalized engagement strategies
- AI-powered communications suite

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
