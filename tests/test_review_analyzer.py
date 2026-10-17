
from app.review_analyzer import (
    analyze_reviews,
    normalize_review,
    similarity,
)


def test_normalization():
    assert normalize_review("VERY GOOD!!! Product") == "very good product"


def test_duplicate_reviews_are_detected():
    result = analyze_reviews([
        "Excellent product!",
        "Excellent product!",
        "Received my order today",
    ])

    assert len(result["exact_duplicate_groups"]) == 1
    assert result["exact_duplicate_groups"][0]["count"] == 2


def test_empty_reviews():
    result = analyze_reviews([])

    assert result["review_count"] == 0
    assert result["signals"] == []


def test_generic_roman_urdu_phrase():
    result = analyze_reviews([
        "Quality bohat achi hai",
        "Delivery was late",
    ])

    assert result["generic_review_count"] == 1


def test_roman_urdu_spelling_variations():
    result = analyze_reviews([
        "Bohut acha product",
        "Bht achi product",
        "The delivery arrived yesterday",
    ])

    assert result["generic_review_count"] == 2


def test_roman_urdu_matching_is_case_insensitive():
    result = analyze_reviews([
        "BOHUT ACHA PRODUCT",
        "bht achi product",
    ])

    assert result["generic_review_count"] == 2


def test_bohat_spelling_variations_normalize_equally():
    variants = [
        "Bohat acha product",
        "Bohut acha product",
        "Bohot acha product",
        "Bht acha product",
    ]

    normalized = [normalize_review(text) for text in variants]

    assert len(set(normalized)) == 1


def test_roman_urdu_variations_form_duplicate_group():
    result = analyze_reviews([
        "Bohat acha product",
        "Bohut acha product",
        "Bht acha product",
    ])

    assert len(result["exact_duplicate_groups"]) == 1
    assert result["exact_duplicate_groups"][0]["count"] == 3
    assert result["near_duplicate_pairs"] == []


def test_negative_delivery_review_is_not_generic_praise():
    result = analyze_reviews([
        "Delivery bohat late hui",
    ])

    assert result["generic_review_count"] == 0


def test_short_reviews_are_not_suspicious_signals():
    result = analyze_reviews([
        "Good",
        "Very nice",
        "Received today",
    ])

    assert result["short_review_count"] == 3
    assert not any(
        "short" in signal.casefold()
        for signal in result["signals"]
    )


def test_similarity_of_identical_normalized_text():
    text_a = normalize_review("Bohat acha product")
    text_b = normalize_review("Bht acha product")

    assert similarity(text_a, text_b) == 1.0
