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
_company_settings = {}    # Set by admins — apply to ALL employees
_department_settings = {} # Set by managers — apply to their department
_role_settings = {}       # Set by admins — apply to specific roles
_custom_keywords = {}     # Custom blocked keywords added by managers/admins

# ─────────────────────────────────────────────
# Profanity / slang blocklist (expandable)
# ─────────────────────────────────────────────
DEFAULT_PROFANITY = [
    "damn", "hell", "ass", "crap", "cussword1", "cussword2",
    "wtf", "stfu", "lmao", "bruh", "af", "bs", "smh"
]

# ─────────────────────────────────────────────
# Default blocked topics
# ─────────────────────────────────────────────
DEFAULT_BLOCKED_TOPICS = [
    "competitor analysis",
    "legal advice",
    "hr complaints",
    "salaries",
    "internal code names",
    "employee termination",
    "lawsuit",
    "union organizing"
]

# ─────────────────────────────────────────────
# Default approved use cases by role
# ─────────────────────────────────────────────
DEFAULT_APPROVED_USE_CASES = {
    "analyst": ["summarize", "draft email", "market research", "data analysis", "create report"],
    "engineer": ["summarize", "draft email", "debug help", "code review", "documentation"],
    "manager": ["summarize", "draft email", "team update", "create report", "project planning", "code review"],
    "director": ["summarize", "draft email", "team update", "create report", "project planning", "strategy analysis"],
    "admin": ["all"]
}

# ─────────────────────────────────────────────
# Data type patterns for detection
# ─────────────────────────────────────────────
DATA_TYPE_PATTERNS = {
    "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    "phone": r'(\+?1?\s?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}',
    "url": r'https?://[^\s]+|www\.[^\s]+',
    "code_snippet": r'(def |class |import |from |function |const |let |var |public |private |<\?php|SELECT\s|INSERT\s|CREATE\s)',
    "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "api_key": r'(api[_-]?key|token|secret)[=:\s]+[A-Za-z0-9_\-]{16,}'
}

# ─────────────────────────────────────────────
# Paste / length thresholds
# ─────────────────────────────────────────────
DEFAULT_MAX_PROMPT_LENGTH = 2000
DEFAULT_PASTE_THRESHOLD = 500  # chars — anything above this is considered a "paste"


def _load_default_settings():
    """Load default settings from JSON file if it exists."""
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    return {}


def _save_settings():
    """Persist all settings to JSON."""
    data = {
        "company": _company_settings,
        "departments": _department_settings,
        "roles": _role_settings,
        "custom_keywords": _custom_keywords
    }
    with open(SETTINGS_PATH, "w") as f:
        json.dump(data, f, indent=2)


# ══════════════════════════════════════════════
# PERMISSION CHECKING
# ══════════════════════════════════════════════

def _check_permission(user_profile: dict, scope: str, target_dept: str = None) -> dict:
    """
    Verify user has permission to modify settings.
    Admins → company-wide + any department + role-based
    Managers → their own department only
    """
    role = user_profile.get("role", "")
    clearance = user_profile.get("clearance", "standard")
    user_dept = user_profile.get("department", "")

    if scope == "company":
        if clearance != "admin" and role not in ("director", "admin"):
            return {"allowed": False, "error": "Only admins can set company-wide limitations"}
        return {"allowed": True}

    if scope == "department":
        if clearance == "admin" or role in ("director", "admin"):
            return {"allowed": True}
        if role == "manager" and user_dept == target_dept:
            return {"allowed": True}
        if role == "manager" and user_dept != target_dept:
            return {"allowed": False, "error": f"You can only manage your own department ({user_dept})"}
        return {"allowed": False, "error": "Only managers and admins can set department limitations"}

    if scope == "role":
        if clearance != "admin" and role not in ("director", "admin"):
            return {"allowed": False, "error": "Only admins can set role-based limitations"}
        return {"allowed": True}

    return {"allowed": False, "error": "Invalid scope"}


# ══════════════════════════════════════════════
# BLOCKED KEYWORDS MANAGEMENT
# ══════════════════════════════════════════════

