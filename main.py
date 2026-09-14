"""
main.py
-------
Root entry point for RadiVision AI.
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import main

if __name__ == "__main__":
    main()
