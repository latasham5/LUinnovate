"""
Dashboard routes — scorecard analytics, department data, trend analysis.
"""

from fastapi import APIRouter, Depends
from typing import Optional
from api.dependencies import require_elevated
from services.watchtower.scorecard_service import (
    calculate_department_score,
    assign_scorecard_color,
    get_department_breakdown as _get_department_breakdown,
    get_top_offenders as _get_top_offenders,
    get_trend_analysis as _get_trend_analysis,
    get_company_wide_scorecard as _get_company_wide_scorecard,
    get_risk_category_distribution as _get_risk_category_distribution,
    compare_departments as _compare_departments,
    get_shadow_mode_impact_report as _get_shadow_mode_impact_report,
    get_training_correlation_report as _get_training_correlation_report,
    generate_executive_briefing as _generate_executive_briefing,
)

router = APIRouter()


@router.get("/scorecard/company")
async def get_company_scorecard(current_user: dict = Depends(require_elevated)):
    """All departments in one view."""
    departments = await _get_company_wide_scorecard()
    return {"departments": departments}


@router.get("/scorecard/department/{department_id}")
async def get_department_score(department_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None, current_user: dict = Depends(require_elevated)):
    """Department score and breakdown."""
    score = await calculate_department_score(department_id, date_from, date_to)
    color = assign_scorecard_color(score)
    breakdown = await _get_department_breakdown(department_id, date_from, date_to)
    return {"department_id": department_id, "score": score, "color": color, "breakdown": breakdown}


@router.get("/department/{department_id}/breakdown")
async def get_department_breakdown(department_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None, current_user: dict = Depends(require_elevated)):
    """Counts by action type for a department."""
    breakdown = await _get_department_breakdown(department_id, date_from, date_to)
    return {"department_id": department_id, "breakdown": breakdown}


@router.get("/department/{department_id}/top-offenders")
async def get_top_offenders(department_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None, current_user: dict = Depends(require_elevated)):
    """Highest flag counts in a department."""
    offenders = await _get_top_offenders(department_id, date_from, date_to)
    return {"department_id": department_id, "offenders": offenders}


@router.get("/department/{department_id}/trends")
async def get_trend_analysis(department_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None, current_user: dict = Depends(require_elevated)):
    """Behavioral trends over time."""
    trends = await _get_trend_analysis(department_id, date_from, date_to)
    return {"department_id": department_id, "trends": trends}


@router.get("/department/{department_id}/risk-distribution")
async def get_risk_distribution(department_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None, current_user: dict = Depends(require_elevated)):
    """Which data types triggered most flags."""
    distribution = await _get_risk_category_distribution(department_id, date_from, date_to)
    return {"department_id": department_id, "distribution": distribution}


@router.get("/compare")
async def compare_departments(department_ids: str, date_from: Optional[str] = None, date_to: Optional[str] = None, current_user: dict = Depends(require_elevated)):
    """Side-by-side department comparison. department_ids is comma-separated."""
    ids = [d.strip() for d in department_ids.split(",")]
    comparison = await _compare_departments(ids, date_from, date_to)
    return {"departments": ids, "comparison": comparison}


@router.get("/shadow-impact")
async def get_shadow_impact(date_from: Optional[str] = None, date_to: Optional[str] = None, current_user: dict = Depends(require_elevated)):
    """Projected impact of full enforcement."""
    impact = await _get_shadow_mode_impact_report(date_from, date_to)
    return {"impact": impact}


@router.get("/training-correlation/{department_id}")
async def get_training_correlation(department_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None, current_user: dict = Depends(require_elevated)):
    """Training completion vs flag reduction."""
    correlation = await _get_training_correlation_report(department_id, date_from, date_to)
    return {"department_id": department_id, "correlation": correlation}


@router.get("/executive-briefing")
async def get_executive_briefing(date_from: Optional[str] = None, date_to: Optional[str] = None, current_user: dict = Depends(require_elevated)):
    """One-page leadership summary."""
    briefing = await _generate_executive_briefing(date_from, date_to)
    return {"briefing": briefing}
