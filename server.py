#!/usr/bin/env python3
"""
Production-ready MCP server built with FastMCP
Equivalent to the TypeScript version with tools, resources, and prompts
"""

from typing import Any, Optional
import os
import json
import requests
from dotenv import load_dotenv
from fastmcp import FastMCP
from datetime import datetime

# Load environment variables
load_dotenv()

# Server configuration
SERVER_NAME = os.getenv("SERVER_NAME", "blockza-mcp-server")
SERVER_VERSION = os.getenv("SERVER_VERSION", "1.0.0")

# Initialize FastMCP server
mcp = FastMCP(SERVER_NAME)

# ========== BLOCKZA API CLIENT ==========

class BlockzaClient:
    """Client for interacting with Blockza API"""

    BASE_URL = "https://api.blockza.io/api"
    EVENTS_URL = "https://api.blockza.io/api/events"
    PODCASTS_URL = "https://api.blockza.io/api/podcasts"
    DIRECTORY_URL = "https://api.blockza.io/api/directory"

    @staticmethod
    def filter_event_fields(event: dict[str, Any]) -> dict[str, Any]:
        """Extract only essential fields from an event to reduce payload size

        Args:
            event: Full event dictionary

        Returns:
            Filtered event with only essential fields
        """
        return {
            "_id": event.get("_id"),
            "title": event.get("title"),
            "description": event.get("description", "")[:200],  # Truncate long descriptions
            "location": event.get("location"),
            "country": event.get("country"),
            "city": event.get("city"),
            "eventStartDate": event.get("eventStartDate"),
            "eventEndDate": event.get("eventEndDate"),
            "category": event.get("category"),
            "website": event.get("website"),
            "company": event.get("company")
        }

    @staticmethod
    def filter_podcast_fields(podcast: dict[str, Any]) -> dict[str, Any]:
        """Extract only essential fields from a podcast to reduce payload size

        Args:
            podcast: Full podcast dictionary

        Returns:
            Filtered podcast with only essential fields
        """
        image = podcast.get("image", {})
        return {
            "_id": podcast.get("_id") or podcast.get("id"),
            "title": podcast.get("title"),
            "description": podcast.get("description", "")[:200],
            "shortDescription": podcast.get("shortDescription", ""),
            "slug": podcast.get("slug"),
            "category": podcast.get("category"),
            "company": podcast.get("company"),
            "image": image.get("url") if isinstance(image, dict) else None,
            "youtubeIframe": podcast.get("youtubeIframe"),
            "status": podcast.get("status"),
            "likes": podcast.get("likes", 0),
            "views": podcast.get("views", 0),
            "createdAt": podcast.get("createdAt")
        }

    @staticmethod
    def get_events(
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        category: Optional[str] = None,
        upcoming: bool = False
    ) -> list[dict[str, Any]]:
        """Fetch events from Blockza API

        Args:
            limit: Maximum number of events to return
            offset: Number of events to skip
            search: Search query for event name or description
            country: Filter by country
            city: Filter by city
            category: Filter by category
            upcoming: Only return upcoming events

        Returns:
            List of event dictionaries
        """
        try:
            url = BlockzaClient.EVENTS_URL
            params = {}

            if limit is not None:
                params["limit"] = limit
            if offset is not None:
                params["offset"] = offset
            if search:
                params["search"] = search
            if country:
                params["country"] = country
            if city:
                params["city"] = city
            if category:
                params["category"] = category
            if upcoming:
                params["upcoming"] = "true"

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            events = data if isinstance(data, list) else []

            # Filter events to reduce payload size
            filtered_events = [BlockzaClient.filter_event_fields(event) for event in events]
            return filtered_events
        except requests.exceptions.RequestException as e:
            print(f"Error fetching events: {e}")
            return []

    @staticmethod
    def get_event_by_id(event_id: str) -> dict[str, Any] | None:
        """Fetch a specific event by ID

        Args:
            event_id: The event identifier

        Returns:
            Event data dictionary or None if not found
        """
        try:
            events = BlockzaClient.get_events()
            for event in events:
                if event.get("_id") == event_id:
                    return event
            return None
        except Exception as e:
            print(f"Error fetching event by ID: {e}")
            return None

    @staticmethod
    def get_podcasts(
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search: Optional[str] = None,
        category: Optional[str] = None,
        company: Optional[str] = None,
        status: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Fetch podcasts from Blockza API

        Args:
            limit: Maximum number of podcasts to return
            offset: Number of podcasts to skip
            search: Search query for podcast title or description
            category: Filter by category
            company: Filter by company
            status: Filter by status (e.g., 'published')

        Returns:
            List of podcast dictionaries
        """
        try:
            url = BlockzaClient.PODCASTS_URL
            params = {}

            if limit is not None:
                params["limit"] = limit
            if offset is not None:
                params["offset"] = offset
            if search:
                params["search"] = search
            if category:
                params["category"] = category
            if company:
                params["company"] = company
            if status:
                params["status"] = status

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            # Handle both array and object response formats
            podcasts = data if isinstance(data, list) else (data.get("data", []) if isinstance(data, dict) else [])

            # Filter podcasts to reduce payload size
            filtered_podcasts = [BlockzaClient.filter_podcast_fields(p) for p in podcasts]
            return filtered_podcasts
        except requests.exceptions.RequestException as e:
            print(f"Error fetching podcasts: {e}")
            return []

    @staticmethod
    def get_podcast_by_id(podcast_id: str) -> dict[str, Any] | None:
        """Fetch a specific podcast by ID

        Args:
            podcast_id: The podcast identifier

        Returns:
            Podcast data dictionary or None if not found
        """
        try:
            podcasts = BlockzaClient.get_podcasts()
            for podcast in podcasts:
                if podcast.get("_id") == podcast_id or podcast.get("id") == podcast_id:
                    return podcast
            return None
        except Exception as e:
            print(f"Error fetching podcast by ID: {e}")
            return None

    @staticmethod
    def get_podcasts_by_category(category: str) -> list[dict[str, Any]]:
        """Fetch podcasts filtered by category

        Args:
            category: The category to filter by

        Returns:
            List of podcast dictionaries
        """
        return BlockzaClient.get_podcasts(category=category)

    @staticmethod
    def get_upcoming_events() -> list[dict[str, Any]]:
        """Get upcoming events

        Returns:
            List of upcoming event dictionaries
        """
        try:
            events = BlockzaClient.get_events()
            now = datetime.now()
            upcoming = []
            for event in events:
                try:
                    event_date = datetime.fromisoformat(event.get("eventStartDate", "").replace("Z", "+00:00"))
                    if event_date > now:
                        upcoming.append(event)
                except:
                    pass
            return upcoming
        except Exception as e:
            print(f"Error getting upcoming events: {e}")
            return []


# ========== TOOLS ==========

# ========== BLOCKZA EVENT TOOLS ==========

@mcp.tool()
def list_events(
    limit: int = 5,
    offset: int = 0,
    upcoming_only: bool = False
) -> str:
    """List blockchain events from Blockza directory

    Args:
        limit: Maximum number of events to return (default: 5, max: 20)
        offset: Number of events to skip for pagination (default: 0)
        upcoming_only: Only return upcoming events (default: False)

    Returns:
        JSON string with events data
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 20)
    events = BlockzaClient.get_events(
        limit=limit,
        offset=offset,
        upcoming=upcoming_only
    )
    return json.dumps({"events": events, "count": len(events)}, indent=2)


