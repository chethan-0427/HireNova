"""
HireNova - Root Create Admin Proxy
Forwards execution to `scripts/create_admin.py`.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.create_admin import create_admin

if __name__ == "__main__":
    create_admin()