def add_blocked_keywords(user_profile: dict, keywords: list[str], scope: str = "department", target_dept: str = None) -> dict:
    """
    Add custom blocked keywords/phrases.
    Managers → department-level only
    Admins → company-wide or any department
    This is the 'input box' feature for department heads.
    """
    dept = target_dept or user_profile.get("department", "")
    perm = _check_permission(user_profile, scope, dept)
    if not perm["allowed"]:
        return perm

    key = "company" if scope == "company" else f"dept:{dept}"
    if key not in _custom_keywords:
        _custom_keywords[key] = []

    new_words = [kw.strip().lower() for kw in keywords if kw.strip()]
    existing = set(_custom_keywords[key])
    added = [w for w in new_words if w not in existing]
    _custom_keywords[key].extend(added)
    _save_settings()

    return {
        "success": True,
        "scope": scope,
        "target": dept if scope == "department" else "all",
        "added": added,
        "total_blocked_keywords": len(_custom_keywords[key]),
        "set_by": user_profile.get("name", "unknown"),
        "timestamp": datetime.utcnow().isoformat()
    }


def remove_blocked_keywords(user_profile: dict, keywords: list[str], scope: str = "department", target_dept: str = None) -> dict:
    """Remove keywords from the blocklist."""
    dept = target_dept or user_profile.get("department", "")
    perm = _check_permission(user_profile, scope, dept)
    if not perm["allowed"]:
        return perm

    key = "company" if scope == "company" else f"dept:{dept}"
    if key not in _custom_keywords:
        return {"success": True, "removed": [], "message": "No keywords to remove"}

    to_remove = {kw.strip().lower() for kw in keywords}
    removed = [w for w in _custom_keywords[key] if w in to_remove]
    _custom_keywords[key] = [w for w in _custom_keywords[key] if w not in to_remove]
    _save_settings()

    return {
        "success": True,
        "removed": removed,
        "remaining": len(_custom_keywords[key])
    }


def get_blocked_keywords(scope: str = "company", department: str = None) -> list[str]:
    """Get all blocked keywords for a given scope."""
    if scope == "company":
        return _custom_keywords.get("company", [])
    return _custom_keywords.get(f"dept:{department}", [])


# ══════════════════════════════════════════════
# SETTINGS CONFIGURATION
# ══════════════════════════════════════════════

def set_company_settings(user_profile: dict, settings: dict) -> dict:
    """
    Admin sets company-wide limitations.
    These apply to ALL employees and override department settings.
    """
    global _company_settings
    perm = _check_permission(user_profile, "company")
    if not perm["allowed"]:
        return perm

    _company_settings = {
        "blocked_topics": settings.get("blocked_topics", DEFAULT_BLOCKED_TOPICS),
        "blocked_data_types": settings.get("blocked_data_types", ["email", "phone", "ssn", "credit_card"]),
        "block_profanity": settings.get("block_profanity", True),
        "profanity_list": settings.get("profanity_list", DEFAULT_PROFANITY),
        "work_hours_only": settings.get("work_hours_only", True),
        "work_hours_start": settings.get("work_hours_start", 8),
        "work_hours_end": settings.get("work_hours_end", 18),
        "max_prompt_length": settings.get("max_prompt_length", DEFAULT_MAX_PROMPT_LENGTH),
        "block_large_paste": settings.get("block_large_paste", True),
        "paste_threshold": settings.get("paste_threshold", DEFAULT_PASTE_THRESHOLD),
        "override_priority": settings.get("override_priority", "company_overrides_department"),
        "set_by": user_profile.get("employee_id", "unknown"),
        "set_at": datetime.utcnow().isoformat()
    }
    _save_settings()
    return {"success": True, "scope": "company", "settings": _company_settings}


