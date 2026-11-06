"""
AI module: Complaint priority assignment.

assign_priority(category, description) -> str
Returns: 'High', 'Medium', or 'Low'
"""

# Default priority per category
CATEGORY_DEFAULT_PRIORITY = {
    "Road Damage": "High",
    "Drainage": "High",
    "Water Leakage": "High",
    "Garbage": "Medium",
    "Streetlight": "Medium",
    "Other": "Low",
}

# Keywords that escalate any complaint to High priority
URGENCY_KEYWORDS = [
    "accident", "injury", "injured", "dangerous", "emergency", "urgent", "critical",
    "flooding", "flood", "burst", "no water", "water outage", "electrocution",
    "fire", "collapse", "broken", "major", "severe", "immediate", "risk",
    "child", "hospital", "death", "dead", "overflow", "sewage overflow",
]

# Keywords that de-escalate to Low
MINOR_KEYWORDS = [
    "minor", "small", "little", "slight", "paint", "cosmetic", "aesthetic",
]


def assign_priority(category: str, description: str) -> str:
    """
    Determine priority:
    1. Start with the category default.
    2. Scan description for urgency keywords → escalate to High.
    3. Scan description for minor keywords and no urgency → de-escalate to Low.
    """
    base = CATEGORY_DEFAULT_PRIORITY.get(category, "Medium")
    desc_lower = description.lower()

    # Urgency override → always High
    for kw in URGENCY_KEYWORDS:
        if kw in desc_lower:
            return "High"

    # Minor override → only if base is not already High
    if base != "High":
        for kw in MINOR_KEYWORDS:
            if kw in desc_lower:
                return "Low"

    return base


if __name__ == "__main__":
    # Smoke tests
    assert assign_priority("Road Damage", "pothole causing accidents") == "High"  # urgency kw
    assert assign_priority("Garbage", "garbage near park") == "Medium"            # category default
    assert assign_priority("Other", "minor paint issue on wall") == "Low"         # minor kw
    assert assign_priority("Water Leakage", "burst pipe flooding street") == "High"
    assert assign_priority("Streetlight", "small light issue") == "Low"           # minor kw on Medium base
    assert assign_priority("Drainage", "severe flooding of road") == "High"
    print("priority.py: All smoke tests passed OK")
