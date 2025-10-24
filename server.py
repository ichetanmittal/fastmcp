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
    """Client for interacting with Blockza API with separate endpoints for better performance"""

    # Dedicated API Endpoints
    BASE_URL = "https://api.blockza.io/api"
    EVENTS_URL = "https://api.blockza.io/api/events"
    PODCASTS_URL = "https://api.blockza.io/api/podcasts"
    DIRECTORY_URL = "https://api.blockza.io/api/directory"  # Companies only
    EXPERTS_URL = "https://api.blockza.io/api/experts"  # Standalone experts
    BOOKINGS_URL = "https://api.blockza.io/api/bookings"  # Expert bookings

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

    @staticmethod
    def filter_expert_fields(expert: dict[str, Any]) -> dict[str, Any]:
        """Extract only essential fields from a standalone expert - from /api/experts endpoint

        Args:
            expert: Full expert dictionary from /api/experts

        Returns:
            Filtered expert with only essential fields
        """
        return {
            "_id": expert.get("_id"),
            "name": expert.get("name"),
            "title": expert.get("title"),
            "email": expert.get("email"),
            "image": expert.get("image"),
            "linkedinUrl": expert.get("linkedinUrl"),
            "price": expert.get("price", 0),
            "bookingMethods": expert.get("bookingMethods", []),
            "status": expert.get("status"),
            "followers": expert.get("followers", 0),
            "responseRate": expert.get("responseRate", 0)
        }

    @staticmethod
    def filter_team_member_fields(member: dict[str, Any], company_name: str = "") -> dict[str, Any]:
        """Extract only essential fields from a company team member - from /api/directory

        Args:
            member: Full team member dictionary from company
            company_name: Name of the company they belong to

        Returns:
            Filtered team member with company context
        """
        return {
            "_id": member.get("_id"),
            "name": member.get("name"),
            "title": member.get("title"),
            "email": member.get("email"),
            "image": member.get("image"),
            "linkedinUrl": member.get("linkedinUrl"),
            "price": member.get("price", 0),
            "bookingMethods": member.get("bookingMethods", []),
            "status": member.get("status"),
            "followers": member.get("followers", 0),
            "responseRate": member.get("responseRate", 0),
            "company": company_name,
            "memberType": "company_team_member"
        }

    @staticmethod
    def get_experts(
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Fetch standalone experts from dedicated /api/experts endpoint

        Args:
            limit: Maximum number of experts to return
            offset: Number of experts to skip
            search: Search query for expert name or title

        Returns:
            List of expert dictionaries
        """
        try:
            url = BlockzaClient.EXPERTS_URL
            params = {}

            if limit is not None:
                params["limit"] = limit
            if offset is not None:
                params["offset"] = offset
            if search:
                params["search"] = search

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            experts = data if isinstance(data, list) else (data.get("data", []) if isinstance(data, dict) else [])

            # Filter experts to reduce payload size
            filtered_experts = [BlockzaClient.filter_expert_fields(exp) for exp in experts]
            return filtered_experts
        except requests.exceptions.RequestException as e:
            print(f"Error fetching experts from /api/experts: {e}")
            return []

    @staticmethod
    def get_expert_by_id(expert_id: str) -> dict[str, Any] | None:
        """Fetch a specific expert by ID from /api/experts/:id

        Args:
            expert_id: The expert identifier

        Returns:
            Expert data dictionary or None if not found
        """
        try:
            url = f"{BlockzaClient.EXPERTS_URL}/{expert_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data:
                return BlockzaClient.filter_expert_fields(data)
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching expert by ID: {e}")
            return None

    @staticmethod
    def get_team_members(
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search: Optional[str] = None,
        company: Optional[str] = None,
        category: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Fetch team members from companies via /api/directory endpoint

        Args:
            limit: Maximum number of team members to return
            offset: Number to skip
            search: Search query for member name
            company: Filter by company name
            category: Filter by company category

        Returns:
            List of team member dictionaries with company context
        """
        try:
            url = BlockzaClient.DIRECTORY_URL
            params = {}

            if limit is not None:
                params["limit"] = limit
            if search:
                params["search"] = search
            if category:
                params["category"] = category

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            companies = data.get("data", []) if isinstance(data, dict) else []

            # Extract all team members from all companies
            team_members = []
            for company_data in companies:
                company_name = company_data.get("name", "")

                # Filter by company if specified
                if company and company.lower() not in company_name.lower():
                    continue

                if "teamMembers" in company_data:
                    for member in company_data["teamMembers"]:
                        filtered = BlockzaClient.filter_team_member_fields(member, company_name)

                        # Apply search filter if provided
                        if search:
                            search_lower = search.lower()
                            if (search_lower in filtered.get("name", "").lower() or
                                search_lower in filtered.get("title", "").lower() or
                                search_lower in filtered.get("email", "").lower()):
                                team_members.append(filtered)
                        else:
                            team_members.append(filtered)

            # Apply limit
            if limit:
                team_members = team_members[:limit]

            return team_members
        except requests.exceptions.RequestException as e:
            print(f"Error fetching team members from /api/directory: {e}")
            return []

    @staticmethod
    def get_team_member_by_id(member_id: str) -> dict[str, Any] | None:
        """Fetch a specific team member by ID

        Args:
            member_id: The team member identifier

        Returns:
            Team member data dictionary or None if not found
        """
        try:
            team_members = BlockzaClient.get_team_members(limit=1000)
            for member in team_members:
                if member.get("_id") == member_id:
                    return member
            return None
        except Exception as e:
            print(f"Error fetching team member by ID: {e}")
            return None

    @staticmethod
    def get_companies(
        limit: Optional[int] = None,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Fetch companies from Blockza directory

        Args:
            limit: Maximum number of companies to return
            search: Search query for company name
            category: Filter by category

        Returns:
            List of company dictionaries
        """
        try:
            url = BlockzaClient.DIRECTORY_URL
            params = {}

            if limit is not None:
                params["limit"] = limit
            if search:
                params["search"] = search
            if category:
                params["category"] = category

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            companies = data.get("data", []) if isinstance(data, dict) else []

            # Filter basic company info
            filtered_companies = []
            for company in companies:
                filtered_companies.append({
                    "_id": company.get("_id"),
                    "name": company.get("name"),
                    "slug": company.get("slug"),
                    "category": company.get("category"),
                    "shortDescription": company.get("shortDescription", "")[:200],
                    "logo": company.get("logo"),
                    "website": company.get("url"),
                    "founderName": company.get("founderName"),
                    "verificationStatus": company.get("verificationStatus"),
                    "teamSize": len(company.get("teamMembers", [])),
                    "likes": company.get("likes", 0),
                    "views": company.get("views", 0)
                })

            return filtered_companies
        except requests.exceptions.RequestException as e:
            print(f"Error fetching companies: {e}")
            return []

    @staticmethod
    def get_company_by_id(company_id: str) -> dict[str, Any] | None:
        """Fetch a specific company by ID

        Args:
            company_id: The company identifier

        Returns:
            Company data dictionary or None if not found
        """
        try:
            url = f"{BlockzaClient.DIRECTORY_URL}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            companies = data.get("data", []) if isinstance(data, dict) else []

            for company in companies:
                if company.get("_id") == company_id:
                    return company
            return None
        except Exception as e:
            print(f"Error fetching company by ID: {e}")
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


# ========== BLOCKZA STANDALONE EXPERTS TOOLS (FROM /api/experts) ==========

@mcp.tool()
def list_experts(limit: int = 5, offset: int = 0) -> str:
    """List standalone experts from /api/experts endpoint

    Args:
        limit: Maximum number of experts to return (default: 5, max: 20)
        offset: Number of experts to skip for pagination (default: 0)

    Returns:
        JSON string with standalone experts data
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 20)
    experts = BlockzaClient.get_experts(limit=limit, offset=offset)
    return json.dumps({
        "experts": experts,
        "count": len(experts),
        "source": "/api/experts",
        "type": "standalone_experts"
    }, indent=2)


@mcp.tool()
def search_experts(query: str, limit: int = 5) -> str:
    """Search for standalone experts by name or title from /api/experts

    Args:
        query: Search term for expert name or title
        limit: Maximum number of results (default: 5, max: 15)

    Returns:
        JSON string with matching standalone experts
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 15)
    experts = BlockzaClient.get_experts(search=query, limit=limit)
    return json.dumps({
        "experts": experts,
        "count": len(experts),
        "source": "/api/experts",
        "type": "standalone_experts"
    }, indent=2)


@mcp.tool()
def get_expert_details(expert_id: str) -> str:
    """Get detailed information about a standalone expert from /api/experts/:id

    Args:
        expert_id: The standalone expert identifier

    Returns:
        JSON string with standalone expert details
    """
    expert = BlockzaClient.get_expert_by_id(expert_id)
    if expert is None:
        return json.dumps({"error": "Expert not found", "expert": None}, indent=2)
    return json.dumps({
        "expert": expert,
        "source": "/api/experts",
        "type": "standalone_expert"
    }, indent=2)


@mcp.tool()
def get_top_experts(limit: int = 5, sort_by: str = "followers") -> str:
    """Get top standalone experts sorted by engagement metrics

    Args:
        limit: Maximum number of experts to return (default: 5, max: 15)
        sort_by: Sort by 'followers', 'responseRate', or 'price' (default: 'followers')

    Returns:
        JSON string with top standalone experts
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 15)
    experts = BlockzaClient.get_experts(limit=100)  # Get all to sort

    if sort_by == "responseRate":
        experts = sorted(experts, key=lambda x: x.get("responseRate", 0), reverse=True)
    elif sort_by == "price":
        experts = sorted(experts, key=lambda x: x.get("price", 0), reverse=True)
    else:  # followers
        experts = sorted(experts, key=lambda x: x.get("followers", 0), reverse=True)

    return json.dumps({
        "experts": experts[:limit],
        "count": min(len(experts), limit),
        "sortedBy": sort_by,
        "source": "/api/experts",
        "type": "standalone_experts"
    }, indent=2)


