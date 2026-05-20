class LoanStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


VALID_ROLES = {"admin", "super_user"}
SCORE_MIN = 200
SCORE_MAX = 950
MANUAL_REVIEW_WEIGHT = 0.5
