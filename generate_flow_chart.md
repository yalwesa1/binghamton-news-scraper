# generate_flow_chart.md

This document contains Mermaid diagrams to visualize the project flow, architecture, and data pipelines of the DeepSeek AI Web Crawler. View this file in **Markdown Preview** (or on GitHub/GitLab) to see the Mermaid charts rendered here.

---

## 1. Overall System Architecture

```mermaid
graph TB
    subgraph User
        A[User/Scheduler]
    end
    
    subgraph Configuration
        B[config.py<br/>BASE_URL, CSS_SELECTOR, REQUIRED_KEYS]
        C[.env<br/>GROQ_API_KEY]
    end
    
    subgraph Core Application
        D[main.py<br/>Orchestrator]
    end
    
    subgraph Utilities
        E[scraper_utils.py<br/>Browser & LLM Config]
        F[data_utils.py<br/>Validation & Export]
    end
    
    subgraph Data Models
        G[venue.py<br/>Pydantic Schema]
    end
    
    subgraph External Services
        H[Crawl4AI<br/>Async Crawler]
        I[Groq API<br/>LLM Provider]
        J[Target Website<br/>theknot.com]
    end
    
    subgraph Output
        K[complete_venues.csv]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    D --> F
    E --> H
    E --> I
    H --> J
    G --> E
    G --> F
    F --> K
```

---

## 2. Main Application Flow (Detailed)

```mermaid
flowchart TD
    Start([Start]) --> LoadEnv[Load .env file<br/>python-dotenv]
    LoadEnv --> LoadConfig[Load config.py<br/>BASE_URL, CSS_SELECTOR, REQUIRED_KEYS]
    LoadConfig --> InitBrowser[Initialize BrowserConfig<br/>browser_type: chromium<br/>headless: False<br/>verbose: True]
    InitBrowser --> InitLLM[Initialize LLMExtractionStrategy<br/>provider: groq/deepseek-r1-distill-llama-70b<br/>schema: Venue model<br/>extraction_type: schema]
    InitLLM --> CreateSession[Create AsyncWebCrawler session]
    CreateSession --> InitVars[Initialize state variables<br/>page_number = 1<br/>all_venues = empty list<br/>seen_names = set]
    
    InitVars --> BuildURL[Build URL with page number<br/>BASE_URL?page=N]
    BuildURL --> CheckNoResults{Check for<br/>'No Results Found'<br/>message}
    
    CheckNoResults -->|Found| EndLoop[Exit crawl loop]
    CheckNoResults -->|Not found| FetchPage[Fetch page with arun<br/>css_selector + llm_strategy]
    
    FetchPage --> FetchSuccess{Fetch<br/>successful?}
    FetchSuccess -->|No| LogError[Log error message]
    LogError --> EndLoop
    
    FetchSuccess -->|Yes| ParseJSON[Parse extracted_content<br/>as JSON]
    ParseJSON --> HasData{Has venue<br/>data?}
    HasData -->|No| LogNoVenues[Log 'No venues found']
    LogNoVenues --> EndLoop
    
    HasData -->|Yes| IterateVenues[Iterate through extracted venues]
    IterateVenues --> RemoveError[Remove error=false flag<br/>if present]
    RemoveError --> CheckComplete{Has all<br/>required keys?}
    
    CheckComplete -->|No| NextVenue[Skip to next venue]
    CheckComplete -->|Yes| CheckDupe{Is venue name<br/>a duplicate?}
    
    CheckDupe -->|Yes| LogDupe[Log duplicate found]
    LogDupe --> NextVenue
    CheckDupe -->|No| AddVenue[Add venue to list<br/>Add name to seen_names set]
    
    AddVenue --> NextVenue
    NextVenue --> MoreVenues{More venues<br/>on page?}
    MoreVenues -->|Yes| RemoveError
    MoreVenues -->|No| LogCount[Log venue count for page]
    
    LogCount --> IncrPage[Increment page_number]
    IncrPage --> Sleep[Sleep 2 seconds<br/>Rate limiting]
    Sleep --> BuildURL
    
    EndLoop --> HasVenues{Any venues<br/>collected?}
    HasVenues -->|Yes| SaveCSV[Save to complete_venues.csv<br/>Use CSV DictWriter]
    HasVenues -->|No| LogNoResults[Log 'No venues found']
    
    SaveCSV --> ShowStats[Display LLM usage statistics<br/>llm_strategy.show_usage]
    LogNoResults --> ShowStats
    ShowStats --> End([End])
```

