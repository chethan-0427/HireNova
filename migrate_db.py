"""
HireNova - Root Database Migration Proxy
Forwards execution to `scripts/migrate_db.py`.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.migrate_db import run_migration

if __name__ == "__main__":
    run_migration()
