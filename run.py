"""
HireNova - Application Launcher
Launches the HireNova Flask web application.

Usage:
    python run.py
"""

import os
import sys

# Ensure project root is in the Python search path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.app import app

if __name__ == "__main__":
    print("=" * 60)
    print("  HireNova - Find Your Next Opportunity")
    print("  Server running at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host="127.0.0.1", port=5000)