# ========== BLOCKZA TEAM MEMBERS TOOLS (FROM /api/directory companies) ==========

@mcp.tool()
def list_team_members(limit: int = 5, offset: int = 0) -> str:
    """List company team members from /api/directory endpoint

    Args:
        limit: Maximum number of team members to return (default: 5, max: 20)
        offset: Number to skip for pagination (default: 0)

    Returns:
        JSON string with company team members data
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 20)
    team_members = BlockzaClient.get_team_members(limit=limit, offset=offset)
    return json.dumps({
        "team_members": team_members,
        "count": len(team_members),
        "source": "/api/directory",
        "type": "company_team_members"
    }, indent=2)


@mcp.tool()
def search_team_members(
    query: str,
    limit: int = 5,
    company: Optional[str] = None,
    category: Optional[str] = None
) -> str:
    """Search for company team members by name or title from /api/directory

    Args:
        query: Search term for member name or title
        limit: Maximum number of results (default: 5, max: 15)
        company: Filter by company name (optional)
        category: Filter by company category (optional)

    Returns:
        JSON string with matching company team members
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 15)
    team_members = BlockzaClient.get_team_members(
        search=query,
        limit=limit,
        company=company,
        category=category
    )
    return json.dumps({
        "team_members": team_members,
        "count": len(team_members),
        "filters": {"search": query, "company": company, "category": category},
        "source": "/api/directory",
        "type": "company_team_members"
    }, indent=2)


