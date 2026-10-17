
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)


# ---------------------------------------------------------
# SAFE DATA HELPERS
# ---------------------------------------------------------

def safe_dict(value):
    """Return a dictionary or an empty dictionary."""
    return value if isinstance(value, dict) else {}


def safe_list(value):
    """Return a list without raising an exception."""
    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    return []


def safe_int(value, default=0):
    """Convert a value to an integer safely."""
    try:
        if value is None or isinstance(value, bool):
            return default
        return int(float(value))
    except (TypeError, ValueError, OverflowError):
        return default


def safe_text(value, fallback="Not available"):
    """Convert a value to readable text."""
    if value is None:
        return fallback

    if isinstance(value, str):
        value = value.strip()

        if value.upper() in {
            "", "N/A", "NA", "NONE", "NULL", "NOT AVAILABLE"
        }:
            return fallback

        return value

    return str(value)


def get_first_value(data, keys, default=None):
    """Return the first available value from a dictionary."""
    data = safe_dict(data)

    for key in keys:
        if key in data and data[key] is not None:
            return data[key]

    return default


def count_items(value):
    """Count a list or use a numeric value as a count."""
    if isinstance(value, (list, tuple, set)):
        return len(value)

    return safe_int(value, 0)


def metric_value(metrics, review_result, keys, default=0):
    """Read a metric from metrics or fall back to review results."""
    value = get_first_value(metrics, keys)

    if value is None:
        value = get_first_value(review_result, keys)

    if value is None:
        return default

    return count_items(value)


def format_detail(value):
    """Convert nested results into readable report text."""
    if value is None:
        return "Not available"

    if isinstance(value, dict):
        if not value:
            return "No details provided."

        parts = []

        for key, item in value.items():
            label = str(key).replace("_", " ").title()
            parts.append(f"{label}: {format_detail(item)}")

        return "; ".join(parts)

    if isinstance(value, (list, tuple)):
        if not value:
            return "No items found."

        parts = []

        for index, item in enumerate(value, start=1):
            parts.append(f"{index}. {format_detail(item)}")

        return "\n".join(parts)

    return str(value)


def make_paragraph(text, style):
    """Escape ordinary text before adding it to a ReportLab paragraph."""
    text = safe_text(text)
    text = escape(text)
    text = text.replace("\n", "<br/>")

    return Paragraph(text, style)


# ---------------------------------------------------------
# PDF REPORT GENERATOR
# ---------------------------------------------------------

