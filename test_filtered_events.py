#!/usr/bin/env python3
"""
Test filtered event data size
"""

import sys
sys.path.insert(0, '/Users/chetanmittal/Desktop/block/mcp/fastmcp')

from server import BlockzaClient
import json

# Test getting 5 events
events = BlockzaClient.get_events(limit=5)

print(f"Number of events: {len(events)}")
print(f"JSON size: {len(json.dumps(events))} characters")
print(f"\nFirst event fields:")
if events:
    for key in events[0].keys():
        print(f"  - {key}")

print(f"\nSample event:")
print(json.dumps(events[0] if events else {}, indent=2))