@mcp.tool()
def get_team_member_details(member_id: str) -> str:
    """Get detailed information about a specific company team member

    Args:
        member_id: The team member identifier

    Returns:
        JSON string with team member details including company affiliation
    """
    member = BlockzaClient.get_team_member_by_id(member_id)
    if member is None:
        return json.dumps({"error": "Team member not found", "member": None}, indent=2)
    return json.dumps({
        "team_member": member,
        "source": "/api/directory",
        "type": "company_team_member"
    }, indent=2)


@mcp.tool()
def get_team_members_by_company(company: str, limit: int = 5) -> str:
    """Get all team members from a specific company

    Args:
        company: The company name to filter by
        limit: Maximum number of team members to return (default: 5, max: 15)

    Returns:
        JSON string with team members from the specified company
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 15)
    team_members = BlockzaClient.get_team_members(company=company, limit=limit)
    return json.dumps({
        "team_members": team_members,
        "count": len(team_members),
        "company": company,
        "source": "/api/directory",
        "type": "company_team_members"
    }, indent=2)


@mcp.tool()
def get_team_members_by_category(category: str, limit: int = 5) -> str:
    """Get team members from companies in a specific category

    Args:
        category: The company category to filter by
        limit: Maximum number of team members to return (default: 5, max: 15)

    Returns:
        JSON string with team members in the category
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 15)
    team_members = BlockzaClient.get_team_members(category=category, limit=limit)
    return json.dumps({
        "team_members": team_members,
        "count": len(team_members),
        "category": category,
        "source": "/api/directory",
        "type": "company_team_members"
    }, indent=2)