def set_department_settings(user_profile: dict, department: str, settings: dict) -> dict:
    """
    Manager sets department-level limitations.
    Only applies to employees in their department.
    """
    perm = _check_permission(user_profile, "department", department)
    if not perm["allowed"]:
        return perm

    _department_settings[department] = {
        "blocked_topics": settings.get("blocked_topics", []),
        "blocked_data_types": settings.get("blocked_data_types", []),
        "blocked_keywords": settings.get("blocked_keywords", []),
        "block_profanity": settings.get("block_profanity", True),
        "additional_profanity": settings.get("additional_profanity", []),
        "approved_use_cases": settings.get("approved_use_cases", []),
        "restrict_to_approved_only": settings.get("restrict_to_approved_only", False),
        "work_hours_only": settings.get("work_hours_only", None),
        "work_hours_start": settings.get("work_hours_start", None),
        "work_hours_end": settings.get("work_hours_end", None),
        "max_prompt_length": settings.get("max_prompt_length", None),
        "block_large_paste": settings.get("block_large_paste", None),
        "paste_threshold": settings.get("paste_threshold", None),
        "set_by": user_profile.get("employee_id", "unknown"),
        "set_at": datetime.utcnow().isoformat()
    }
    _save_settings()
    return {"success": True, "scope": "department", "department": department, "settings": _department_settings[department]}


def set_role_settings(user_profile: dict, role: str, settings: dict) -> dict:
    """
    Admin sets role-based limitations.
    Applies to all employees with a specific role across the company.
    """
    perm = _check_permission(user_profile, "role")
    if not perm["allowed"]:
        return perm

    _role_settings[role] = {
        "approved_use_cases": settings.get("approved_use_cases", DEFAULT_APPROVED_USE_CASES.get(role, [])),
        "restrict_to_approved_only": settings.get("restrict_to_approved_only", False),
        "blocked_data_types": settings.get("blocked_data_types", []),
        "max_prompt_length": settings.get("max_prompt_length", None),
        "set_by": user_profile.get("employee_id", "unknown"),
        "set_at": datetime.utcnow().isoformat()
    }
    _save_settings()
    return {"success": True, "scope": "role", "role": role, "settings": _role_settings[role]}


# ══════════════════════════════════════════════
# GET SETTINGS (for reading current config)
# ══════════════════════════════════════════════

def get_company_settings() -> dict:
    """Return current company-wide settings."""
    return _company_settings.copy()


def get_department_settings(department: str) -> dict:
    """Return settings for a specific department."""
    return _department_settings.get(department, {})


def get_role_settings(role: str) -> dict:
    """Return settings for a specific role."""
    return _role_settings.get(role, {})


def get_all_settings_for_user(user_profile: dict) -> dict:
    """
    Get the MERGED settings that apply to a specific user.
    Combines company + department + role with override priority.
    """
    dept = user_profile.get("department", "")
    role = user_profile.get("role", "")

    company = _company_settings.copy()
    dept_s = _department_settings.get(dept, {})
    role_s = _role_settings.get(role, {})

    priority = company.get("override_priority", "company_overrides_department")

    merged = {
        "blocked_topics": list(set(
            company.get("blocked_topics", []) +
            dept_s.get("blocked_topics", [])
        )),
        "blocked_data_types": list(set(
            company.get("blocked_data_types", []) +
            dept_s.get("blocked_data_types", []) +
            role_s.get("blocked_data_types", [])
        )),
        "blocked_keywords": list(set(
            _custom_keywords.get("company", []) +
            _custom_keywords.get(f"dept:{dept}", []) +
            dept_s.get("blocked_keywords", [])
        )),
        "block_profanity": company.get("block_profanity", True) or dept_s.get("block_profanity", True),
        "profanity_list": list(set(
            company.get("profanity_list", DEFAULT_PROFANITY) +
            dept_s.get("additional_profanity", [])
        )),
        "approved_use_cases": role_s.get("approved_use_cases", DEFAULT_APPROVED_USE_CASES.get(role, [])),
        "restrict_to_approved_only": role_s.get("restrict_to_approved_only", False) or dept_s.get("restrict_to_approved_only", False),
        "max_prompt_length": None,
        "block_large_paste": company.get("block_large_paste", True),
        "paste_threshold": None,
        "work_hours_only": None,
        "work_hours_start": None,
        "work_hours_end": None
    }

    # Apply override priority for conflicting numeric settings
    if priority == "company_overrides_department":
        merged["max_prompt_length"] = company.get("max_prompt_length") or dept_s.get("max_prompt_length") or role_s.get("max_prompt_length") or DEFAULT_MAX_PROMPT_LENGTH
        merged["paste_threshold"] = company.get("paste_threshold") or dept_s.get("paste_threshold") or DEFAULT_PASTE_THRESHOLD
        merged["work_hours_only"] = company.get("work_hours_only", False) if company.get("work_hours_only") is not None else dept_s.get("work_hours_only", False)
        merged["work_hours_start"] = company.get("work_hours_start") or dept_s.get("work_hours_start") or 8
        merged["work_hours_end"] = company.get("work_hours_end") or dept_s.get("work_hours_end") or 18
    else:
        merged["max_prompt_length"] = dept_s.get("max_prompt_length") or company.get("max_prompt_length") or role_s.get("max_prompt_length") or DEFAULT_MAX_PROMPT_LENGTH
        merged["paste_threshold"] = dept_s.get("paste_threshold") or company.get("paste_threshold") or DEFAULT_PASTE_THRESHOLD
        merged["work_hours_only"] = dept_s.get("work_hours_only") if dept_s.get("work_hours_only") is not None else company.get("work_hours_only", False)
        merged["work_hours_start"] = dept_s.get("work_hours_start") or company.get("work_hours_start") or 8
        merged["work_hours_end"] = dept_s.get("work_hours_end") or company.get("work_hours_end") or 18

    return merged


