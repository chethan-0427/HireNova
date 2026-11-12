"""
HireNova - Root Application Wrapper
Provides backward compatibility for running `python app.py`.
Imports and serves the core Flask application from `src.app`.

Usage:
    python app.py
    # or
    python run.py
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.app import app

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
