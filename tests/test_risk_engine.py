
from app.risk_engine import calculate_risk


def test_empty_evidence_does_not_claim_safety():
    result = calculate_risk({
        "review_count": 0,
        "analyzed_nonempty_count": 0,
        "exact_duplicate_groups": [],
        "near_duplicate_pairs": [],
        "generic_review_count": 0,
        "short_review_count": 0,
    })

    assert result["risk_score"] == 0
    assert result["risk_level"] == "Low"
    assert result["is_fraud_probability"] is False
    assert any(
        "No reviews" in item
        for item in result["limitations"]
    )


def test_duplicate_reviews_increase_risk():
    result = calculate_risk({
        "review_count": 3,
        "analyzed_nonempty_count": 3,
        "exact_duplicate_groups": [
            {"normalized_review": "good product", "count": 2}
        ],
        "near_duplicate_pairs": [],
        "generic_review_count": 0,
        "short_review_count": 0,
    })

    assert result["risk_score"] == 25
    assert result["risk_level"] == "Moderate"


def test_identical_reference_image_adds_evidence():
    result = calculate_risk(
        {
            "review_count": 1,
            "analyzed_nonempty_count": 1,
            "exact_duplicate_groups": [],
            "near_duplicate_pairs": [],
            "generic_review_count": 0,
            "short_review_count": 0,
        },
        {
            "status": "success",
            "reference_comparison": {
                "status": "success",
                "perceptual_hash_distance": 0,
            },
        },
    )

    assert result["risk_score"] == 25
    assert any(
        item["signal"] == "Very similar reference image"
        for item in result["evidence"]
    )



def test_risk_score_is_capped_at_100():
    result = calculate_risk(
        {
            "review_count": 10,
            "analyzed_nonempty_count": 10,
            "exact_duplicate_groups": [
                {"normalized_review": "same", "count": 10}
            ],
            "near_duplicate_pairs": [{"similarity": 0.9}] * 10,
            "generic_review_count": 10,
            "short_review_count": 10,
        },
        {
            "status": "success",
            "reference_comparison": {
                "status": "success",
                "perceptual_hash_distance": 0,
            },
        },
    )

    assert result["risk_score"] == 80
    assert result["risk_score"] <= 100
    assert result["risk_level"] == "High"



def test_short_reviews_alone_do_not_increase_risk():
    result = calculate_risk({
        "review_count": 3,
        "analyzed_nonempty_count": 3,
        "exact_duplicate_groups": [],
        "near_duplicate_pairs": [],
        "generic_review_count": 0,
        "short_review_count": 3,
    })

    assert result["risk_score"] == 0
    assert result["evidence"] == []
    assert any(
        "Many reviews are short" in item
        for item in result["limitations"]
    )


def test_generic_praise_has_a_small_contribution():
    result = calculate_risk({
        "review_count": 5,
        "analyzed_nonempty_count": 5,
        "exact_duplicate_groups": [],
        "near_duplicate_pairs": [],
        "generic_review_count": 3,
        "short_review_count": 0,
    })

    assert result["risk_score"] == 5
    assert result["risk_level"] == "Low"
    assert result["evidence"][0]["points"] == 5
