"""
Developer 2 - The Enforcer
===========================
Top-level package containing:
  - auth_service          → Authentication & Authorization
  - policy_service        → Policy Management
  - action_service        → Action Execution (executes Dev 1 decisions)
  - shadow_mode_service   → Shadow Mode Management
  - settings_service      → Limitation Settings (admin/manager controls)

Usage from parent project:
    from developer_2.auth_service import validate_sso_token
    from developer_2.policy_service import get_active_policies
    from developer_2.action_service import block_prompt
    from developer_2.shadow_mode_service import get_deployment_mode
    from developer_2.settings_service import validate_prompt, set_company_settings
"""

__version__ = "1.1.0"
__developer__ = "Developer 2 - The Enforcer"