@mcp.tool()
def list_companies(limit: int = 5, offset: int = 0) -> str:
    """List companies from Blockza directory

    Args:
        limit: Maximum number of companies to return (default: 5, max: 20)
        offset: Number of companies to skip for pagination (default: 0)

    Returns:
        JSON string with companies data
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 20)
    companies = BlockzaClient.get_companies(limit=limit)
    return json.dumps({"companies": companies[:limit], "count": min(len(companies), limit)}, indent=2)


@mcp.tool()
def search_companies(
    query: str,
    limit: int = 5,
    category: Optional[str] = None
) -> str:
    """Search for companies by name or description

    Args:
        query: Search term for company name or description
        limit: Maximum number of results (default: 5, max: 15)
        category: Filter by category (optional)

    Returns:
        JSON string with matching companies
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 15)
    companies = BlockzaClient.get_companies(search=query, category=category, limit=limit)
    return json.dumps({"companies": companies, "count": len(companies)}, indent=2)


@mcp.tool()
def get_companies_by_category(category: str, limit: int = 5) -> str:
    """Get companies in a specific category

    Args:
        category: The category to filter by
        limit: Maximum number of companies to return (default: 5, max: 15)

    Returns:
        JSON string with companies in the category
    """
    # Cap limit to prevent token overflow
    limit = min(limit, 15)
    companies = BlockzaClient.get_companies(category=category, limit=limit)
    return json.dumps({"companies": companies, "count": len(companies)}, indent=2)


# ========== BLOCKZA COMPANY RESOURCES ==========

@mcp.resource("blockza://experts")
def resource_all_experts() -> str:
    """Access all standalone experts from /api/experts (limited to 20 for performance)"""
    experts = BlockzaClient.get_experts(limit=20)
    return json.dumps({
        "experts": experts,
        "count": len(experts),
        "source": "/api/experts",
        "type": "standalone_experts"
    }, indent=2)


@mcp.resource("blockza://experts/{expert_id}")
def resource_expert_by_id(expert_id: str) -> str:
    """Access a specific standalone expert by ID

    Args:
        expert_id: The standalone expert identifier
    """
    expert = BlockzaClient.get_expert_by_id(expert_id)
    if expert is None:
        return json.dumps({"error": "Expert not found"}, indent=2)
    return json.dumps({
        "expert": expert,
        "source": "/api/experts",
        "type": "standalone_expert"
    }, indent=2)


