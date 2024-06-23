"""This module is used to add the project root to the Python path."""

import sys
import os

# Get the absolute path of the project root
project_root = os.path.dirname(os.path.abspath(__file__))

# Add the project root to the Python path
sys.path.insert(0, project_root)
