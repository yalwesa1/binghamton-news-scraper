import json
import os
from typing import List, Set, Tuple

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMExtractionStrategy,
)

from models.venue import Venue
from utils.data_utils import is_complete_venue, is_duplicate_venue


def get_browser_config() -> BrowserConfig:
    """
    Returns the browser configuration for the crawler with stealth settings.

    Returns:
        BrowserConfig: The configuration settings for the browser.
    """
    # https://docs.crawl4ai.com/core/browser-crawler-config/
    return BrowserConfig(
        browser_type="chromium",  # Type of browser to simulate
        headless=False,  # Whether to run in headless mode (no GUI)
        verbose=True,  # Enable verbose logging
        # Stealth settings to avoid bot detection
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        },
        viewport_width=1920,
        viewport_height=1080,
    )


def get_llm_strategy() -> LLMExtractionStrategy:
    """
    Returns the configuration for the language model extraction strategy.

    Returns:
        LLMExtractionStrategy: The settings for how to extract data using LLM.
    """
    # https://docs.crawl4ai.com/api/strategies/#llmextractionstrategy
    return LLMExtractionStrategy(
        provider="groq/llama-3.3-70b-versatile",  # Name of the LLM provider (updated from deprecated model)
        api_token=os.getenv("GROQ_API_KEY"),  # API token for authentication
        schema=Venue.model_json_schema(),  # JSON schema of the data model
        extraction_type="schema",  # Type of extraction to perform
        instruction=(
            "Extract all news stories from the Binghamton University news page. For each story, provide:\n"
            "1. story_title: The headline or title of the news story\n"
            "2. story_category: The category or topic (e.g., 'Arts & Culture', 'Athletics', 'Business', 'Health', 'Science & Technology', 'Campus News', etc.)\n"
            "3. story_summary: A brief 2-3 sentence summary of the story\n"
            "4. story_url: The complete URL link to the full story. Must be a valid URL starting with https://. "
            "If you find a relative URL (e.g., /news/story), convert it to absolute by adding https://www.binghamton.edu prefix.\n"
            "5. story_LinkedIn_post: Create an engaging LinkedIn post (100-150 words) about this story that would be suitable for sharing on social media. "
            "Include relevant hashtags and make it professional yet engaging. "
            "At the END of the post, add a new line and include: '🔗 Read more: [story_url]' where [story_url] is the actual URL from field 4.\n\n"
            "Return as many news stories as you can find in the content."
        ),  # Instructions for the LLM
        input_format="markdown",  # Format of the input content
        verbose=True,  # Enable verbose logging
    )


async def check_no_results(
    crawler: AsyncWebCrawler,
    url: str,
    session_id: str,
) -> bool:
    """
    Checks if the "No Results Found" message is present on the page.

    Args:
        crawler (AsyncWebCrawler): The web crawler instance.
        url (str): The URL to check.
        session_id (str): The session identifier.

    Returns:
        bool: True if "No Results Found" message is found, False otherwise.
    """
    # Fetch the page without any CSS selector or extraction strategy
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            session_id=session_id,
            wait_until="networkidle",  # Wait until network is idle
            page_timeout=60000,  # Increase timeout to 60 seconds
            delay_before_return_html=3.0,  # Wait 3 seconds after page load
        ),
    )

    if result.success:
        if "No Results Found" in result.cleaned_html:
            return True
    else:
        print(
            f"Error fetching page for 'No Results Found' check: {result.error_message}"
        )

    return False


async def fetch_and_process_page(
    crawler: AsyncWebCrawler,
    page_number: int,
    base_url: str,
    css_selector: str,
    llm_strategy: LLMExtractionStrategy,
    session_id: str,
    required_keys: List[str],
    seen_names: Set[str],
) -> Tuple[List[dict], bool]:
    """
    Fetches and processes a single page of venue data.

    Args:
        crawler (AsyncWebCrawler): The web crawler instance.
        page_number (int): The page number to fetch.
        base_url (str): The base URL of the website.
        css_selector (str): The CSS selector to target the content.
        llm_strategy (LLMExtractionStrategy): The LLM extraction strategy.
        session_id (str): The session identifier.
        required_keys (List[str]): List of required keys in the venue data.
        seen_names (Set[str]): Set of venue names that have already been seen.

    Returns:
        Tuple[List[dict], bool]:
            - List[dict]: A list of processed venues from the page.
            - bool: A flag indicating if the "No Results Found" message was encountered.
    """
    url = f"{base_url}?page={page_number}"
    print(f"Loading page {page_number}...")

    # Check if "No Results Found" message is present
    no_results = await check_no_results(crawler, url, session_id)
    if no_results:
        return [], True  # No more results, signal to stop crawling

    # Fetch page content with the extraction strategy
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,  # Do not use cached data
            extraction_strategy=llm_strategy,  # Strategy for data extraction
            css_selector=css_selector,  # Target specific content on the page
            session_id=session_id,  # Unique session ID for the crawl
            wait_until="networkidle",  # Wait until network is idle
            page_timeout=60000,  # Increase timeout to 60 seconds
            delay_before_return_html=3.0,  # Wait 3 seconds after page load
        ),
    )

    if not (result.success and result.extracted_content):
        print(f"Error fetching page {page_number}: {result.error_message}")
        return [], False

    # Parse extracted content
    extracted_data = json.loads(result.extracted_content)
    if not extracted_data:
        print(f"No news stories found on page {page_number}.")
        return [], False

    # Handle cases where LLM returns data in a nested 'content' array
    if isinstance(extracted_data, list) and len(extracted_data) > 0:
        if isinstance(extracted_data[0], dict) and 'content' in extracted_data[0]:
            # Extract and parse JSON strings from content array
            content_array = extracted_data[0]['content']
            parsed_stories = []
            for json_str in content_array:
                try:
                    # Clean the JSON string (remove control characters that break JSON parsing)
                    # Replace literal \n in strings with space
                    cleaned_json = json_str.replace('\n    ', ' ').replace('\n', ' ')
                    story = json.loads(cleaned_json)
                    parsed_stories.append(story)
                except json.JSONDecodeError as e:
                    print(f"Warning: Could not parse story JSON: {e}")
                    # Try to parse with strict=False as fallback
                    try:
                        story = json.loads(json_str, strict=False)
                        parsed_stories.append(story)
                    except:
                        continue
            extracted_data = parsed_stories
            print(f"Parsed {len(extracted_data)} stories from content array")

    # After parsing extracted content
    print("Extracted data:", extracted_data)

    # Process news stories
    complete_venues = []
    for venue in extracted_data:
        # Debugging: Print each story to understand its structure
        print("Processing story:", venue)

        # Ignore the 'error' key if it's False
        if venue.get("error") is False:
            venue.pop("error", None)  # Remove the 'error' key if it's False

        if not is_complete_venue(venue, required_keys):
            continue  # Skip incomplete stories

        # Check for duplicates using story_title
        story_title = venue.get("story_title", "")
        if is_duplicate_venue(story_title, seen_names):
            print(f"Duplicate story '{story_title}' found. Skipping.")
            continue  # Skip duplicate stories

        # Add story to the list
        seen_names.add(story_title)
        complete_venues.append(venue)

    if not complete_venues:
        print(f"No complete news stories found on page {page_number}.")
        return [], False

    print(f"Extracted {len(complete_venues)} news stories from page {page_number}.")
    return complete_venues, False  # Continue crawling