# ══════════════════════════════════════════════
# PROMPT VALIDATION (the main enforcement function)
# ══════════════════════════════════════════════

def validate_prompt(user_profile: dict, prompt_text: str) -> dict:
    """
    MAIN FUNCTION — validates a prompt against ALL active limitations.
    Returns pass/fail with detailed reasons.
    Called BEFORE Developer 1's risk engine.
    """
    violations = []
    warnings = []
    settings = get_all_settings_for_user(user_profile)

    # ── 1. Time-of-day check ──
    if settings.get("work_hours_only"):
        now = datetime.now().hour
        start = settings.get("work_hours_start", 8)
        end = settings.get("work_hours_end", 18)
        if now < start or now >= end:
            violations.append({
                "type": "time_restriction",
                "message": f"AI usage is restricted to work hours ({start}:00 - {end}:00). Current hour: {now}:00"
            })

    # ── 2. Prompt length check ──
    max_len = settings.get("max_prompt_length", DEFAULT_MAX_PROMPT_LENGTH)
    if len(prompt_text) > max_len:
        violations.append({
            "type": "prompt_too_long",
            "message": f"Prompt exceeds maximum length ({len(prompt_text)}/{max_len} characters)"
        })

    # ── 3. Large paste detection ──
    if settings.get("block_large_paste"):
        threshold = settings.get("paste_threshold", DEFAULT_PASTE_THRESHOLD)
        lines = prompt_text.count("\n")
        if len(prompt_text) > threshold and lines > 5:
            violations.append({
                "type": "large_paste_detected",
                "message": f"Large data paste detected ({len(prompt_text)} chars, {lines} lines). Pasting large blocks of data is restricted."
            })

    # ── 4. Blocked keywords check ──
    blocked_kw = settings.get("blocked_keywords", [])
    prompt_lower = prompt_text.lower()
    found_keywords = [kw for kw in blocked_kw if kw in prompt_lower]
    if found_keywords:
        violations.append({
            "type": "blocked_keyword",
            "message": f"Prompt contains blocked keywords: {', '.join(found_keywords)}"
        })

    # ── 5. Blocked topics check ──
    blocked_topics = settings.get("blocked_topics", [])
    found_topics = [t for t in blocked_topics if t.lower() in prompt_lower]
    if found_topics:
        violations.append({
            "type": "blocked_topic",
            "message": f"Prompt touches restricted topics: {', '.join(found_topics)}"
        })

    # ── 6. Data type restrictions ──
    blocked_types = settings.get("blocked_data_types", [])
    for dtype, pattern in DATA_TYPE_PATTERNS.items():
        if dtype in blocked_types:
            matches = re.findall(pattern, prompt_text, re.IGNORECASE)
            if matches:
                violations.append({
                    "type": f"blocked_data_type:{dtype}",
                    "message": f"Prompt contains blocked data type: {dtype} ({len(matches)} instance(s) detected)"
                })

    # ── 7. Profanity / slang check ──
    if settings.get("block_profanity"):
        profanity_list = settings.get("profanity_list", DEFAULT_PROFANITY)
        words = re.findall(r'\b\w+\b', prompt_lower)
        found_profanity = [w for w in words if w in profanity_list]
        if found_profanity:
            violations.append({
                "type": "profanity_detected",
                "message": f"Prompt contains blocked language: {', '.join(set(found_profanity))}"
            })

    # ── 8. Approved use cases check ──
    if settings.get("restrict_to_approved_only"):
        approved = settings.get("approved_use_cases", [])
        if "all" not in approved:
            prompt_matches_use_case = False
            for case in approved:
                if case.lower() in prompt_lower:
                    prompt_matches_use_case = True
                    break
            if not prompt_matches_use_case:
                warnings.append({
                    "type": "unapproved_use_case",
                    "message": f"This prompt may not match your approved use cases: {', '.join(approved)}. Please ensure your request aligns with approved tasks."
                })

    # ── Build result ──
    passed = len(violations) == 0
    return {
        "passed": passed,
        "violations": violations,
        "warnings": warnings,
        "violation_count": len(violations),
        "warning_count": len(warnings),
        "user": user_profile.get("employee_id"),
        "department": user_profile.get("department"),
        "role": user_profile.get("role"),
        "prompt_length": len(prompt_text),
        "validated_at": datetime.utcnow().isoformat(),
        "settings_applied": {
            "scope": "merged (company + department + role)",
            "override_priority": _company_settings.get("override_priority", "company_overrides_department")
        }
    }


