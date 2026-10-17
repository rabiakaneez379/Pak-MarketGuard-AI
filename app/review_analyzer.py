
import re
from difflib import SequenceMatcher
from collections import Counter
from typing import Any


# English and Roman Urdu generic praise phrases.
GENERIC_PHRASES = (
    # English
    "very good product",
    "highly recommended",
    "best quality",
    "excellent product",
    "must buy",
    "100 percent original",
    "good product",
    "great product",
    "amazing product",
    "value for money",
    "excellent quality",
    "awesome product",
    "great quality",
    "perfect product",

    # Roman Urdu
    "bohat acha",
    "bohat achi",
    "bohat achay",
    "zabardast product",
    "quality bohat achi",
    "paisa wasool",
    "lazawab product",
    "kamal ki quality",
    "bohat zabardast",
    "bohat umda",
    "intiha ka acha",
    "quality kamaal ki hai",
    "paisay wasool",
    "pese wasool",
    "qeemat ke hisaab se acha",
)


def normalize_review(review: str) -> str:
    """Normalize text and common English/Roman Urdu variations."""
    text = review.casefold().strip()

    # Normalize URLs.
    text = re.sub(
        r"https?://\S+|www\.\S+",
        " URL ",
        text,
    )

    # Standardize common Roman Urdu spellings.
    spelling_variations = {
        r"\bbohut\b": "bohat",
        r"\bbohot\b": "bohat",
        r"\bbht\b": "bohat",
        r"\bbuhat\b": "bohat",
        r"\bpaisay\b": "paisa",
        r"\bpese\b": "paisa",
        r"\bpaise\b": "paisa",
        r"\blajawab\b": "lazawab",
        r"\bla jawab\b": "lazawab",
        r"\bkamal\b": "kamaal",
    }

    for pattern, replacement in spelling_variations.items():
        text = re.sub(pattern, replacement, text)

    # Remove punctuation and normalize whitespace.
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def similarity(text_a: str, text_b: str) -> float:
    """Return a text similarity score between 0 and 1."""
    if not text_a or not text_b:
        return 0.0

    return SequenceMatcher(None, text_a, text_b).ratio()


def find_generic_phrases(review: str) -> list[str]:
    """
    Find configured praise phrases.

    Equivalent spelling variations are reported using one standard phrase.
    """
    normalized = normalize_review(review)
    matched_phrases = []
    seen_normalized_phrases = set()

    for phrase in GENERIC_PHRASES:
        normalized_phrase = normalize_review(phrase)

        # Skip spelling variations already represented by a standard phrase.
        if normalized_phrase in seen_normalized_phrases:
            continue

        pattern = (
            r"(?<!\w)"
            + re.escape(normalized_phrase)
            + r"(?!\w)"
        )

        if re.search(pattern, normalized):
            matched_phrases.append(phrase)
            seen_normalized_phrases.add(normalized_phrase)

    return matched_phrases


def analyze_reviews(reviews: list[str]) -> dict[str, Any]:
    """
    Detect duplicate wording, near-duplicates, and generic praise.
    Short reviews alone are not treated as suspicious.
    """

    if not reviews:
        return {
            "review_count": 0,
            "analyzed_nonempty_count": 0,
            "exact_duplicate_groups": [],
            "near_duplicate_pairs": [],
            "generic_review_count": 0,
            "generic_phrase_matches": [],
            "generic_review_details": [],
            "short_review_count": 0,
            "signals": [],
            "limitations": [
                "No reviews were supplied, so patterns could not be assessed."
            ],
        }

    # Normalize reviews for comparison.
    cleaned = [normalize_review(review) for review in reviews]
    nonempty = [review for review in cleaned if review]

    # Find exact duplicates after normalization.
    counts = Counter(nonempty)

    duplicate_groups = [
        {
            "normalized_review": text,
            "count": count,
        }
        for text, count in counts.items()
        if count > 1
    ]

    # Find highly similar but non-identical reviews.
    near_duplicate_pairs = []

    for i in range(len(nonempty)):
        for j in range(i + 1, len(nonempty)):
            if nonempty[i] == nonempty[j]:
                continue

            score = similarity(nonempty[i], nonempty[j])

            if score >= 0.85:
                near_duplicate_pairs.append({
                    "review_index_a": i,
                    "review_index_b": j,
                    "similarity": round(score, 3),
                })

    # Record detected phrases for each original review.
    generic_review_details = []
    generic_phrase_counts = Counter()

    for index, original_review in enumerate(reviews):
        if not original_review.strip():
            continue

        matched = find_generic_phrases(original_review)

        if matched:
            generic_review_details.append({
                "review_index": index + 1,
                "matched_phrases": matched,
            })
            generic_phrase_counts.update(matched)

    generic_count = len(generic_review_details)

    # Summarize the number of reviews containing each standard phrase.
    generic_phrase_matches = [
        {
            "phrase": phrase,
            "count": count,
        }
        for phrase, count in generic_phrase_counts.items()
    ]

    # Count short reviews for context only.
    short_count = sum(
        len(review.split()) <= 3
        for review in nonempty
    )

    # Create review-pattern signals.
    signals = []

    if duplicate_groups:
        signals.append("Exact duplicate review text was found.")

    if near_duplicate_pairs:
        signals.append("Some reviews have highly similar wording.")

    if nonempty and generic_count / len(nonempty) >= 0.4:
        signals.append("Many reviews contain generic praise phrases.")

    limitations = [
        "Similarity does not prove that a review is fake.",
        "Review timestamps and verified-purchase information are unavailable.",
        "Roman Urdu spelling and phrasing vary, so some patterns may be missed.",
        "This is a rule-based baseline, not a trained fraud classifier.",
        "Generic praise is not proof of fake reviews.",
    ]

    if nonempty and short_count / len(nonempty) >= 0.5:
        limitations.append(
            "Many reviews are short. This is contextual information, "
            "not evidence of fraud by itself."
        )

    return {
        "review_count": len(reviews),
        "analyzed_nonempty_count": len(nonempty),
        "exact_duplicate_groups": duplicate_groups,
        "near_duplicate_pairs": near_duplicate_pairs,
        "generic_review_count": generic_count,
        "generic_phrase_matches": generic_phrase_matches,
        "generic_review_details": generic_review_details,
        "short_review_count": short_count,
        "signals": signals,
        "limitations": limitations,
    }
