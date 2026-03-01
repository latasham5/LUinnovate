"""
Developer 2 - The Enforcer
===========================
Top-level package containing:
  - auth_service        → Authentication & Authorization
  - policy_service      → Policy Management
  - action_service      → Action Execution (executes Dev 1 decisions)
  - shadow_mode_service → Shadow Mode Management

Usage from parent project:
    from developer_2_enforcer.auth_service import validate_sso_token
    from developer_2_enforcer.policy_service import get_active_policies
    from developer_2_enforcer.action_service import block_prompt
    from developer_2_enforcer.shadow_mode_service import get_deployment_mode
"""

__version__ = "1.0.0"
__developer__ = "Developer 2 - The Enforcer"