---

## 3. Data Extraction Pipeline

```mermaid
flowchart LR
    subgraph Web Layer
        A[Target Webpage<br/>HTML + CSS]
    end
    
    subgraph Crawl Layer
        B[AsyncWebCrawler<br/>Fetch page]
        C[CSS Selector<br/>Filter elements]
        D[Extract HTML content]
    end
    
    subgraph LLM Layer
        E[LLMExtractionStrategy<br/>Send to Groq API]
        F[DeepSeek R1 Model<br/>Process content]
        G[Return JSON<br/>structured data]
    end
    
    subgraph Validation Layer
        H[Parse JSON]
        I[Check required keys<br/>name, price, location, etc.]
        J[Check for duplicates<br/>by venue name]
    end
    
    subgraph Storage Layer
        K[Add to collection<br/>all_venues list]
        L[Export to CSV<br/>complete_venues.csv]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I -->|Valid| J
    I -->|Invalid| M[Discard]
    J -->|Unique| K
    J -->|Duplicate| M
    K --> L
```

---

## 4. Venue Data Model Structure

```mermaid
classDiagram
    class Venue {
        +str name
        +str location
        +str price
        +str capacity
        +float rating
        +int reviews
        +str description
        +model_json_schema()
        +model_fields()
    }
    
    class BaseModel {
        <<pydantic>>
        +model_json_schema()
        +model_validate()
    }
    
    BaseModel <|-- Venue
```

---

## 5. Configuration Flow

```mermaid
flowchart TD
    A[config.py] --> B[BASE_URL<br/>Target website]
    A --> C[CSS_SELECTOR<br/>Element selector]
    A --> D[REQUIRED_KEYS<br/>Field validation list]
    
    E[.env] --> F[GROQ_API_KEY<br/>API authentication]
    
    B --> G[scraper_utils.py<br/>fetch_and_process_page]
    C --> G
    D --> H[data_utils.py<br/>is_complete_venue]
    F --> I[scraper_utils.py<br/>get_llm_strategy]
    
    G --> J[main.py<br/>crawl_venues]
    H --> J
    I --> J
```

---

## 6. Page Processing Sequence

```mermaid
sequenceDiagram
    participant M as main.py
    participant S as scraper_utils.py
    participant C as Crawl4AI
    participant W as Website
    participant G as Groq API
    participant D as data_utils.py
    
    M->>S: fetch_and_process_page(page_number)
    S->>S: Build URL with page param
    S->>C: check_no_results(url)
    C->>W: Fetch page (no CSS selector)
    W-->>C: Return HTML
    C->>C: Check for "No Results Found"
    C-->>S: Return boolean
    
    alt No Results Found
        S-->>M: Return ([], True)
    else Results Available
        S->>C: arun(url, css_selector, llm_strategy)
        C->>W: Fetch page with selector
        W-->>C: Return filtered HTML
        C->>G: Send content for extraction
        G->>G: Process with DeepSeek model
        G-->>C: Return JSON data
        C-->>S: Return result object
        
        S->>S: Parse extracted_content
        loop For each venue
            S->>S: Remove error flag
            S->>D: is_complete_venue(venue)
            D-->>S: Boolean result
            S->>D: is_duplicate_venue(name, seen_names)
            D-->>S: Boolean result
            alt Valid & Unique
                S->>S: Add to complete_venues
                S->>S: Add name to seen_names
            end
        end
        S-->>M: Return (venues, False)
    end
```

---

## 7. Error Handling Flow

```mermaid
flowchart TD
    A[Operation Start] --> B{Operation<br/>Type}
    
    B -->|Fetch Page| C[AsyncWebCrawler.arun]
    B -->|Parse JSON| D[json.loads]
    B -->|Check Results| E[Check HTML content]
    
    C --> F{Success?}
    F -->|No| G[Log error_message<br/>from result object]
    F -->|Yes| H[Continue processing]
    
    D --> I{Valid JSON?}
    I -->|No| J[Log parse error<br/>Return empty list]
    I -->|Yes| H
    
    E --> K{Contains 'No Results Found'?}
    K -->|Yes| L[Return stop signal]
    K -->|No| H
    
    G --> M[Return empty results]
    J --> M
    L --> N[Exit crawl loop]
    M --> N
    H --> O[Process data]
```

