"""
Application configuration loaded from environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central configuration for the Phantom App."""

    # Application
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Hugging Face — Developer 1
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")

    # CokeGPT — Developer 2
    COKEGPT_API_KEY: str = os.getenv("COKEGPT_API_KEY", "")

    # Supabase — Developer 3
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # Slack/Teams — Developer 3
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")

    # Deployment
    DEPLOYMENT_MODE: str = os.getenv("DEPLOYMENT_MODE", "SHADOW")  # SHADOW or FULL_ENFORCEMENT
    DEFAULT_POLICY_MODE: str = os.getenv("DEFAULT_POLICY_MODE", "BALANCED")  # STRICT, BALANCED, FAST

    @property
    def is_shadow_mode(self) -> bool:
        return self.DEPLOYMENT_MODE == "SHADOW"

    @property
    def is_mock_cokegpt(self) -> bool:
        return self.COKEGPT_API_KEY.startswith("mock_")


settings = Settings()