@mcp.tool()
def search_events(
    query: str,
    limit: int = 5,
    country: Optional[str] = None,
    city: Optional[str] = None
) -> str:
    """Search for blockchain events by name or description

    Args:
        query: Search term for event name or description
        limit: Maximum number of results (default: 5, max: 15)
        country: Filter by country (optional)
        city: Filter by city (optional)

    Returns:
        JSON string with matching events
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 15)
    events = BlockzaClient.get_events(
        search=query,
        limit=limit,
        country=country,
        city=city
    )
    return json.dumps({"events": events, "count": len(events)}, indent=2)


@mcp.tool()
def get_event_details(event_id: str) -> str:
    """Get detailed information about a specific event

    Args:
        event_id: The event identifier

    Returns:
        JSON string with event details
    """
    event = BlockzaClient.get_event_by_id(event_id)
    if event is None:
        return json.dumps({"error": "Event not found", "event": None}, indent=2)
    return json.dumps(event, indent=2)


@mcp.tool()
def get_upcoming_events(limit: int = 5) -> str:
    """Get upcoming blockchain events

    Args:
        limit: Maximum number of events to return (default: 5, max: 15)

    Returns:
        JSON string with upcoming events
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 15)
    events = BlockzaClient.get_events(
        limit=limit,
        upcoming=True
    )
    return json.dumps({"events": events, "count": len(events)}, indent=2)


