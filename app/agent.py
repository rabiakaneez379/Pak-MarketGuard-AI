
from typing import Any
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

from app.review_analyzer import analyze_reviews
from app.image_inspector import inspect_image
from app.risk_engine import calculate_risk


class AnalysisState(TypedDict, total=False):
    reviews: list[str]
    image_bytes: bytes | None
    reference_image_bytes: bytes | None

    review_result: dict[str, Any]
    image_result: dict[str, Any] | None
    risk_result: dict[str, Any]


def analyze_reviews_node(state: AnalysisState) -> dict:
    """Analyze review text and return review signals."""

    reviews = state.get("reviews", [])

    return {
        "review_result": analyze_reviews(reviews)
    }


def inspect_image_node(state: AnalysisState) -> dict:
    """Inspect the listing image when one is provided."""

    image_bytes = state.get("image_bytes")
    reference_bytes = state.get("reference_image_bytes")

    if image_bytes is None:
        return {"image_result": None}

    result = inspect_image(
        image_bytes=image_bytes,
        reference_bytes=reference_bytes,
    )

    return {"image_result": result}


def calculate_risk_node(state: AnalysisState) -> dict:
    """Combine review and image evidence into a risk assessment."""

    review_result = state.get("review_result", {})
    image_result = state.get("image_result")

    risk_result = calculate_risk(
        review_result=review_result,
        image_result=image_result,
    )

    return {"risk_result": risk_result}


def build_analysis_graph():
    """Build the complete Pak-MarketGuard analysis workflow."""

    workflow = StateGraph(AnalysisState)

    workflow.add_node("analyze_reviews", analyze_reviews_node)
    workflow.add_node("inspect_image", inspect_image_node)
    workflow.add_node("calculate_risk", calculate_risk_node)

    workflow.add_edge(START, "analyze_reviews")
    workflow.add_edge("analyze_reviews", "inspect_image")
    workflow.add_edge("inspect_image", "calculate_risk")
    workflow.add_edge("calculate_risk", END)

    return workflow.compile()


analysis_graph = build_analysis_graph()


def run_analysis(
    reviews: list[str],
    image_bytes: bytes | None = None,
    reference_image_bytes: bytes | None = None,
) -> dict[str, Any]:
    """Run the complete analysis and return its results."""

    result = analysis_graph.invoke({
        "reviews": reviews,
        "image_bytes": image_bytes,
        "reference_image_bytes": reference_image_bytes,
    })

    return {
        "review_result": result["review_result"],
        "image_result": result.get("image_result"),
        "risk_result": result["risk_result"],
    }