# ══════════════════════════════════════════════
# VIEW / AUDIT FUNCTIONS
# ══════════════════════════════════════════════

def get_settings_summary(user_profile: dict) -> dict:
    """
    Returns a readable summary of what limitations apply to a user.
    Useful for the frontend to display current restrictions.
    """
    settings = get_all_settings_for_user(user_profile)
    return {
        "employee": user_profile.get("name"),
        "department": user_profile.get("department"),
        "role": user_profile.get("role"),
        "active_limitations": {
            "blocked_keywords_count": len(settings.get("blocked_keywords", [])),
            "blocked_topics": settings.get("blocked_topics", []),
            "blocked_data_types": settings.get("blocked_data_types", []),
            "profanity_filter": settings.get("block_profanity", False),
            "work_hours_restriction": f"{settings.get('work_hours_start')}:00 - {settings.get('work_hours_end')}:00" if settings.get("work_hours_only") else "None",
            "max_prompt_length": settings.get("max_prompt_length"),
            "paste_blocking": settings.get("block_large_paste"),
            "approved_use_cases": settings.get("approved_use_cases", []),
            "restricted_to_approved_only": settings.get("restrict_to_approved_only", False)
        }
    }


def get_limitation_audit_log(user_profile: dict, scope: str = "company") -> dict:
    """See who set what limitations and when."""
    if scope == "company":
        return {
            "scope": "company",
            "set_by": _company_settings.get("set_by", "not configured"),
            "set_at": _company_settings.get("set_at", "never"),
            "settings": _company_settings
        }
    dept = user_profile.get("department", "")
    return {
        "scope": "department",
        "department": dept,
        "set_by": _department_settings.get(dept, {}).get("set_by", "not configured"),
        "set_at": _department_settings.get(dept, {}).get("set_at", "never"),
        "settings": _department_settings.get(dept, {})
    }


# ══════════════════════════════════════════════
# SMOKE TEST
# ══════════════════════════════════════════════