@mcp.tool()
def search_events_by_location(country: Optional[str] = None, city: Optional[str] = None, limit: int = 5) -> str:
    """Find blockchain events in a specific location

    Args:
        country: The country to filter by (e.g., "USA", "UAE") (optional)
        city: The city to filter by (e.g., "San Francisco", "Dubai") (optional)
        limit: Maximum number of events to return (default: 5, max: 15)

    Returns:
        JSON string with events in the specified location
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 15)
    events = BlockzaClient.get_events(
        country=country,
        city=city,
        limit=limit
    )
    return json.dumps({"events": events, "count": len(events)}, indent=2)


# ========== BLOCKZA PODCAST TOOLS ==========

@mcp.tool()
def list_podcasts(limit: int = 5, offset: int = 0) -> str:
    """List podcasts from Blockza directory

    Args:
        limit: Maximum number of podcasts to return (default: 5, max: 20)
        offset: Number of podcasts to skip for pagination (default: 0)

    Returns:
        JSON string with podcasts data
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 20)
    podcasts = BlockzaClient.get_podcasts(limit=limit, offset=offset)
    return json.dumps({"podcasts": podcasts, "count": len(podcasts)}, indent=2)


@mcp.tool()
def search_podcasts(
    query: str,
    limit: int = 5,
    category: Optional[str] = None,
    company: Optional[str] = None
) -> str:
    """Search for podcasts by title or description

    Args:
        query: Search term for podcast title or description
        limit: Maximum number of results (default: 5, max: 15)
        category: Filter by category (optional)
        company: Filter by company/organization (optional)

    Returns:
        JSON string with matching podcasts
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 15)
    podcasts = BlockzaClient.get_podcasts(
        search=query,
        limit=limit,
        category=category,
        company=company
    )
    return json.dumps({"podcasts": podcasts, "count": len(podcasts)}, indent=2)


@mcp.tool()
def get_podcast_details(podcast_id: str) -> str:
    """Get detailed information about a specific podcast

    Args:
        podcast_id: The podcast identifier

    Returns:
        JSON string with podcast details
    """
    podcast = BlockzaClient.get_podcast_by_id(podcast_id)
    if podcast is None:
        return json.dumps({"error": "Podcast not found", "podcast": None}, indent=2)
    return json.dumps(podcast, indent=2)


@mcp.tool()
def get_podcasts_by_category(category: str, limit: int = 5) -> str:
    """Get podcasts in a specific category

    Args:
        category: The category to filter by (optional)
        limit: Maximum number of podcasts to return (default: 5, max: 15)

    Returns:
        JSON string with podcasts in the category
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 15)
    podcasts = BlockzaClient.get_podcasts_by_category(category)
    return json.dumps({"podcasts": podcasts[:limit], "count": min(len(podcasts), limit)}, indent=2)


