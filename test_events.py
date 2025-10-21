#!/usr/bin/env python3
"""
Test script for Blockza events functionality
"""

import sys
sys.path.insert(0, '/Users/chetanmittal/Desktop/block/mcp/fastmcp')

from server import BlockzaClient
import json

def test_get_events():
    """Test fetching events"""
    print("Testing get_events()...")
    events = BlockzaClient.get_events(limit=5)

    if not isinstance(events, list):
        print(f"❌ Error: Expected list, got {type(events)}")
        return False

    print(f"✅ Success! Retrieved {len(events)} events")
    if events:
        first_event = events[0]
        print(f"   First event: {first_event.get('title', 'N/A')}")
    return True

def test_upcoming_events():
    """Test fetching upcoming events"""
    print("\nTesting get_events(upcoming=True)...")
    events = BlockzaClient.get_events(limit=3, upcoming=True)

    if not isinstance(events, list):
        print(f"❌ Error: Expected list, got {type(events)}")
        return False

    print(f"✅ Success! Retrieved {len(events)} upcoming events")
    return True

def test_search_events():
    """Test searching events"""
    print("\nTesting get_events(search='blockchain')...")
    events = BlockzaClient.get_events(search="blockchain", limit=3)

    if not isinstance(events, list):
        print(f"❌ Error: Expected list, got {type(events)}")
        return False

    print(f"✅ Success! Found {len(events)} events matching 'blockchain'")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("Blockza Events API Test")
    print("=" * 50)

    tests = [
        test_get_events,
        test_upcoming_events,
        test_search_events
    ]

    passed = sum(1 for test in tests if test())
    total = len(tests)

    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 50)

    sys.exit(0 if passed == total else 1)
