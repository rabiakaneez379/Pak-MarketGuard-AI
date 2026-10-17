
from app.agent import run_analysis


def test_workflow_analyzes_reviews():
    result = run_analysis([
        "Excellent product!",
        "Excellent product!",
        "Delivery was late",
    ])

    assert "review_result" in result
    assert "image_result" in result
    assert "risk_result" in result

    assert len(
        result["review_result"]["exact_duplicate_groups"]
    ) == 1

    assert result["risk_result"]["risk_score"] > 0


def test_workflow_without_image():
    result = run_analysis([
        "The package arrived today and works well"
    ])

    assert result["image_result"] is None
    assert result["risk_result"]["is_fraud_probability"] is False
    assert any(
        "No image analysis" in item
        for item in result["risk_result"]["limitations"]
    )