@mcp.tool()
def search_podcasts_by_company(company: str, limit: int = 5) -> str:
    """Find podcasts by a specific company or organization

    Args:
        company: The company/organization name to filter by
        limit: Maximum number of podcasts to return (default: 5, max: 15)

    Returns:
        JSON string with podcasts from the company
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 15)
    podcasts = BlockzaClient.get_podcasts(company=company, limit=limit)
    return json.dumps({"podcasts": podcasts, "count": len(podcasts)}, indent=2)


# ========== BLOCKZA EVENT RESOURCES ==========

@mcp.resource("blockza://events")
def resource_all_events() -> str:
    """Access blockchain events from Blockza directory (limited to 10 for performance)"""
    events = BlockzaClient.get_events(limit=10)
    return json.dumps({"events": events, "count": len(events)}, indent=2)


@mcp.resource("blockza://events/upcoming")
def resource_upcoming_events() -> str:
    """Access upcoming blockchain events (limited to 10 for performance)"""
    events = BlockzaClient.get_events(limit=10, upcoming=True)
    return json.dumps({"events": events, "count": len(events)}, indent=2)


@mcp.resource("blockza://events/{event_id}")
def resource_event_by_id(event_id: str) -> str:
    """Access a specific blockchain event by ID

    Args:
        event_id: The event identifier
    """
    event = BlockzaClient.get_event_by_id(event_id)
    if event is None:
        return json.dumps({"error": "Event not found"}, indent=2)
    return json.dumps(event, indent=2)


@mcp.resource("blockza://events/country/{country}")
def resource_events_by_country(country: str) -> str:
    """Access blockchain events filtered by country

    Args:
        country: The country to filter by
    """
    events = BlockzaClient.get_events(country=country, limit=30)
    return json.dumps({"events": events, "count": len(events)}, indent=2)


# ========== BLOCKZA PODCAST RESOURCES ==========

@mcp.resource("blockza://podcasts")
def resource_all_podcasts() -> str:
    """Access all podcasts from Blockza directory (limited to 10 for performance)"""
    podcasts = BlockzaClient.get_podcasts(limit=10)
    return json.dumps({"podcasts": podcasts, "count": len(podcasts)}, indent=2)


@mcp.resource("blockza://podcasts/{podcast_id}")
def resource_podcast_by_id(podcast_id: str) -> str:
    """Access a specific podcast by ID

    Args:
        podcast_id: The podcast identifier
    """
    podcast = BlockzaClient.get_podcast_by_id(podcast_id)
    if podcast is None:
        return json.dumps({"error": "Podcast not found"}, indent=2)
    return json.dumps(podcast, indent=2)


@mcp.resource("blockza://podcasts/category/{category}")
def resource_podcasts_by_category(category: str) -> str:
    """Access podcasts filtered by category

    Args:
        category: The category to filter by
    """
    podcasts = BlockzaClient.get_podcasts(category=category, limit=30)
    return json.dumps({"podcasts": podcasts, "count": len(podcasts)}, indent=2)


@mcp.resource("blockza://podcasts/company/{company}")
def resource_podcasts_by_company(company: str) -> str:
    """Access podcasts filtered by company

    Args:
        company: The company/organization name to filter by
    """
    podcasts = BlockzaClient.get_podcasts(company=company, limit=30)
    return json.dumps({"podcasts": podcasts, "count": len(podcasts)}, indent=2)


# ========== BLOCKZA EVENT PROMPTS ==========

@mcp.prompt()
def analyze_blockchain_events() -> list[dict[str, str]]:
    """Analyze blockchain events and provide insights"""
    return [
        {
            "role": "user",
            "content": """Please analyze the blockchain events data and provide:

1. **Overview**: Summary of the total number of events and date range
2. **Geographic Distribution**: Key locations and regional trends
3. **Event Types**: Categorization of events (conferences, hackathons, meetups, etc.)
4. **Timing Patterns**: Analysis of when events are scheduled (months, quarters)
5. **Key Highlights**: Notable or flagship events in the dataset
6. **Trends**: Any emerging patterns or insights about the blockchain event ecosystem

