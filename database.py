"""
HireNova - Root Database Proxy
Exposes database utilities from `src.database` for backward compatibility.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database import get_db_connection, create_tables, DEFAULT_DB_PATH

__all__ = ["get_db_connection", "create_tables", "DEFAULT_DB_PATH"]

if __name__ == "__main__":
    create_tables()
    print("Database tables initialized successfully via root proxy.")