@mcp.resource("blockza://team-members")
def resource_all_team_members() -> str:
    """Access all company team members from /api/directory (limited to 20 for performance)"""
    team_members = BlockzaClient.get_team_members(limit=20)
    return json.dumps({
        "team_members": team_members,
        "count": len(team_members),
        "source": "/api/directory",
        "type": "company_team_members"
    }, indent=2)


@mcp.resource("blockza://team-members/{member_id}")
def resource_team_member_by_id(member_id: str) -> str:
    """Access a specific company team member by ID

    Args:
        member_id: The team member identifier
    """
    member = BlockzaClient.get_team_member_by_id(member_id)
    if member is None:
        return json.dumps({"error": "Team member not found"}, indent=2)
    return json.dumps({
        "team_member": member,
        "source": "/api/directory",
        "type": "company_team_member"
    }, indent=2)


@mcp.resource("blockza://team-members/company/{company}")
def resource_team_members_by_company(company: str) -> str:
    """Access team members filtered by company

    Args:
        company: The company name to filter by
    """
    team_members = BlockzaClient.get_team_members(company=company, limit=30)
    return json.dumps({
        "team_members": team_members,
        "count": len(team_members),
        "company": company,
        "source": "/api/directory",
        "type": "company_team_members"
    }, indent=2)


@mcp.resource("blockza://team-members/category/{category}")
def resource_team_members_by_category(category: str) -> str:
    """Access team members filtered by company category

    Args:
        category: The category to filter by
    """
    team_members = BlockzaClient.get_team_members(category=category, limit=30)
    return json.dumps({
        "team_members": team_members,
        "count": len(team_members),
        "category": category,
        "source": "/api/directory",
        "type": "company_team_members"
    }, indent=2)


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


# ========== BLOCKZA COMPANY RESOURCES ==========

@mcp.resource("blockza://companies")
def resource_all_companies() -> str:
    """Access all companies from /api/directory (limited to 20 for performance)"""
    companies = BlockzaClient.get_companies(limit=20)
    return json.dumps({
        "companies": companies,
        "count": len(companies),
        "source": "/api/directory",
        "type": "companies"
    }, indent=2)


@mcp.resource("blockza://companies/{company_id}")
def resource_company_by_id(company_id: str) -> str:
    """Access a specific company by ID

    Args:
        company_id: The company identifier
    """
    company = BlockzaClient.get_company_by_id(company_id)
    if company is None:
        return json.dumps({"error": "Company not found"}, indent=2)
    return json.dumps({
        "company": company,
        "source": "/api/directory",
        "type": "company"
    }, indent=2)


@mcp.resource("blockza://companies/category/{category}")
def resource_companies_by_category(category: str) -> str:
    """Access companies filtered by category

    Args:
        category: The category to filter by
    """
    companies = BlockzaClient.get_companies(category=category, limit=30)
    return json.dumps({
        "companies": companies,
        "count": len(companies),
        "category": category,
        "source": "/api/directory",
        "type": "companies"
    }, indent=2)


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


# ========== BLOCKZA EXPERT PROMPTS ==========

@mcp.prompt()
def find_expert_for_needs() -> list[dict[str, str]]:
    """Find the right expert for specific needs"""
    return [
        {
            "role": "user",
            "content": """Based on the expert directory data, help me find the right expert for my needs by:

1. **Identifying Key Requirements**: What specific skills and experience are needed?
2. **Expert Matching**: Recommend experts who match the requirements
3. **Availability Analysis**: Check booking methods and response rates
4. **Pricing Assessment**: Compare consulting rates and value proposition
5. **Track Record**: Analyze follower counts and engagement as quality indicators
6. **Communication Fit**: Suggest experts based on title and background alignment
7. **Next Steps**: Provide recommendations for contacting or hiring recommended experts

Consider factors like response rate, followers, credentials, and pricing when making recommendations."""
        }
    ]