---

## 8. State Management

```mermaid
stateDiagram-v2
    [*] --> Initializing: Start application
    
    Initializing --> Ready: Configs loaded
    Ready --> Crawling: Start crawl loop
    
    state Crawling {
        [*] --> FetchingPage
        FetchingPage --> Extracting: Page loaded
        Extracting --> Validating: Data extracted
        Validating --> FetchingPage: More venues on page
        Validating --> NextPage: Page complete
        NextPage --> FetchingPage: More pages available
        NextPage --> [*]: No more pages
    }
    
    Crawling --> Saving: All pages processed
    Crawling --> Error: Critical failure
    
    Saving --> Reporting: CSV written
    Reporting --> [*]: Complete
    
    Error --> [*]: Terminate
```

---

## 9. Module Dependency Graph

```mermaid
graph TD
    A[main.py] --> B[config.py]
    A --> C[utils/scraper_utils.py]
    A --> D[utils/data_utils.py]
    A --> E[python-dotenv]
    A --> F[crawl4ai.AsyncWebCrawler]
    
    C --> G[models/venue.py]
    C --> H[crawl4ai.BrowserConfig]
    C --> I[crawl4ai.CrawlerRunConfig]
    C --> J[crawl4ai.LLMExtractionStrategy]
    C --> D
    
    D --> G
    
    G --> K[pydantic.BaseModel]
    
    style A fill:#e1f5ff
    style G fill:#fff3cd
    style C fill:#d4edda
    style D fill:#d4edda
```

---

## 10. LLM Extraction Strategy Workflow

```mermaid
flowchart TD
    A[Initialize LLMExtractionStrategy] --> B[Set provider:<br/>groq/deepseek-r1-distill-llama-70b]
    B --> C[Load API token from env]
    C --> D[Generate JSON schema<br/>from Venue model]
    D --> E[Define extraction instructions<br/>Extract venue fields]
    E --> F[Set input_format: markdown]
    
    F --> G[Strategy Ready]
    
    G --> H[Receive page content<br/>from Crawl4AI]
    H --> I[Send to Groq API:<br/>- Content<br/>- Schema<br/>- Instructions]
    I --> J[DeepSeek R1 processes<br/>natural language → JSON]
    J --> K{Valid JSON?}
    
    K -->|Yes| L[Return extracted venues]
    K -->|No| M[Return error]
    
    L --> N[Track usage statistics<br/>tokens, cost, latency]
    M --> N
    N --> O[show_usage method<br/>displays stats]
```

---

## 11. CSV Export Process

```mermaid
flowchart LR
    A[all_venues list] --> B[Check if empty]
    B -->|Empty| C[Log 'No venues to save'<br/>Return]
    B -->|Has data| D[Get field names<br/>from Venue.model_fields]
    
    D --> E[Open CSV file<br/>complete_venues.csv<br/>mode: write, encoding: utf-8]
    E --> F[Create DictWriter<br/>with field names]
    F --> G[Write header row]
    G --> H[Write all venue rows<br/>DictWriter.writerows]
    H --> I[Close file]
    I --> J[Log success message<br/>with venue count]
```

---

## 12. Pagination & Rate Limiting

```mermaid
flowchart TD
    A[Start Loop] --> B[page_number = 1]
    B --> C[Construct URL<br/>BASE_URL?page=N]
    C --> D[Fetch and process page]
    D --> E{No Results<br/>Found?}
    
    E -->|Yes| F[Break loop]
    E -->|No| G{Venues<br/>extracted?}
    
    G -->|No| F
    G -->|Yes| H[Add venues to collection]
    H --> I[Increment page_number]
    I --> J[asyncio.sleep 2 seconds<br/>⏰ Rate Limiting]
    J --> C
    
    F --> K[End Loop]
    
    style J fill:#ffe6e6
```

---

