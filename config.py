"""
config.py
Configuration and constants for P2P Notes App.
Defines database path, ports, and device ID length.
"""

from pathlib import Path


DB_PATH = Path(__file__).parent / ".p2p_notes.db"

PORT = 9876
FLASK_PORT = 5000
DEVICE_ID_LENGTH = 8