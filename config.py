import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    # Add any other configuration variables here
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')  # Optional: for GitHub API