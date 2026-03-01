"""
Safer Prompt Rewrite Engine — sanitizes prompts by replacing sensitive data.

generateSaferRewrite, replaceNames, replaceEmails, replaceAccountIds,
replaceFinancialFigures, replaceCredentials, replaceInternalCodeNames,
convertDataPasteToStructure, generateRewriteExplanation, validateRewrite.
"""

import re
from shared.schemas.analysis_result import DetectedElement
from shared.enums import RiskCategory


def generate_safer_rewrite(
    raw_prompt: str,
    flagged_elements: list[DetectedElement],
    risk_categories: list[RiskCategory],
) -> dict:
    """
    Master function that produces the sanitized prompt.
    Applies all relevant replacement functions based on detected categories.
    Returns the safer prompt and explanation of changes.
    """
    safer_prompt = raw_prompt
    transformations = []

    # Sort elements by start_index descending so replacements don't shift indices
    sorted_elements = sorted(flagged_elements, key=lambda e: e.start_index, reverse=True)

    for element in sorted_elements:
        original_text = element.text
        replacement = _get_replacement(element)

        safer_prompt = safer_prompt[:element.start_index] + replacement + safer_prompt[element.end_index:]
        transformations.append(f"Replaced '{original_text}' with '{replacement}' ({element.category.value})")

    explanation = generate_rewrite_explanation(raw_prompt, safer_prompt, transformations)

    return {
        "safer_prompt": safer_prompt,
        "explanation": explanation,
        "transformations": transformations,
    }


def _get_replacement(element: DetectedElement) -> str:
    """Get the appropriate replacement string for a detected element."""
    replacements = {
        RiskCategory.PII: _get_pii_replacement(element.text),
        RiskCategory.CREDENTIALS: "[REDACTED_CREDENTIAL]",
        RiskCategory.FINANCIAL: "[FINANCIAL_FIGURE]",
        RiskCategory.CUSTOMER_INFO: "[CUSTOMER_DATA]",
        RiskCategory.INTERNAL_CODE_NAME: "[INTERNAL_PROJECT]",
        RiskCategory.PROPRIETARY: "[PROPRIETARY_INFO]",
        RiskCategory.REGULATED: "[REGULATED_CONTENT]",
        RiskCategory.GENERAL: element.text,  # No replacement for general
    }
    return replacements.get(element.category, "[REDACTED]")


def _get_pii_replacement(text: str) -> str:
    """Determine the specific PII replacement token."""
    if "@" in text:
        return "[EMAIL_ADDRESS]"
    elif re.match(r"\d{3}[-.]?\d{3}[-.]?\d{4}", text):
        return "[PHONE_NUMBER]"
    elif re.match(r"\d{3}-\d{2}-\d{4}", text):
        return "[SSN]"
    elif re.match(r"\d{8,16}", text):
        return "[ACCOUNT_ID]"
    else:
        return "[PERSON_NAME]"


def replace_names(raw_prompt: str, detected_names: list[DetectedElement]) -> str:
    """Swap real names with [CUSTOMER_NAME] or [EMPLOYEE_NAME]."""
    result = raw_prompt
    for name in sorted(detected_names, key=lambda e: e.start_index, reverse=True):
        result = result[:name.start_index] + "[PERSON_NAME]" + result[name.end_index:]
    return result


def replace_emails(raw_prompt: str, detected_emails: list[DetectedElement]) -> str:
    """Swap email addresses with [EMAIL_ADDRESS]."""
    result = raw_prompt
    for email in sorted(detected_emails, key=lambda e: e.start_index, reverse=True):
        result = result[:email.start_index] + "[EMAIL_ADDRESS]" + result[email.end_index:]
    return result


def replace_account_ids(raw_prompt: str, detected_ids: list[DetectedElement]) -> str:
    """Swap account IDs with [ACCOUNT_ID]."""
    result = raw_prompt
    for aid in sorted(detected_ids, key=lambda e: e.start_index, reverse=True):
        result = result[:aid.start_index] + "[ACCOUNT_ID]" + result[aid.end_index:]
    return result


def replace_financial_figures(raw_prompt: str, detected_numbers: list[DetectedElement]) -> str:
    """Replace exact financial numbers with ranges or mock values."""
    result = raw_prompt
    for num in sorted(detected_numbers, key=lambda e: e.start_index, reverse=True):
        result = result[:num.start_index] + "[FINANCIAL_FIGURE]" + result[num.end_index:]
    return result


def replace_credentials(raw_prompt: str, detected_credentials: list[DetectedElement]) -> str:
    """Completely remove and replace credentials with [REDACTED_CREDENTIAL]."""
    result = raw_prompt
    for cred in sorted(detected_credentials, key=lambda e: e.start_index, reverse=True):
        result = result[:cred.start_index] + "[REDACTED_CREDENTIAL]" + result[cred.end_index:]
    return result


def replace_internal_code_names(raw_prompt: str, detected_code_names: list[DetectedElement]) -> str:
    """Swap internal code names with generalized descriptions."""
    result = raw_prompt
    for cn in sorted(detected_code_names, key=lambda e: e.start_index, reverse=True):
        result = result[:cn.start_index] + "[INTERNAL_PROJECT]" + result[cn.end_index:]
    return result


def convert_data_paste_to_structure(raw_prompt: str) -> str:
    """Transform raw data pastes into structural descriptions."""
    # TODO: Detect tabular/CSV data and convert to schema descriptions
    return raw_prompt


def generate_rewrite_explanation(original: str, safer: str, transformations: list[str]) -> list[str]:
    """Produce the bullet-point list explaining each change."""
    if not transformations:
        return ["No changes were necessary."]
    return transformations


def validate_rewrite(safer_prompt: str) -> bool:
    """Run the safer version back through detection to confirm it passes."""
    # TODO: Re-run detectors on the safer prompt
    # TODO: Return True only if no sensitive elements remain
    return True
