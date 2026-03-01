"""
Scorecard & Analytics Service.

calculateDepartmentScore, assignScorecardColor, getDepartmentBreakdown,
getTopOffenders, getTrendAnalysis, getCompanyWideScorecard,
getRiskCategoryDistribution, compareDepartments, getShadowModeImpactReport,
getTrainingCorrelationReport, generateExecutiveBriefing.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from shared.enums import SeverityColor
from services.watchtower.logging_service import _prompt_events


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _filter_events(
    events: list[dict],
    department_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[dict]:
    """Return a filtered copy of events based on department and date range."""
    filtered = events[:]
    if department_id:
        filtered = [e for e in filtered if e.get("department_id") == department_id]
    if date_from:
        filtered = [e for e in filtered if e.get("created_at", "") >= date_from]
    if date_to:
        filtered = [e for e in filtered if e.get("created_at", "") <= date_to]
    return filtered


_SEVERITY_WEIGHT = {
    SeverityColor.RED.value: 10,
    SeverityColor.ORANGE.value: 5,
    SeverityColor.YELLOW.value: 1,
}

_ACTION_WEIGHT = {
    "BLOCKED": 10,
    "REWRITTEN": 5,
    "ALLOWED_WITH_WARNING": 2,
    "SHADOW_LOGGED": 3,
    "ALLOWED": 0,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def calculate_department_score(
    department_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> float:
    """Aggregate risk events into a department score (0-100 scale).

    The score is a weighted sum of events normalised so that a department
    with no events scores 0 and one with many severe events approaches 100.
    """
    events = _filter_events(_prompt_events, department_id, date_from, date_to)
    if not events:
        return 0.0

    total_weight = 0.0
    for e in events:
        severity_w = _SEVERITY_WEIGHT.get(e.get("severity_color", ""), 1)
        action_w = _ACTION_WEIGHT.get(e.get("action_taken", ""), 0)
        total_weight += severity_w + action_w

    # Normalise: cap at 100.  Each event can contribute up to 20 points,
    # so we scale by (count * 20) to keep the score in 0-100.
    max_possible = len(events) * 20
    score = (total_weight / max_possible) * 100 if max_possible else 0.0
    return round(min(score, 100.0), 2)


def assign_scorecard_color(department_score: float) -> str:
    """Map department score to Yellow, Orange, or Red."""
    if department_score >= 70:
        return SeverityColor.RED.value
    elif department_score >= 40:
        return SeverityColor.ORANGE.value
    else:
        return SeverityColor.YELLOW.value


async def get_department_breakdown(
    department_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    """Counts by action type for a department."""
    events = _filter_events(_prompt_events, department_id, date_from, date_to)
    counts = {"blocked": 0, "rewritten": 0, "warned": 0, "allowed": 0, "shadow_logged": 0}
    action_map = {
        "BLOCKED": "blocked",
        "REWRITTEN": "rewritten",
        "ALLOWED_WITH_WARNING": "warned",
        "ALLOWED": "allowed",
        "SHADOW_LOGGED": "shadow_logged",
    }
    for e in events:
        key = action_map.get(e.get("action_taken", ""), "allowed")
        counts[key] += 1
    return counts


async def get_top_offenders(
    department_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 10,
) -> list[dict]:
    """Highest flag counts in a department."""
    events = _filter_events(_prompt_events, department_id, date_from, date_to)
    # Only count events where some action was taken (not plain ALLOWED)
    flagged = [e for e in events if e.get("action_taken") != "ALLOWED"]
    user_counts: dict[str, int] = defaultdict(int)
    for e in flagged:
        user_counts[e["user_id"]] += 1

    sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)
    return [
        {"user_id": uid, "flag_count": count}
        for uid, count in sorted_users[:limit]
    ]


async def get_trend_analysis(
    department_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> list[dict]:
    """Behavioral trends over time -- data formatted for Recharts.

    Groups events by date and returns daily counts of flagged vs total.
    """
    events = _filter_events(_prompt_events, department_id, date_from, date_to)
    if not events:
        return []

    daily: dict[str, dict] = defaultdict(lambda: {"total": 0, "flagged": 0})
    for e in events:
        day = e.get("created_at", "")[:10]  # YYYY-MM-DD
        daily[day]["total"] += 1
        if e.get("action_taken") != "ALLOWED":
            daily[day]["flagged"] += 1

    return [
        {"date": day, "total": data["total"], "flagged": data["flagged"]}
        for day, data in sorted(daily.items())
    ]


async def get_company_wide_scorecard() -> list[dict]:
    """All departments in one view."""
    dept_ids: set[str] = {e.get("department_id", "") for e in _prompt_events}
    results = []
    for dept_id in sorted(dept_ids):
        score = await calculate_department_score(dept_id)
        color = assign_scorecard_color(score)
        breakdown = await get_department_breakdown(dept_id)
        results.append({
            "department_id": dept_id,
            "score": score,
            "color": color,
            "breakdown": breakdown,
        })
    return results


async def get_risk_category_distribution(
    department_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    """Which data types triggered most flags -- formatted for Recharts pie chart."""
    events = _filter_events(_prompt_events, department_id, date_from, date_to)
    dist: dict[str, int] = defaultdict(int)
    for e in events:
        cat = e.get("risk_category", "GENERAL")
        dist[cat] += 1
    return dict(dist)


async def compare_departments(
    department_ids: list[str],
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> list[dict]:
    """Side-by-side department comparison."""
    results = []
    for dept_id in department_ids:
        score = await calculate_department_score(dept_id, date_from, date_to)
        breakdown = await get_department_breakdown(dept_id, date_from, date_to)
        top = await get_top_offenders(dept_id, date_from, date_to, limit=5)
        results.append({
            "department_id": dept_id,
            "score": score,
            "color": assign_scorecard_color(score),
            "breakdown": breakdown,
            "top_offenders": top,
        })
    return results


async def get_shadow_mode_impact_report(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    """Projected impact of full enforcement based on shadow-mode logs."""
    events = _filter_events(_prompt_events, date_from=date_from, date_to=date_to)
    shadow_events = [e for e in events if e.get("deployment_mode") == "SHADOW"]

    projected_blocks = sum(
        1 for e in shadow_events if e.get("action_taken") in ("BLOCKED", "SHADOW_LOGGED")
        and e.get("risk_score", 0) >= 70
    )
    projected_rewrites = sum(
        1 for e in shadow_events if e.get("action_taken") in ("REWRITTEN", "SHADOW_LOGGED")
        and 40 <= e.get("risk_score", 0) < 70
    )
    total = len(shadow_events) if shadow_events else 1  # avoid div-by-zero
    impact_score = round(((projected_blocks + projected_rewrites) / total) * 100, 2)

    return {
        "total_shadow_events": len(shadow_events),
        "projected_blocks": projected_blocks,
        "projected_rewrites": projected_rewrites,
        "impact_score": impact_score,
    }


async def get_training_correlation_report(
    department_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    """Training completion vs flag reduction -- formatted for Recharts.

    Since training data is tracked separately (training_service), this function
    imports the in-memory stores from both services and computes a simple
    correlation: users who completed training vs. their subsequent flag rate.
    """
    from services.watchtower.training_service import _training_completions, _training_assignments

    events = _filter_events(_prompt_events, department_id, date_from, date_to)
    if not events:
        return {"correlation": 0.0, "data_points": []}

    # Build set of users who completed training
    trained_users = {c["user_id"] for c in _training_completions}

    # Per-user flag counts split by trained / untrained
    user_flags: dict[str, int] = defaultdict(int)
    for e in events:
        if e.get("action_taken") != "ALLOWED":
            user_flags[e["user_id"]] += 1

    data_points = []
    for uid, count in user_flags.items():
        data_points.append({
            "user_id": uid,
            "flag_count": count,
            "training_completed": uid in trained_users,
        })

    # Simple correlation metric: average flags for trained vs untrained
    trained_flags = [d["flag_count"] for d in data_points if d["training_completed"]]
    untrained_flags = [d["flag_count"] for d in data_points if not d["training_completed"]]
    avg_trained = sum(trained_flags) / len(trained_flags) if trained_flags else 0
    avg_untrained = sum(untrained_flags) / len(untrained_flags) if untrained_flags else 0

    # correlation is the reduction ratio: positive means training helps
    if avg_untrained > 0:
        correlation = round((avg_untrained - avg_trained) / avg_untrained, 2)
    else:
        correlation = 0.0

    return {"correlation": correlation, "data_points": data_points}


async def generate_executive_briefing(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    """One-page leadership summary."""
    events = _filter_events(_prompt_events, date_from=date_from, date_to=date_to)
    total = len(events)
    flagged = [e for e in events if e.get("action_taken") != "ALLOWED"]
    flagged_pct = round((len(flagged) / total) * 100, 2) if total else 0.0

    # Top risk category
    cat_counts: dict[str, int] = defaultdict(int)
    for e in events:
        cat_counts[e.get("risk_category", "GENERAL")] += 1
    top_risk_cat = max(cat_counts, key=cat_counts.get) if cat_counts else "N/A"

    # Departments at risk (score >= 40)
    dept_ids = {e.get("department_id", "") for e in events}
    at_risk = []
    for dept_id in dept_ids:
        score = await calculate_department_score(dept_id, date_from, date_to)
        if score >= 40:
            at_risk.append({"department_id": dept_id, "score": score})

    # Training completion rate (from training service)
    from services.watchtower.training_service import _training_assignments, _training_completions
    total_assigned = len(_training_assignments)
    total_completed = len(_training_completions)
    training_rate = round((total_completed / total_assigned) * 100, 2) if total_assigned else 0.0

    # Recommendation
    if not events:
        recommendation = "System in shadow mode -- collecting baseline data."
    elif flagged_pct > 30:
        recommendation = "High flag rate detected. Consider targeted training and stricter policy enforcement."
    elif flagged_pct > 10:
        recommendation = "Moderate activity. Continue monitoring; some departments may benefit from focused training."
    else:
        recommendation = "Low risk activity. Current policies are effective."

    return {
        "total_prompts": total,
        "flagged_prompts": len(flagged),
        "flagged_percentage": flagged_pct,
        "top_risk_category": top_risk_cat,
        "departments_at_risk": at_risk,
        "training_completion_rate": training_rate,
        "recommendation": recommendation,
    }
