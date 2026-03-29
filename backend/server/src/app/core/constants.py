# ML constants from models_deep_dive.md

# M1: Tier base premiums (₹/week)
# Status/type enums live in schemas
# 
# only constants from ml belong here
TIER_BASE_PREMIUM: dict[str, float] = {
    "BASIC": 79.0,
    "STANDARD": 149.0,
    "PREMIUM": 249.0,
}