def generate_pdf_report(
    reviews,
    review_result,
    image_result,
    risk_result,
    metrics=None,
    product_name="",
    display_score=None,
    display_risk_level=None,
    recommendation=None,
):
    """
    Generate a PDF screening report.

    The function accepts the same arguments used by app/main.py
    and returns PDF bytes.
    """

    # Normalize incoming data.
    reviews = safe_list(reviews)
    review_result = safe_dict(review_result)
    image_result = safe_dict(image_result)
    risk_result = safe_dict(risk_result)
    metrics = safe_dict(metrics)

    # Fill missing metric names without assuming any key exists.
    review_count = metric_value(
        metrics,
        review_result,
        ["review_count", "total_reviews", "reviews_analyzed"],
        len(reviews),
    )

    exact_group_count = metric_value(
        metrics,
        review_result,
        [
            "exact_group_count",
            "exact_duplicate_groups",
            "duplicate_groups",
            "duplicate_group_count",
        ],
        0,
    )

    similar_pair_count = metric_value(
        metrics,
        review_result,
        [
            "similar_pair_count",
            "near_duplicate_pairs",
            "similar_pairs",
            "similar_review_pairs",
            "similar_pair_count",
        ],
        0,
    )

    generic_review_count = metric_value(
        metrics,
        review_result,
        [
            "generic_review_count",
            "generic_reviews",
            "generic_praise_count",
        ],
        0,
    )

    # Use the supplied display values first, then the risk results.
    if display_score is None:
        display_score = get_first_value(
            risk_result,
            ["risk_score", "score"],
            "Not available",
        )

    if display_risk_level is None:
        display_risk_level = get_first_value(
            risk_result,
            ["risk_level"],
            "Not available",
        )

    if recommendation is None:
        recommendation = get_first_value(
            risk_result,
            ["recommendation"],
            "Review the available evidence before purchasing.",
        )

    product_name = safe_text(product_name, "Unnamed product")
    display_score = safe_text(display_score)
    display_risk_level = safe_text(display_risk_level)
    recommendation = safe_text(
        recommendation,
        "Review the available evidence before purchasing.",
    )

    # -----------------------------------------------------
    # PDF DOCUMENT AND STYLES
    # -----------------------------------------------------

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Pak-MarketGuard AI Screening Report",
        author="Pak-MarketGuard AI",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"),
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#52657A"),
        spaceAfter=18,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#17365D"),
        spaceBefore=14,
        spaceAfter=7,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#263445"),
        spaceAfter=5,
        wordWrap="LTR",
    )

    small_style = ParagraphStyle(
        "ReportSmall",
        parent=body_style,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#52657A"),
    )

    cell_style = ParagraphStyle(
        "ReportCell",
        parent=body_style,
        fontSize=8,
        leading=11,
        spaceAfter=0,
    )

    cell_header_style = ParagraphStyle(
        "ReportCellHeader",
        parent=cell_style,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    story = []

    # -----------------------------------------------------
    # REPORT HEADER
    # -----------------------------------------------------

    story.append(Paragraph("Pak-MarketGuard AI", title_style))

    story.append(
        Paragraph(
            "AI-Assisted E-Commerce Risk Screening Report",
            subtitle_style,
        )
    )

    story.append(
        Paragraph("Product Information", heading_style)
    )

    product_rows = [
        [
            make_paragraph("Product name", cell_header_style),
            make_paragraph(product_name, cell_style),
        ],
        [
            make_paragraph("Reviews supplied", cell_header_style),
            make_paragraph(str(review_count), cell_style),
        ],
        [
            make_paragraph("Screening score", cell_header_style),
            make_paragraph(
                f"{display_score} / 100",
                cell_style,
            ),
        ],
        [
            make_paragraph("Risk level", cell_header_style),
            make_paragraph(display_risk_level, cell_style),
        ],
    ]

    product_table = Table(
        product_rows,
        colWidths=[1.65 * inch, 4.85 * inch],
        repeatRows=0,
    )

    product_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#17365D"),
                ),
                (
                    "BACKGROUND",
                    (1, 0),
                    (1, -1),
                    colors.HexColor("#F2F6FC"),
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D6DFEA")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(product_table)
    story.append(Spacer(1, 8))

    # -----------------------------------------------------
    # SCREENING SUMMARY
    # -----------------------------------------------------

    story.append(
        Paragraph("Review Screening Summary", heading_style)
    )

    metric_rows = [
        [
            make_paragraph("Metric", cell_header_style),
            make_paragraph("Count", cell_header_style),
        ],
        [
            make_paragraph("Reviews supplied", cell_style),
            make_paragraph(str(review_count), cell_style),
        ],
        [
            make_paragraph("Exact duplicate groups", cell_style),
            make_paragraph(str(exact_group_count), cell_style),
        ],
        [
            make_paragraph("Similar review pairs", cell_style),
            make_paragraph(str(similar_pair_count), cell_style),
        ],
        [
            make_paragraph("Generic praise reviews", cell_style),
            make_paragraph(str(generic_review_count), cell_style),
        ],
    ]

    metrics_table = Table(
        metric_rows,
        colWidths=[4.9 * inch, 1.6 * inch],
        repeatRows=1,
    )

    metrics_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#17365D"),
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F2F6FC"),
                    ],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D6DFEA")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(metrics_table)

    # -----------------------------------------------------
    # RECOMMENDATION
    # -----------------------------------------------------

    story.append(
        Paragraph("Recommendation", heading_style)
    )

    story.append(
        make_paragraph(recommendation, body_style)
    )

    # -----------------------------------------------------
    # REVIEW ANALYSIS DETAILS
    # -----------------------------------------------------

    story.append(
        Paragraph("Review Analysis Details", heading_style)
    )

    if review_result:
        for key, value in review_result.items():
            label = str(key).replace("_", " ").title()
            detail = format_detail(value)

            story.append(
                KeepTogether(
                    [
                        Paragraph(
                            f"<b>{escape(label)}</b>",
                            body_style,
                        ),
                        make_paragraph(detail, small_style),
                        Spacer(1, 3),
                    ]
                )
            )
    else:
        story.append(
            Paragraph(
                "No additional review-analysis details were provided.",
                body_style,
            )
        )

    # Include the supplied reviews.
    story.append(
        Paragraph("Submitted Customer Reviews", heading_style)
    )

    if reviews:
        for index, review in enumerate(reviews, start=1):
            review_text = safe_text(review, "Empty review")
            story.append(
                make_paragraph(
                    f"{index}. {review_text}",
                    small_style,
                )
            )
    else:
        story.append(
            Paragraph(
                "No customer reviews were supplied.",
                body_style,
            )
        )

    # -----------------------------------------------------
    # IMAGE ANALYSIS
    # -----------------------------------------------------

    story.append(
        Paragraph("Product Image Analysis", heading_style)
    )

    if image_result:
        story.append(
            make_paragraph(
                format_detail(image_result),
                body_style,
            )
        )
    else:
        story.append(
            Paragraph(
                "No image-analysis details were provided. "
                "Image comparison is optional.",
                body_style,
            )
        )

    # -----------------------------------------------------
    # RISK ASSESSMENT EVIDENCE
    # -----------------------------------------------------

    story.append(
        Paragraph("Risk Assessment Evidence", heading_style)
    )

    if risk_result:
        story.append(
            make_paragraph(
                format_detail(risk_result),
                body_style,
            )
        )
    else:
        story.append(
            Paragraph(
                "No additional risk-assessment evidence was provided.",
                body_style,
            )
        )

    # -----------------------------------------------------
    # LIMITATIONS AND DISCLAIMER
    # -----------------------------------------------------

    story.append(
        Paragraph("Important Limitations", heading_style)
    )

    disclaimer = (
        "The screening score is a heuristic indicator based on the "
        "project's implemented rules and available inputs. It is not "
        "a probability of fraud and does not prove that a product, "
        "seller, or review is fraudulent. Automated analysis can produce "
        "false positives and false negatives. Duplicate wording or "
        "generic praise alone does not establish deceptive activity. "
        "Verify product details, seller information, and independent "
        "evidence before making a purchasing decision."
    )

    story.append(
        make_paragraph(disclaimer, small_style)
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "Generated by Pak-MarketGuard AI",
            subtitle_style,
        )
    )

    # -----------------------------------------------------
    # BUILD THE PDF
    # -----------------------------------------------------

    document.build(story)

    buffer.seek(0)
    return buffer.getvalue()
