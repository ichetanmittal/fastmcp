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

# Load environment variables
load_dotenv()

# Server configuration
SERVER_NAME = os.getenv("SERVER_NAME", "mcp-server")
SERVER_VERSION = os.getenv("SERVER_VERSION", "1.0.0")

# Initialize FastMCP server
mcp = FastMCP(SERVER_NAME)

# ========== BLOCKZA API CLIENT ==========

class BlockzaClient:
    """Client for interacting with Blockza API"""

    BASE_URL = "https://api.blockza.io/api"

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
    def get_events(
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        upcoming: bool = False
    ) -> list[dict[str, Any]]:
        """Fetch events from Blockza API

        Args:
            limit: Maximum number of events to return
            offset: Number of events to skip
            search: Search query for event name or description
            country: Filter by country
            city: Filter by city
            upcoming: Only return upcoming events

        Returns:
            List of event dictionaries
        """
        try:
            url = f"{BlockzaClient.BASE_URL}/events"
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


if __name__ == "__main__":
    # Run the server
    mcp.run()
