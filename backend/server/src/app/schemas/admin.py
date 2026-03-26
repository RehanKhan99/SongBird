from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_workers: int
    active_policies: int
    active_triggers: int
    pending_review_claims: int  # CONDITIONAL + HOLD
