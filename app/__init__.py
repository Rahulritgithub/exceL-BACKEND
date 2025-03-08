# app/__init__.py

from flask import Flask

app = Flask(__name__)

# Import routes or views
from app import app  # Import the app instance to avoid circular imports
