# ML constants from models_deep_dive.md

# M1: Tier base premiums (₹/week)
TIER_BASE_PREMIUM: dict[str, float] = {
    "BASIC": 79.0,
    "STANDARD": 149.0,
    "PREMIUM": 249.0,
}

# Policy status vals : used in queries and model defaults
POLICY_STATUS_ACTIVE = "ACTIVE"
POLICY_STATUS_CANCELLED = "CANCELLED"
POLICY_STATUS_EXPIRED = "EXPIRED"

# Trigger event status vals
TRIGGER_STATUS_ACTIVE = "ACTIVE"
TRIGGER_STATUS_CLOSED = "CLOSED"

# Worker KYC status vals
KYC_STATUS_MOCK = "mock_verified"
