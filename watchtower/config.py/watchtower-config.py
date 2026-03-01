"""
config.py
Central configuration: Supabase client, Slack/Teams webhook, and env vars.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
TEAMS_WEBHOOK_URL: str = os.getenv("TEAMS_WEBHOOK_URL", "")
DEFAULT_RETENTION_DAYS: int = int(os.getenv("DEFAULT_RETENTION_DAYS", "365"))
TRAINING_CONTENT_PATH: str = os.getenv("TRAINING_CONTENT_PATH", "data/training_modules.json")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
