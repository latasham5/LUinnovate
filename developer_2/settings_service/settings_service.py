"""
Settings & Limitations Service
Developer 2 - The Enforcer
Allows admins and managers to set prompt limitations
for their departments or company-wide.
"""
import json
import os
import re
from datetime import datetime

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "default_settings.json")

# ─────────────────────────────────────────────
# In-memory settings store
# ─────────────────────────────────────────────
_company_settings = {}
_department_settings = {}
_role_settings = {}
_custom_keywords = {}

# ─────────────────────────────────────────────
# Profanity / slang blocklist (expandable)
# ─────────────────────────────────────────────
DEFAULT_PROFANITY = [
    "damn", "hell", "ass", "crap", "cussword1", "cussword2",
    "wtf", "stfu", "lmao", "bruh", "af", "bs", "smh"
]

# ─────────────────────────