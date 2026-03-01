"""
scorecard_service.py
Scorecard & Analytics Service — department scores, trends, comparisons,
and executive briefings that feed into Recharts dashboards.
"""

from datetime import datetime
from config import supabase
from models import SeverityColor, DateRangeParams, DepartmentScore


FLAG_TABLE = "flag_events"
COMPLETION_TABLE = "training_completions"
SHADOW_TABLE = "shadow_mode_events"


# ── Helpers ──────────────────────────────────────────────────────────────

def _query_flags(
    date_range: DateRangeParams,
    department_id: str | None = None,
) -> list[dict]:
    q = (
        supabase.table(FLAG_TABLE)
        .select("*")
        .gte("timestamp", date_range.start.isoformat())
        .lte("timestamp", date_range.end.isoformat())
    )
    if department_id:
        q = q.eq("department_id", department_id)
    return q.execute().data


def _score_to_color(score: float) -> SeverityColor:
    """Map numeric score to severity color."""
    if score >= 80:
        return SeverityColor.YELLOW   # healthy
    if score >= 50:
        return SeverityColor.ORANGE   # caution
    return SeverityColor.RED          # critical


# ── Department Scorecard ─────────────────────────────────────────────────

def calculate_department_score(
    department_id: str, date_range: DateRangeParams
) -> DepartmentScore:
    """
    Aggregate risk events into a 0-100 score.
    Scoring: start at 100, deduct per event weighted by severity.
    """
    rows = _query_flags(date_range, department_id)
    deductions = {"yellow": 1, "orange": 3, "red": 10}
    total_deduction = sum(
        deductions.get(r.get("severity_color", "yellow"), 1)
        for r in rows
    )
    score = max(0.0, 100.0 - total_deduction)
    return DepartmentScore(
        department_id=department_id,
        score=round(score, 1),
        color=_score_to_color(score),
        total_events=len(rows),
        date_range_start=date_range.start,
        date_range_end=date_range.end,
    )


def assign_scorecard_color(score: float) -> SeverityColor:
    return _score_to_color(score)


def get_department_breakdown(
    department_id: str, date_range: DateRangeParams
) -> dict[str, int]:
    """Counts by action type."""
    rows = _query_flags(date_range, department_id)
    breakdown: dict[str, int] = {}
    for r in rows:
        action = r.get("action_taken", "unknown")
        breakdown[action] = breakdown.get(action, 0) + 1
    return breakdown


def get_top_offenders(
    department_id: str, date_range: DateRangeParams, limit: int = 10
) -> list[dict]:
    """Highest flag counts within a department."""
    rows = _query_flags(date_range, department_id)
    counts: dict[str, int] = {}
    for r in rows:
        uid = r.get("user_id", "unknown")
        counts[uid] = counts.get(uid, 0) + 1
    sorted_users = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [
        {"user_id": uid, "flag_count": c}
        for uid, c in sorted_users[:limit]
    ]


def get_trend_analysis(
    department_id: str, date_range: DateRangeParams
) -> list[dict]:
    """Weekly trend for Recharts line chart."""
    rows = _query_flags(date_range, department_id)
    buckets: dict[str, int] = {}
    for r in rows:
        ts = datetime.fromisoformat(r["timestamp"])
        week = ts.strftime("%Y-W%W")
        buckets[week] = buckets.get(week, 0) + 1
    return [{"week": k, "count": v} for k, v in sorted(buckets.items())]


def get_risk_category_distribution(
    department_id: str, date_range: DateRangeParams
) -> dict[str, int]:
    """Which data types triggered most (for Recharts pie chart)."""
    rows = _query_flags(date_range, department_id)
    dist: dict[str, int] = {}
    for r in rows:
        cat = r.get("risk_category", "unknown")
        dist[cat] = dist.get(cat, 0) + 1
    return dist


# ── Cross-Department ─────────────────────────────────────────────────────

def get_company_wide_scorecard(date_range: DateRangeParams) -> list[dict]:
    """All departments in one view."""
    rows = _query_flags(date_range)
    depts: set[str] = {r.get("department_id", "unknown") for r in rows}
    return [
        calculate_department_score(d, date_range).model_dump(mode="json")
        for d in sorted(depts)
    ]


def compare_departments(
    department_ids: list[str], date_range: DateRangeParams
) -> list[dict]:
    return [
        calculate_department_score(d, date_range).model_dump(mode="json")
        for d in department_ids
    ]


# ── Shadow Mode & Training Correlation ───────────────────────────────────

def get_shadow_mode_impact_report(date_range: DateRangeParams) -> dict:
    """Projected impact if shadow mode events were enforced."""
    rows = (
        supabase.table(SHADOW_TABLE)
        .select("*")
        .gte("timestamp", date_range.start.isoformat())
        .lte("timestamp", date_range.end.isoformat())
        .execute()
        .data
    )
    return {
        "total_shadow_events": len(rows),
        "projected_blocks": sum(
            1 for r in rows
            if "block" in r.get("what_would_have_happened", "").lower()
        ),
        "projected_warns": sum(
            1 for r in rows
            if "warn" in r.get("what_would_have_happened", "").lower()
        ),
    }


def get_training_correlation_report(
    department_id: str, date_range: DateRangeParams
) -> dict:
    """Training completions vs flag reduction — high-level stats."""
    completions = (
        supabase.table(COMPLETION_TABLE)
        .select("*")
        .gte("completion_timestamp", date_range.start.isoformat())
        .lte("completion_timestamp", date_range.end.isoformat())
        .execute()
        .data
    )
    flags = _query_flags(date_range, department_id)
    return {
        "department_id": department_id,
        "total_trainings_completed": len(completions),
        "total_flags": len(flags),
        "ratio": (
            round(len(flags) / len(completions), 2) if completions else None
        ),
    }


def generate_executive_briefing(date_range: DateRangeParams) -> dict:
    """One-page leadership summary."""
    all_flags = _query_flags(date_range)
    scorecard = get_company_wide_scorecard(date_range)
    shadow = get_shadow_mode_impact_report(date_range)
    return {
        "period": {
            "start": date_range.start.isoformat(),
            "end": date_range.end.isoformat(),
        },
        "total_flag_events": len(all_flags),
        "department_scores": scorecard,
        "shadow_mode_impact": shadow,
        "generated_at": datetime.utcnow().isoformat(),
    }