if __name__ == "__main__":
    # Mock admin profile
    admin = {
        "employee_id": "EMP100",
        "name": "Henry Chen",
        "role": "director",
        "department": "executive",
        "clearance": "admin"
    }

    # Mock manager profile
    manager = {
        "employee_id": "EMP010",
        "name": "Carol Davis",
        "role": "manager",
        "department": "marketing",
        "clearance": "elevated"
    }

    # Mock employee profile
    employee = {
        "employee_id": "EMP001",
        "name": "Alice Johnson",
        "role": "analyst",
        "department": "marketing",
        "clearance": "standard"
    }

    print("=" * 60)
    print("1. ADMIN SETS COMPANY-WIDE SETTINGS")
    print("=" * 60)
    result = set_company_settings(admin, {
        "blocked_topics": DEFAULT_BLOCKED_TOPICS,
        "blocked_data_types": ["email", "phone", "ssn", "credit_card", "api_key"],
        "block_profanity": True,
        "work_hours_only": True,
        "max_prompt_length": 2000,
        "block_large_paste": True,
        "override_priority": "company_overrides_department"
    })
    print(f"Success: {result['success']}")

    print("\n" + "=" * 60)
    print("2. ADMIN ADDS COMPANY-WIDE BLOCKED KEYWORDS")
    print("=" * 60)
    result = add_blocked_keywords(admin, [
        "secret formula", "merchandise 7x", "coca-cola recipe",
        "ingredient list", "syrup ratio"
    ], scope="company")
    print(f"Added: {result['added']}")

    print("\n" + "=" * 60)
    print("3. MANAGER ADDS DEPARTMENT KEYWORDS")
    print("=" * 60)
    result = add_blocked_keywords(manager, [
        "campaign budget", "influencer rates", "ad spend"
    ], scope="department")
    print(f"Added: {result['added']}")

    print("\n" + "=" * 60)
    print("4. MANAGER SETS DEPARTMENT SETTINGS")
    print("=" * 60)
    result = set_department_settings(manager, "marketing", {
        "blocked_topics": ["competitor analysis", "ad strategy"],
        "restrict_to_approved_only": True,
        "approved_use_cases": ["summarize", "draft email", "market research"]
    })
    print(f"Success: {result['success']}")

    print("\n" + "=" * 60)
    print("5. EMPLOYEE TRIES TO SEND PROMPTS")
    print("=" * 60)

    # Clean prompt
    test1 = validate_prompt(employee, "Can you summarize our Q3 marketing report?")
    print(f"\nClean prompt: PASSED={test1['passed']}, Violations={test1['violation_count']}")

    # Prompt with blocked keyword
    test2 = validate_prompt(employee, "What is the secret formula for Coca-Cola?")
    print(f"Blocked keyword: PASSED={test2['passed']}, Violations={test2['violations']}")

    # Prompt with email
    test3 = validate_prompt(employee, "Send this to john.doe@coca-cola.com please")
    print(f"Email detected: PASSED={test3['passed']}, Violations={test3['violations']}")

    # Prompt with profanity
    test4 = validate_prompt(employee, "This damn report is taking forever to finish")
    print(f"Profanity: PASSED={test4['passed']}, Violations={test4['violations']}")

    # Prompt with blocked topic
    test5 = validate_prompt(employee, "Give me legal advice on this contract dispute")
    print(f"Blocked topic: PASSED={test5['passed']}, Violations={test5['violations']}")

    print("\n" + "=" * 60)
    print("6. EMPLOYEE SETTINGS SUMMARY")
    print("=" * 60)
    summary = get_settings_summary(employee)
    for k, v in summary["active_limitations"].items():
        print(f"  {k}: {v}")

    print("\n" + "=" * 60)
    print("7. MANAGER TRIES COMPANY-WIDE (SHOULD FAIL)")
    print("=" * 60)
    fail = set_company_settings(manager, {"block_profanity": False})
    print(f"Result: {fail}")

    print("\n" + "=" * 60)
    print("8. EMPLOYEE TRIES TO SET SETTINGS (SHOULD FAIL)")
    print("=" * 60)
    fail2 = add_blocked_keywords(employee, ["test"], scope="department")
    print(f"Result: {fail2}")