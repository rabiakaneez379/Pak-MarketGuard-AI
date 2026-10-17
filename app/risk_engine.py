
from typing import Any


def calculate_risk(
    review_result: dict[str, Any],
    image_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Calculate a transparent listing-risk score from 0 to 100.

    This is a heuristic screening score, not a probability of fraud.
    Short reviews alone do not increase the score.
    """

    score = 0
    evidence = []
    limitations = []

    review_count = review_result.get("review_count", 0)
    analyzed_count = review_result.get("analyzed_nonempty_count", 0)

    # 1. Repeated review wording
    duplicate_groups = review_result.get("exact_duplicate_groups", [])

    if duplicate_groups:
        points = 25
        score += points

        duplicate_count = sum(
            group.get("count", 0)
            for group in duplicate_groups
        )

        evidence.append({
            "signal": "Repeated review wording",
            "category": "Observed pattern",
            "points": points,
            "reason": (
                f"{len(duplicate_groups)} group(s) of repeated normalized "
                f"review text were found, involving {duplicate_count} "
                "review occurrence(s)."
            ),
            "interpretation": (
                "Genuine customers can independently write the same phrase. "
                "Repeated wording is not proof of fake reviews."
            ),
        })

    # 2. Similar but non-identical reviews
    near_pairs = review_result.get("near_duplicate_pairs", [])

    if near_pairs:
        points = min(25, 8 * len(near_pairs))
        score += points

        evidence.append({
            "signal": "Similar review wording",
            "category": "Observed pattern",
            "points": points,
            "reason": (
                f"{len(near_pairs)} highly similar review pair(s) "
                "were identified."
            ),
            "interpretation": (
                "Similar wording may have legitimate explanations. "
                "Additional context is needed."
            ),
        })

    # 3. Generic praise is a weak indicator
    generic_count = review_result.get("generic_review_count", 0)

    if analyzed_count > 0 and generic_count / analyzed_count >= 0.6:
        points = 5
        score += points

        evidence.append({
            "signal": "Frequent generic praise",
            "category": "Weak indicator",
            "points": points,
            "reason": (
                f"{generic_count} of {analyzed_count} analyzed reviews "
                "contain configured generic praise phrases."
            ),
            "interpretation": (
                "Genuine customers often write short positive reviews. "
                "This indicator receives only a small contribution."
            ),
        })

    # 4. Short reviews do not add risk points
    short_count = review_result.get("short_review_count", 0)

    if analyzed_count > 0 and short_count / analyzed_count >= 0.5:
        limitations.append(
            "Many reviews are short. Short reviews are not treated as "
            "evidence of fraud because genuine customers may write briefly."
        )

    # 5. Product image evidence
    if image_result is None:
        limitations.append(
            "No image analysis was supplied; image risk remains unknown."
        )

    elif image_result.get("status") != "success":
        limitations.append(
            "The image could not be analyzed; image risk is unknown."
        )

    else:
        comparison = image_result.get("reference_comparison")

        if comparison is None:
            limitations.append(
                "No reference image was supplied; image reuse "
                "could not be assessed."
            )

        elif comparison.get("status") == "error":
            limitations.append(
                "The reference image comparison could not be completed."
            )

        else:
            distance = comparison.get("perceptual_hash_distance")

            if isinstance(distance, int) and not isinstance(distance, bool):
                if distance <= 5:
                    points = 25
                    score += points

                    evidence.append({
                        "signal": "Very similar reference image",
                        "category": "Observed image similarity",
                        "points": points,
                        "reason": (
                            "The listing image has a very similar "
                            "perceptual hash to the supplied reference image."
                        ),
                        "interpretation": (
                            "The images may show the same product or be "
                            "duplicates. Similarity alone does not prove misuse."
                        ),
                    })

                elif distance <= 10:
                    points = 15
                    score += points

                    evidence.append({
                        "signal": "Some reference-image similarity",
                        "category": "Observed image similarity",
                        "points": points,
                        "reason": (
                            "The listing image has some perceptual-hash "
                            "similarity to the supplied reference image."
                        ),
                        "interpretation": (
                            "Inspect both images and their sources before "
                            "drawing conclusions."
                        ),
                    })

            else:
                limitations.append(
                    "The reference comparison returned no valid distance."
                )

    # 6. Keep the score within 0–100
    score = min(max(score, 0), 100)

    if score >= 50:
        level = "High"
        recommendation = (
            "Several configured indicators were detected. Verify the seller, "
            "product details, review context, and image sources independently."
        )

    elif score >= 25:
        level = "Moderate"
        recommendation = (
            "Some configured indicators were detected. Review the evidence "
            "and verify the seller and product details."
        )

    else:
        level = "Low"
        recommendation = (
            "Few configured indicators were detected. A low score does not "
            "guarantee that the listing or seller is trustworthy."
        )

    # 7. Add relevant limitations
    if review_count == 0:
        limitations.append("No reviews were provided.")

    elif analyzed_count == 0:
        limitations.append(
            "No non-empty reviews were available for analysis."
        )

    return {
        "risk_score": score,
        "risk_level": level,
        "recommendation": recommendation,
        "evidence": evidence,
        "limitations": limitations,
        "assessment_type": "Heuristic, evidence-based screening",
        "is_fraud_probability": False,
        "score_explanation": (
            "The score adds configured points for observed patterns. "
            "It is not a probability, confidence percentage, or proof of fraud."
        ),
    }
