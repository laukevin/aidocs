#!/usr/bin/env python3

import sys
import os
from pathlib import Path
sys.path.insert(0, '/data/projects/aidocs/src')

from aidocs.database import Database

def debug_search():
    db = Database(Path('.aidocs/store.db'))

    print("=== All docs in database ===")
    docs = db.list_docs()
    print(f"Found {len(docs)} docs:")
    for doc in docs:
        print(f"Name: {doc.name}")
        print(f"Description: {doc.description}")
        print(f"Content: {repr(doc.content[:100])}")
        print("---")

    print("\n=== Search for 'user' ===")
    results = db.search_docs('user')
    print(f"Found {len(results)} results:")
    for doc in results:
        print(f"- {doc.name}: {doc.description}")

    print("\n=== Search for 'authentication' ===")
    results = db.search_docs('authentication')
    print(f"Found {len(results)} results:")
    for doc in results:
        print(f"- {doc.name}: {doc.description}")

if __name__ == '__main__':
    debug_search()