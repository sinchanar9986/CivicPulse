"""
AI module: Duplicate complaint detection using TF-IDF + cosine similarity.

find_duplicate(title, description, existing_complaints, threshold) -> (bool, int|None, float)
Returns (is_duplicate, original_complaint_id, similarity_score)
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DEFAULT_THRESHOLD = 0.75


def _build_document(title: str, description: str) -> str:
    """Combine title (weighted 2x) and description into one document string."""
    return f"{title} {title} {description}".strip().lower()


def find_duplicate(title: str, description: str, existing_complaints, threshold: float = DEFAULT_THRESHOLD):
    """
    Check whether (title, description) is a near-duplicate of any complaint
    in existing_complaints.

    Parameters
    ----------
    title : str
    description : str
    existing_complaints : list of objects with .id, .title, .description attributes
    threshold : float  cosine similarity threshold (default 0.75)

    Returns
    -------
    (is_duplicate: bool, original_id: int|None, score: float)
    """
    if not existing_complaints:
        return False, None, 0.0

    new_doc = _build_document(title, description)
    existing_docs = [_build_document(c.title, c.description) for c in existing_complaints]

    # Vectorize all documents together
    corpus = existing_docs + [new_doc]
    try:
        vectorizer = TfidfVectorizer(stop_words="english", min_df=1)
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        # Corpus has no usable terms (e.g. all stop words)
        return False, None, 0.0

    # New doc is the last row; compare against all existing
    new_vec = tfidf_matrix[-1]
    existing_matrix = tfidf_matrix[:-1]
    similarities = cosine_similarity(new_vec, existing_matrix).flatten()

    max_idx = similarities.argmax()
    max_score = float(similarities[max_idx])

    if max_score >= threshold:
        return True, existing_complaints[max_idx].id, round(max_score, 4)
    return False, None, round(max_score, 4)


if __name__ == "__main__":
    # Smoke tests using simple mock objects
    class MockComplaint:
        def __init__(self, cid, title, description):
            self.id = cid
            self.title = title
            self.description = description

    existing = [
        MockComplaint(1, "Pothole on MG Road", "Large pothole near signal causing accidents on MG Road"),
        MockComplaint(2, "Garbage dump near park", "Uncollected garbage near children park smells bad"),
    ]

    # Near-duplicate of complaint #1
    is_dup, orig_id, score = find_duplicate(
        "Pothole on MG Road Bengaluru",
        "There is a big pothole near the signal on MG Road causing accidents",
        existing,
    )
    assert is_dup is True, f"Expected duplicate, got score={score}"
    assert orig_id == 1

    # Clearly different complaint
    is_dup2, orig_id2, score2 = find_duplicate(
        "Broken streetlight",
        "The lamp near the bus stop has not been working for two weeks",
        existing,
    )
    assert is_dup2 is False, f"Expected no duplicate, got score={score2}"

    # Empty list edge case
    is_dup3, orig_id3, score3 = find_duplicate("Any title", "Any description", [])
    assert is_dup3 is False

    print("duplicate.py: All smoke tests passed OK")