Please structure your analysis with clear sections and actionable insights."""
        }
    ]


@mcp.prompt()
def upcoming_events_summary() -> list[dict[str, str]]:
    """Generate a summary of upcoming blockchain events"""
    return [
        {
            "role": "user",
            "content": """Please provide a curated summary of upcoming blockchain events including:

1. **Next 30 Days**: Most important events happening soon
2. **By Region**: Events organized by geographic location
3. **Must-Attend**: Flagship conferences and major gatherings
4. **Virtual vs In-Person**: Distribution of event formats
5. **Recommendations**: Top 5 events to consider attending based on relevance

Focus on actionable information for someone planning their event attendance."""
        }
    ]


@mcp.prompt()
def compare_event_locations() -> list[dict[str, str]]:
    """Compare blockchain events across different locations"""
    return [
        {
            "role": "user",
            "content": """Please compare blockchain events across different locations:

1. **Major Hubs**: Identify top cities/countries hosting blockchain events
2. **Event Quality**: Compare the types and scale of events in each location
3. **Frequency**: How often events occur in each region
4. **Emerging Markets**: New or growing locations for blockchain events
5. **Travel Recommendations**: Which locations offer the best event clusters for trip planning

Provide data-driven insights to help with event planning and location selection."""
        }
    ]


# ========== BLOCKZA PODCAST PROMPTS ==========

@mcp.prompt()
def analyze_podcast_trends() -> list[dict[str, str]]:
    """Analyze podcast trends and provide insights"""
    return [
        {
            "role": "user",
            "content": """Please analyze the podcast data from the Blockza directory and provide insights covering:

1. **Overview**: Summary of total podcasts, distribution by category
2. **Popular Topics**: Most common podcast categories and trending subjects
3. **Content Creators**: Most active companies/organizations producing podcasts
4. **Engagement**: Podcasts with highest views and likes
5. **Content Gaps**: Underrepresented topics or opportunities for new podcasts
6. **Recommendations**: Key podcasts to follow based on engagement metrics

Please provide actionable insights for content creators and listeners."""
        }
    ]


@mcp.prompt()
def podcast_recommendations() -> list[dict[str, str]]:
    """Generate podcast recommendations"""
    return [
        {
            "role": "user",
            "content": """Please provide personalized podcast recommendations including:

1. **Top Podcasts**: Most popular and highly-rated podcasts across categories
2. **By Category**: Best podcasts in key blockchain and crypto categories
3. **New Content**: Recently added podcasts worth listening to
4. **Hidden Gems**: Lesser-known but high-quality podcasts
5. **For Beginners**: Podcasts perfect for learning about blockchain/crypto
6. **For Experts**: Advanced podcasts for experienced enthusiasts
7. **Series to Follow**: Podcasts with multiple episodes and consistent themes

Provide detailed recommendations with reasons why each podcast is worth listening to."""
        }
    ]


@mcp.prompt()
def compare_podcast_creators() -> list[dict[str, str]]:
    """Compare podcast creators and production companies"""
    return [
        {
            "role": "user",
            "content": """Please analyze and compare podcast creators based on:

1. **Production Quality**: Audio quality, editing, and presentation
2. **Content Depth**: Technical depth vs. accessibility of topics
3. **Release Frequency**: Consistency and schedule of new episodes
4. **Audience Engagement**: Likes, views, and community interaction
5. **Variety**: Range of topics covered across their podcast library
6. **Guest Appearances**: Notable guests and thought leaders featured
7. **Production Style**: Unique format and presentation approaches
8. **Growth Trajectory**: Emerging creators vs. established producers

Provide insights on choosing podcasts based on content preferences and creator styles."""
        }
    ]


if __name__ == "__main__":
    # Run the server
    mcp.run()
