"""
AI module: Keyword-weighted category classifier.

classify(title, description) -> str
Returns one of: Garbage, Road Damage, Drainage, Water Leakage, Streetlight, Other
"""

CATEGORY_KEYWORDS = {
    "Garbage": [
        "garbage", "trash", "waste", "litter", "dump", "rubbish", "bin", "disposal",
        "smell", "odor", "filth", "dirty", "sewage smell", "rotting", "overflowing bin",
        "pile of garbage", "waste dump", "uncollected", "heap",
    ],
    "Road Damage": [
        "road", "pothole", "crack", "damaged road", "broken road", "uneven road",
        "street damage", "road surface", "asphalt", "pavement", "footpath", "sidewalk",
        "bump", "accident", "vehicle damage", "road repair", "tar", "highway", "lane",
        "road hole", "crater",
    ],
    "Drainage": [
        "drainage", "drain", "clog", "blocked drain", "overflow", "flooding", "flood",
        "waterlog", "stagnant water", "puddle", "sewage", "manhole", "gutter",
        "blocked", "water stagnation", "water overflow", "drain cover", "open drain",
    ],
    "Water Leakage": [
        "water leak", "leakage", "pipe leak", "burst pipe", "water pipe", "water supply",
        "no water", "water shortage", "water loss", "leak", "water pressure",
        "broken pipe", "water main", "tap", "water connection", "drinking water",
        "water outage", "pipeline",
    ],
    "Streetlight": [
        "streetlight", "street light", "light", "lamp", "lamppost", "dark", "darkness",
        "no light", "broken light", "light not working", "dim", "blackout",
        "power outage", "electricity", "bulb", "night", "unsafe at night", "lamp post",
    ],
}

# Minimum score to assign a category (prevent spurious matches)
_THRESHOLD = 2


def classify(title: str, description: str) -> str:
    """
    Score each category by counting keyword matches in (title + description).
    Title matches count double. Returns the highest-scoring category or 'Other'.
    """
    text_lower = (title + " " + description).lower()
    title_lower = title.lower()

    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in text_lower:
                score += 1
            if kw in title_lower:
                score += 1  # double-weight title
        scores[category] = score

    best_category = max(scores, key=scores.get)
    if scores[best_category] >= _THRESHOLD:
        return best_category
    return "Other"


if __name__ == "__main__":
    # Smoke tests
    assert classify("Pothole on MG Road", "There is a large pothole causing accidents") == "Road Damage"
    assert classify("Garbage pile near park", "Huge garbage dump near children park, bad smell") == "Garbage"
    assert classify("Broken streetlight", "The street lamp near bus stop is not working since last week") == "Streetlight"
    assert classify("Water pipe burst", "Water is leaking from broken pipe, flooding the road") == "Water Leakage"
    assert classify("Drain blocked", "The drainage near my house is clogged and causing water stagnation") == "Drainage"
    assert classify("General complaint", "I have a complaint") == "Other"
    print("classifier.py: All smoke tests passed OK")