@mcp.prompt()
def analyze_expert_community() -> list[dict[str, str]]:
    """Analyze the expert community and provide insights"""
    return [
        {
            "role": "user",
            "content": """Please analyze the expert community from the Blockza directory and provide insights covering:

1. **Community Overview**: Total number of experts, distribution across categories
2. **Top Performers**: Experts with highest followers, best response rates
3. **Expertise Areas**: Most represented skills and specializations
4. **Pricing Tiers**: Distribution of consulting rates and market positioning
5. **Engagement Metrics**: Average followers, response rates by category
6. **Emerging Experts**: New experts with high potential
7. **Collaboration Opportunities**: Experts who frequently work together
8. **Market Gaps**: Underrepresented expertise areas

Provide actionable insights for both experts and those seeking their services."""
        }
    ]


@mcp.prompt()
def compare_experts() -> list[dict[str, str]]:
    """Compare experts and consultants"""
    return [
        {
            "role": "user",
            "content": """Please compare experts from the Blockza directory based on:

1. **Expertise & Title**: What is their primary focus and expertise level?
2. **Response Rate**: How quickly and reliably do they respond to inquiries?
3. **Follower Base**: What is their reputation and community reach?
4. **Pricing**: Consulting rates and value proposition
5. **Booking Methods**: Available channels for engagement (email, video call, etc.)
6. **Status**: Current availability and active engagement level
7. **Background**: Company affiliation and professional experience
8. **Specialization**: Unique skills and market positioning

Rank them by overall suitability for different use cases and provide hiring recommendations."""
        }
    ]


# ========== BLOCKZA COMPANY PROMPTS ==========

@mcp.prompt()
def analyze_blockchain_companies() -> list[dict[str, str]]:
    """Analyze blockchain companies in the directory"""
    return [
        {
            "role": "user",
            "content": """Please analyze the blockchain companies from the Blockza directory and provide insights covering:

1. **Market Overview**: Total companies, distribution by category, market size
2. **Top Companies**: Most popular companies by views and likes
3. **Verification Status**: Breakdown of verified vs. unverified companies
4. **Category Leaders**: Leading companies in each blockchain category
5. **Team Strength**: Average team size, distribution of human resources
6. **Engagement**: Views, likes, and community interaction patterns
7. **Business Models**: Patterns in promotion settings and affiliate programs
8. **Growth Opportunities**: Emerging companies and market trends

Provide data-driven insights for investors, partners, and industry observers."""
        }
    ]


@mcp.prompt()
def company_partnership_recommendations() -> list[dict[str, str]]:
    """Generate partnership recommendations for companies"""
    return [
        {
            "role": "user",
            "content": """Based on the company directory, help identify partnership opportunities:

1. **Company Analysis**: Analyze the requesting company's profile and goals
2. **Synergy Identification**: Find companies with complementary services
3. **Market Fit**: Identify partners in adjacent markets or categories
4. **Verification Status**: Prioritize verified and trusted partners
5. **Team Strength**: Companies with strong team capabilities
6. **Business Readiness**: Companies with active affiliate programs
7. **Growth Stage**: Match companies at similar growth stages
8. **Contact Strategy**: Provide outreach recommendations

Suggest specific partnership types and joint opportunity ideas."""
        }
    ]


@mcp.prompt()
def compare_blockchain_companies() -> list[dict[str, str]]:
    """Compare blockchain companies"""
    return [
        {
            "role": "user",
            "content": """Please compare blockchain companies from the Blockza directory based on:

1. **Business Focus**: Core mission, products, and services
2. **Team Size & Quality**: Number and expertise of team members
3. **Founder Background**: Founder credentials and vision
4. **Market Position**: Verification status, likes, views, and reputation
5. **Community Engagement**: Social media presence and follower counts
6. **Business Model**: Revenue streams and partnership strategies
7. **Competitive Advantages**: Unique value propositions
8. **Growth Potential**: Market opportunity and expansion possibilities

Rank companies by overall potential and provide investment or partnership recommendations."""
        }
    ]


if __name__ == "__main__":
    # Run the server
    mcp.run()
