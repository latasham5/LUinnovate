"""
Prompt Interception & Analysis Engine — the entry point for all prompts.

receivePrompt() accepts every prompt from the frontend.
runComprehensiveScan() orchestrates all detectors in parallel and aggregates results.
"""

import time
from typing import Optional
from shared.schemas.analysis_result import AnalysisResult, DetectedElement
from shared.schemas.policy_context import PolicyContext
from shared.schemas.user_history import UserHistory
from shared.enums import ActionType
from services.gatekeeper.detectors.keyword_extractor import extract_keywords
from services.gatekeeper.detectors.numeric_extractor import extract_numeric_data
from services.gatekeeper.detectors.intent_classifier import classify_intent
from services.gatekeeper.detectors.pii_detector import detect_pii
from services.gatekeeper.detectors.credential_detector import detect_credentials
from services.gatekeeper.detectors.financial_detector import detect_financial_data
from services.gatekeeper.detectors.customer_info_detector import detect_customer_information
from services.gatekeeper.detectors.code_name_detector import detect_internal_code_names
from services.gatekeeper.detectors.regulated_content_detector import detect_regulated_content
from services.gatekeeper.detectors.risky_intent_detector import detect_risky_intent
from services.gatekeeper.risk_classifier import classify_risk, calculate_risk_score, map_risk_to_severity
from services.gatekeeper.rewrite_engine import generate_safer_rewrite
from services.gatekeeper.action_determiner import determine_action


async def receive_prompt(
    user_id: str,
    raw_prompt: str,
    timestamp: str,
    policy_context: PolicyContext,
    user_history: Optional[UserHistory] = None,
) -> AnalysisResult:
    """
    Entry point that accepts every prompt from the frontend.

    Orchestrates the full analysis pipeline:
    1. Run comprehensive scan (all detectors)
    2. Classify risk and calculate score
    3. Generate safer rewrite if needed
    4. Determine final action
    """
    start_time = time.time()

    # Step 1: Run all detectors
    scan_results = await run_comprehensive_scan(raw_prompt, policy_context.policy_mode.value)

    # Step 2: Classify risk
    detected_categories = classify_risk(scan_results["detected_elements"])
    risk_score = calculate_risk_score(
        detected_categories=detected_categories,
        data_volume=len(scan_results["detected_elements"]),
        user_role=policy_context.user_profile.role,
        policy_mode=policy_context.policy_mode.value,
        user_history=user_history,
    )
    severity_color = map_risk_to_severity(risk_score, policy_context.thresholds)

    # Step 3: Determine action
    action = determine_action(
        risk_score=risk_score,
        policy_rules=policy_context.active_policies,
        policy_mode=policy_context.policy_mode.value,
        deployment_mode=policy_context.deployment_mode.value,
    )

    # Step 4: Generate rewrite if action is REWRITTEN
    rewritten_prompt = None
    rewrite_explanation = None
    if action == ActionType.REWRITTEN:
        rewrite_result = generate_safer_rewrite(
            raw_prompt=raw_prompt,
            flagged_elements=scan_results["detected_elements"],
            risk_categories=detected_categories,
        )
        rewritten_prompt = rewrite_result["safer_prompt"]
        rewrite_explanation = rewrite_result["explanation"]

    # Build result
    elapsed_ms = (time.time() - start_time) * 1000

    return AnalysisResult(
        detected_elements=scan_results["detected_elements"],
        detected_categories=detected_categories,
        intent=scan_results["intent"],
        risk_score=risk_score,
        severity_color=severity_color,
        confidence_level=scan_results["confidence"],
        recommended_action=action,
        rewritten_prompt=rewritten_prompt,
        rewrite_explanation=rewrite_explanation,
        detectors_run=scan_results["detectors_run"],
        scan_duration_ms=elapsed_ms,
    )


async def run_comprehensive_scan(raw_prompt: str, policy_mode: str) -> dict:
    """
    Orchestrator that calls all detection functions and aggregates results.
    In production, these run in parallel via asyncio.gather().
    """
    detected_elements: list[DetectedElement] = []
    detectors_run = []

    # Run all detectors
    # Each detector returns a list of DetectedElement objects

    keywords = extract_keywords(raw_prompt)
    detected_elements.extend(keywords)
    detectors_run.append("keyword_extractor")

    numeric = extract_numeric_data(raw_prompt)
    detected_elements.extend(numeric)
    detectors_run.append("numeric_extractor")

    intent = await classify_intent(raw_prompt)
    detectors_run.append("intent_classifier")

    pii = detect_pii(raw_prompt)
    detected_elements.extend(pii)
    detectors_run.append("pii_detector")

    credentials = detect_credentials(raw_prompt)
    detected_elements.extend(credentials)
    detectors_run.append("credential_detector")

    financial = detect_financial_data(raw_prompt)
    detected_elements.extend(financial)
    detectors_run.append("financial_detector")

    customer = detect_customer_information(raw_prompt)
    detected_elements.extend(customer)
    detectors_run.append("customer_info_detector")

    code_names = detect_internal_code_names(raw_prompt)
    detected_elements.extend(code_names)
    detectors_run.append("code_name_detector")

    regulated = detect_regulated_content(raw_prompt)
    detected_elements.extend(regulated)
    detectors_run.append("regulated_content_detector")

    risky_intent = await detect_risky_intent(raw_prompt)
    detectors_run.append("risky_intent_detector")

    # Calculate overall confidence
    from services.gatekeeper.risk_classifier import calculate_confidence
    confidence = calculate_confidence(detected_elements)

    return {
        "detected_elements": detected_elements,
        "intent": intent,
        "risky_intent_score": risky_intent,
        "confidence": confidence,
        "detectors_run": detectors_run,
    }