## 13. Deduplication Strategy

```mermaid
flowchart TD
    A[Initialize seen_names<br/>as empty set] --> B[Process venue from page]
    B --> C[Extract venue name]
    C --> D{Is name in<br/>seen_names?}
    
    D -->|Yes| E[Log 'Duplicate venue found'<br/>with venue name]
    E --> F[Skip this venue<br/>Continue to next]
    
    D -->|No| G[Add name to seen_names]
    G --> H[Add venue to all_venues list]
    H --> I[Continue to next venue]
    
    F --> J[Next iteration]
    I --> J
    
    style D fill:#fff3cd
```

---

## 14. Browser Configuration Options

```mermaid
graph TD
    A[get_browser_config] --> B[BrowserConfig Object]
    
    B --> C[browser_type: chromium<br/>🌐 Browser engine]
    B --> D[headless: False<br/>👁️ Show browser window]
    B --> E[verbose: True<br/>📝 Enable detailed logging]
    
    C --> F[Used by AsyncWebCrawler]
    D --> F
    E --> F
    
    style B fill:#e1f5ff
```

---

## 15. Complete End-to-End Flow (Simplified)

```mermaid
flowchart TD
    A[👤 User runs<br/>python main.py] --> B[🔑 Load GROQ_API_KEY<br/>from .env]
    B --> C[⚙️ Load config<br/>URL, selector, keys]
    C --> D[🌐 Open browser session<br/>Chromium via Crawl4AI]
    D --> E[📄 Fetch page 1]
    
    E --> F[🤖 Extract venues<br/>via LLM]
    F --> G[✅ Validate data<br/>required fields]
    G --> H[🔍 Check duplicates]
    H --> I[💾 Store venues]
    
    I --> J{More pages?}
    J -->|Yes| K[⏳ Wait 2 sec]
    K --> L[📄 Fetch next page]
    L --> F
    
    J -->|No| M[📊 Write CSV]
    M --> N[📈 Show stats]
    N --> O[✨ Done!]
    
    style A fill:#d4edda
    style O fill:#d4edda
```

---

## How to Use These Diagrams

### Viewing Options
1. **GitHub/GitLab**: These platforms render Mermaid automatically in Markdown files
2. **VS Code**: Install the "Markdown Preview Mermaid Support" extension
3. **Mermaid Live Editor**: Copy diagram code to https://mermaid.live/
4. **Documentation Sites**: Hugo, MkDocs, Docusaurus support Mermaid natively

### Exporting Diagrams
To export as images:
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Generate PNG from markdown
mmdc -i generate_flow_chart.md -o flow_chart.png

# Or generate SVG
mmdc -i generate_flow_chart.md -o flow_chart.svg
```

### Editing Diagrams
- Modify the text within \`\`\`mermaid blocks
- Follow Mermaid syntax: https://mermaid.js.org/intro/
- Use Mermaid Live Editor for real-time preview while editing

---

## Diagram Legend

### Common Shapes
- **Rectangle** `[text]`: Process or component
- **Diamond** `{text}`: Decision point
- **Rounded Rectangle** `([text])`: Start/End
- **Cylinder** (in some diagrams): Database/storage
- **Circle**: Connection point

### Common Arrows
- **Solid arrow** `-->`: Flow direction
- **Labeled arrow** `-->|label|`: Conditional flow
- **Dashed arrow** `-.->`: Optional or async flow

### Color Coding (when used)
- **Blue** `#e1f5ff`: Main application components
- **Green** `#d4edda`: Utility modules
- **Yellow** `#fff3cd`: Data models
- **Red** `#ffe6e6`: Critical operations (rate limiting, errors)

---

## Extending These Diagrams

When adding new features, update the relevant diagrams:

1. **New module/component**: Update Architecture diagram (#1) and Dependency Graph (#9)
2. **New data flow**: Update Data Extraction Pipeline (#3)
3. **New configuration**: Update Configuration Flow (#5)
4. **New error handling**: Update Error Handling Flow (#7)
5. **UI/workflow changes**: Update Main Application Flow (#2)

Keep diagrams in sync with code changes for accurate documentation!

---

**Last Updated**: January 2026  
**Mermaid Version**: Compatible with v9.0+
