
import html
from io import BytesIO

import streamlit as st
from gtts import gTTS

from app.agent import run_analysis
from app.report_generator import generate_pdf_report


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Pak-MarketGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

def load_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(
                135deg, #07111f 0%, #0b1728 55%, #101f34 100%
            );
            color: #eaf2ff;
        }

        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stToolbar"] { right: 1rem; }

        .block-container {
            max-width: 1180px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3, h4, p, label { color: #eaf2ff; }

        .section-number {
            color: #60a5fa;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 2px;
            margin-bottom: 8px;
        }

        .section-heading {
            color: #f1f7ff;
            font-size: 22px;
            font-weight: 750;
            margin-bottom: 8px;
        }

        .section-description {
            color: #b1c4dc;
            font-size: 14px;
            line-height: 1.7;
        }

        .metric-card {
            background: #11243a;
            border: 1px solid #2b4663;
            border-radius: 14px;
            padding: 18px;
            min-height: 105px;
        }

        .metric-label {
            color: #a9bfd8;
            font-size: 12px;
            margin-bottom: 8px;
        }

        .metric-value {
            color: #f1f7ff;
            font-size: 25px;
            font-weight: 800;
        }

        .result-panel {
            padding: 20px;
            border: 1px solid #2b4663;
            border-radius: 16px;
            background: #0e2034;
            margin: 12px 0;
        }

        .risk-score {
            color: #60a5fa;
            font-size: 38px;
            font-weight: 850;
        }

        .empty-state {
            background: #102239;
            border: 1px solid #29415d;
            border-radius: 9px;
            padding: 12px 14px;
            color: #b9cbe0;
            font-size: 13px;
            line-height: 1.6;
            margin: 5px 0;
        }

        div.stButton > button {
            background: linear-gradient(90deg, #2563eb, #0d9488);
            color: white;
            border: none;
            border-radius: 10px;
            min-height: 46px;
            font-weight: 700;
            transition: 0.2s ease;
        }

        div.stButton > button:hover {
            border: 1px solid #93c5fd;
            color: white;
            filter: brightness(1.1);
        }

        .stTextArea textarea,
        .stTextInput input {
            background-color: #0d1b2c !important;
            color: #edf5ff !important;
            border: 1px solid #314a66 !important;
            border-radius: 10px !important;
        }

        [data-testid="stFileUploader"] {
            background: #0d1b2c;
            border: 1px dashed #3b5878;
            border-radius: 12px;
            padding: 12px;
        }

        [data-testid="stFileUploader"] label,
        [data-testid="stFileUploader"] small {
            color: #c5d8ef !important;
        }

        [data-testid="stExpander"] {
            background: rgba(16, 31, 52, 0.7);
            border: 1px solid #263c56;
            border-radius: 12px;
        }

        .footer-text {
            color: #8299b5;
            font-size: 12px;
            text-align: center;
            line-height: 1.8;
            margin-top: 30px;
        }

        div[data-testid="stAlert"] { border-radius: 10px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# HERO SECTION
# ---------------------------------------------------------

def show_hero():
    st.html("""
        <div style="
            text-align: center;
            padding: 36px 10px 40px 10px;
        ">
            <div style="
                display: inline-block;
                padding: 8px 15px;
                border: 1px solid #315b89;
                border-radius: 30px;
                color: #93c5fd;
                background: #122a45;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 1.5px;
                margin-bottom: 20px;
            ">
                AI-POWERED PRODUCT SCREENING
            </div>

            <h1 style="
                font-size: clamp(32px, 5vw, 48px);
                font-weight: 800;
                color: #f1f7ff;
                margin: 0 0 14px 0;
                line-height: 1.2;
            ">
                Pak-MarketGuard
                <span style="color: #60a5fa;">AI</span>
            </h1>

            <p style="
                color: #d2deed;
                font-size: 20px;
                font-weight: 500;
                margin: 0 0 12px 0;
            ">
                Smarter insights for safer online shopping.
            </p>

            <p style="
                color: #a9bfd8;
                font-size: 14px;
                max-width: 680px;
                margin: 0 auto;
                line-height: 1.8;
            ">
                Analyze review patterns, compare product images, and
                identify potential warning signs before purchasing.
            </p>
        </div>
    """)


# ---------------------------------------------------------
# REUSABLE HELPERS
# ---------------------------------------------------------

def show_section_heading(number, heading, description):
    st.markdown(
        f"""
        <div style="margin: 22px 0 14px 0;">
            <div class="section-number">{html.escape(str(number))}</div>
            <div class="section-heading">{html.escape(str(heading))}</div>
            <div class="section-description">{html.escape(str(description))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(str(label))}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_empty_state(message):
    """Show a readable message when a result list is empty."""
    st.markdown(
        f'<div class="empty-state">{html.escape(message)}</div>',
        unsafe_allow_html=True,
    )


def display_value(value, empty_message="No matching indicators were detected."):
    """
    Display nested analysis data safely.
    Empty lists receive meaningful messages instead of generic placeholders.
    """
    if isinstance(value, dict):
        if not value:
            show_empty_state(empty_message)
            return

        for key, item in value.items():
            label = str(key).replace("_", " ").strip().title()
            st.markdown(f"**{html.escape(label)}**")

            if isinstance(item, (list, tuple)) and not item:
                show_empty_state(empty_message)
            elif isinstance(item, dict) and not item:
                show_empty_state("No additional details were provided.")
            else:
                display_value(item, empty_message)

    elif isinstance(value, (list, tuple)):
        if not value:
            show_empty_state(empty_message)
        else:
            for index, item in enumerate(value, start=1):
                if isinstance(item, (dict, list, tuple)):
                    with st.expander(f"Item {index}"):
                        display_value(item, empty_message)
                else:
                    st.write(f"{index}. {item}")

    elif value is None:
        show_empty_state("No additional information was provided.")

    else:
        st.write(value)


def get_metric(metrics, possible_keys, default=0):
    if not isinstance(metrics, dict):
        return default

    for key in possible_keys:
        if key in metrics and metrics[key] is not None:
            return metrics[key]

    return default


def make_audio(text_to_speak, language):
    audio_buffer = BytesIO()
    speech = gTTS(text=text_to_speak, lang=language, slow=False)
    speech.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.getvalue()


def is_missing(value):
    if value is None:
        return True

    if isinstance(value, str):
        return value.strip().upper() in {
            "", "N/A", "NA", "NONE", "NULL", "NOT AVAILABLE"
        }

    return False


def safe_text(value, fallback):
    if is_missing(value):
        return fallback
    return str(value).strip()


def safe_dict(value):
    return value if isinstance(value, dict) else {}


def safe_list(value):
    if isinstance(value, (list, tuple)):
        return list(value)
    return []


# ---------------------------------------------------------
# NORMALIZE ANALYSIS FOR DISPLAY AND PDF
# ---------------------------------------------------------

def normalize_analysis(raw_analysis, input_reviews, product_name):
    """
    Preserve analysis results while making optional fields safe.
    """
    if not isinstance(raw_analysis, dict):
        raise ValueError(
            "The analysis engine did not return a dictionary."
        )

    analysis = dict(raw_analysis)

    analysis["reviews"] = safe_list(
        analysis.get("reviews", input_reviews)
    )

    analysis["product_name"] = safe_text(
        analysis.get("product_name"),
        product_name,
    )

    if "review_result" not in analysis:
        analysis["review_result"] = analysis.get(
            "review_analysis",
            analysis.get("reviews_analysis", {}),
        )

    if "image_result" not in analysis:
        analysis["image_result"] = analysis.get("image_analysis", {})

    if "risk_result" not in analysis:
        analysis["risk_result"] = analysis.get("risk_assessment", {})

    analysis["review_result"] = safe_dict(analysis.get("review_result"))
    analysis["image_result"] = safe_dict(analysis.get("image_result"))
    analysis["risk_result"] = safe_dict(analysis.get("risk_result"))

    if not isinstance(analysis.get("metrics"), dict):
        analysis["metrics"] = {}

    metrics = dict(analysis["metrics"])
    review_result = analysis["review_result"]

    metric_aliases = {
        "review_count": [
            "review_count", "total_reviews", "reviews_analyzed"
        ],
        "exact_duplicate_groups": [
            "exact_duplicate_groups", "duplicate_groups",
            "duplicate_group_count",
        ],
        "near_duplicate_pairs": [
            "near_duplicate_pairs", "similar_pairs",
            "similar_review_pairs", "similar_pair_count",
        ],
        "generic_review_count": [
            "generic_review_count", "generic_reviews",
            "generic_praise_count",
        ],
    }

    for destination, aliases in metric_aliases.items():
        if destination not in metrics:
            for alias in aliases:
                if alias in review_result:
                    metrics[destination] = review_result[alias]
                    break

    metrics.setdefault("review_count", len(analysis["reviews"]))
    analysis["metrics"] = metrics

    risk_result = analysis["risk_result"]

    if is_missing(analysis.get("score")):
        analysis["score"] = risk_result.get(
            "risk_score",
            risk_result.get("score", "N/A"),
        )

    if is_missing(analysis.get("risk_level")):
        analysis["risk_level"] = risk_result.get(
            "risk_level",
            "Not available",
        )

    if is_missing(analysis.get("recommendation")):
        analysis["recommendation"] = risk_result.get(
            "recommendation",
            "Review the available evidence before making a purchasing decision.",
        )

    return analysis


# ---------------------------------------------------------
# ANALYSIS RESULTS
# ---------------------------------------------------------

def show_analysis_results(analysis):
    st.markdown("---")
    st.markdown("## Screening results")

    st.caption(
        "These results are screening indicators. They are not proof "
        "that a product, seller, or review is fraudulent."
    )

    score = analysis.get("score", "N/A")
    risk_level = analysis.get("risk_level", "Not available")
    recommendation = analysis.get(
        "recommendation",
        "Review the available evidence before making a purchasing decision.",
    )
    metrics = safe_dict(analysis.get("metrics"))

    left, right = st.columns([1, 2])

    with left:
        displayed_score = safe_text(score, "N/A")

        st.markdown(
            f"""
            <div class="result-panel">
                <div class="metric-label">Overall screening score</div>
                <div class="risk-score">
                    {html.escape(displayed_score)}/100
                </div>
                <div style="
                    color: #c5d8ef;
                    font-size: 16px;
                    font-weight: 700;
                    margin-top: 8px;
                ">
                    {html.escape(safe_text(risk_level, "Not available"))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown("### Recommendation")
        st.write(safe_text(
            recommendation,
            "Review the available evidence before making a purchasing decision.",
        ))

        try:
            numeric_score = float(score)
            if 0 <= numeric_score <= 100:
                st.progress(numeric_score / 100)
        except (TypeError, ValueError):
            pass

        st.caption(
            "A higher score indicates more warning signs according to "
            "the project's screening rules; it is not a probability of fraud."
        )

    # Review metrics
    st.markdown("### Review overview")

    total_reviews = get_metric(
        metrics,
        ["total_reviews", "review_count", "reviews_analyzed"],
        len(safe_list(analysis.get("reviews"))),
    )

    duplicate_groups = get_metric(
        metrics,
        ["duplicate_groups", "exact_duplicate_groups", "duplicate_group_count"],
        0,
    )

    similar_pairs = get_metric(
        metrics,
        ["similar_pairs", "near_duplicate_pairs",
         "similar_review_pairs", "similar_pair_count"],
        0,
    )

    generic_reviews = get_metric(
        metrics,
        ["generic_reviews", "generic_praise_count", "generic_review_count"],
        0,
    )

    metric_columns = st.columns(4)

    with metric_columns[0]:
        show_metric_card("Reviews analyzed", total_reviews)

    with metric_columns[1]:
        show_metric_card("Duplicate groups", duplicate_groups)

    with metric_columns[2]:
        show_metric_card("Similar pairs", similar_pairs)

    with metric_columns[3]:
        show_metric_card("Generic praise", generic_reviews)

    # Review details: each empty list has a specific explanation.
    with st.expander("Review analysis details", expanded=True):
        review_result = safe_dict(analysis.get("review_result"))

        if not review_result:
            st.info("No separate review-analysis details were returned.")
        else:
            review_empty_messages = {
                "duplicate_groups": "No exact duplicate review groups were detected.",
                "exact_duplicate_groups": "No exact duplicate review groups were detected.",
                "similar_pairs": "No near-duplicate review pairs were detected.",
                "near_duplicate_pairs": "No near-duplicate review pairs were detected.",
                "similar_review_pairs": "No near-duplicate review pairs were detected.",
                "generic_phrase_matches": "No configured generic-praise phrases were matched.",
                "generic_phrases": "No configured generic-praise phrases were matched.",
                "generic_review_details": "No reviews matched the configured generic-review rules.",
                "signals": "No configured review warning indicators were detected.",
                "evidence": "No review risk evidence was detected by the configured rules.",
                "limitations": "No additional limitations were provided.",
            }

            for key, value in review_result.items():
                label = str(key).replace("_", " ").strip().title()
                st.markdown(f"**{html.escape(label)}**")

                message = review_empty_messages.get(
                    str(key).lower(),
                    "No results were found for this category.",
                )

                if isinstance(value, (list, tuple)) and not value:
                    show_empty_state(message)
                elif isinstance(value, dict) and not value:
                    show_empty_state("No additional details were provided.")
                else:
                    display_value(value, message)

    # Image details
    with st.expander("Product image comparison details"):
        image_result = safe_dict(analysis.get("image_result"))

        if image_result:
            display_value(
                image_result,
                "No additional image-comparison details were provided.",
            )
        else:
            st.info(
                "No separate image-analysis details were returned. "
                "Image comparison is optional."
            )

    # Risk evidence
    with st.expander("Risk assessment evidence"):
        risk_result = safe_dict(analysis.get("risk_result"))

        if not risk_result:
            st.info("No separate risk-assessment details were returned.")
        else:
            risk_empty_messages = {
                "evidence": "No risk indicators were detected in this screening.",
                "signals": "No configured risk signals were detected.",
                "risk_evidence": "No risk indicators were detected in this screening.",
                "limitations": "No additional limitations were provided.",
            }

            for key, value in risk_result.items():
                label = str(key).replace("_", " ").strip().title()
                st.markdown(f"**{html.escape(label)}**")

                message = risk_empty_messages.get(
                    str(key).lower(),
                    "No results were found for this category.",
                )

                if isinstance(value, (list, tuple)) and not value:
                    show_empty_state(message)
                elif isinstance(value, dict) and not value:
                    show_empty_state("No additional details were provided.")
                else:
                    display_value(value, message)

    # -----------------------------------------------------
    # ENGLISH AND URDU AUDIO
    # -----------------------------------------------------

    st.markdown("### Listen to the recommendation")
    st.caption("Generate an audio version in English or Urdu.")

    audio_language = st.selectbox(
        "Audio language",
        options=["English", "Urdu"],
        key="audio_language",
    )

    if st.button("Generate recommendation audio", key="generate_audio"):
        try:
            with st.spinner("Generating audio..."):

                if audio_language == "English":
                    speech_language = "en"

                    spoken_score = safe_text(score, "not available")
                    spoken_level = safe_text(risk_level, "not available")
                    spoken_recommendation = safe_text(
                        recommendation,
                        "Please review the available evidence before purchasing.",
                    )

                    speech_text = (
                        "Pak MarketGuard AI screening result. "
                        f"Risk level: {spoken_level}. "
                        f"Score: {spoken_score} out of 100. "
                        f"Recommendation: {spoken_recommendation}"
                    )

                else:
                    speech_language = "ur"
                    normalized_level = safe_text(risk_level, "").lower()

                    if normalized_level in {"low", "کم", "کم خطرہ"}:
                        urdu_level = "خطرے کی سطح کم ہے۔"
                        urdu_advice = (
                            "دستیاب معلومات میں خطرے کی نشانیاں کم ہیں، "
                            "تاہم خریداری سے پہلے تفصیلات کی تصدیق کریں۔"
                        )

                    elif normalized_level in {
                        "moderate", "medium", "درمیانہ", "درمیانہ خطرہ"
                    }:
                        urdu_level = "خطرے کی سطح درمیانی ہے۔"
                        urdu_advice = (
                            "خریداری سے پہلے صارفین کے تبصروں اور "
                            "مصنوعات کی تفصیلات کو احتیاط سے جانچیں۔"
                        )

                    elif normalized_level in {
                        "high", "زیادہ", "زیادہ خطرہ"
                    }:
                        urdu_level = "خطرے کی سطح زیادہ ہے۔"
                        urdu_advice = (
                            "خریداری سے پہلے تمام معلومات کی اچھی طرح "
                            "تصدیق کریں اور احتیاط سے فیصلہ کریں۔"
                        )

                    else:
                        urdu_level = "خطرے کی سطح دستیاب نہیں ہے۔"
                        urdu_advice = (
                            "خریداری سے پہلے دستیاب معلومات کی تصدیق کریں۔"
                        )

                    try:
                        numeric_score = float(score)

                        if (
                            not is_missing(score)
                            and 0 <= numeric_score <= 100
                        ):
                            score_number = str(int(numeric_score))
                            urdu_score = (
                                f"اسکور ایک سو میں سے {score_number} ہے۔"
                            )
                        else:
                            urdu_score = "اسکور دستیاب نہیں ہے۔"

                    except (TypeError, ValueError):
                        urdu_score = "اسکور دستیاب نہیں ہے۔"

                    speech_text = (
                        "پاک مارکیٹ گارڈ اے آئی کی رپورٹ۔ "
                        f"{urdu_level} {urdu_score} {urdu_advice}"
                    )

                audio_bytes = make_audio(speech_text, speech_language)

            st.audio(audio_bytes, format="audio/mp3")
            st.success("Audio generated successfully.")

        except Exception as error:
            st.error(
                "Audio could not be generated. Check your internet "
                "connection and gTTS installation."
            )
            st.caption(f"Technical detail: {error}")

    # -----------------------------------------------------
    # PDF REPORT
    # -----------------------------------------------------

    st.markdown("### Download screening report")

    try:
        pdf_data = generate_pdf_report(
            reviews=safe_list(analysis.get("reviews")),
            review_result=safe_dict(analysis.get("review_result")),
            image_result=safe_dict(analysis.get("image_result")),
            risk_result=safe_dict(analysis.get("risk_result")),
            metrics=safe_dict(analysis.get("metrics")),
            product_name=safe_text(
                analysis.get("product_name"),
                "Unnamed product",
            ),
            display_score=analysis.get("score"),
            display_risk_level=analysis.get("risk_level"),
            recommendation=analysis.get("recommendation"),
        )

        if hasattr(pdf_data, "getvalue"):
            pdf_bytes = pdf_data.getvalue()
        elif isinstance(pdf_data, bytes):
            pdf_bytes = pdf_data
        else:
            pdf_bytes = bytes(pdf_data)

        if not pdf_bytes:
            raise ValueError("The PDF generator returned an empty file.")

        st.download_button(
            label="Download PDF report",
            data=pdf_bytes,
            file_name="Pak-MarketGuard-AI-Report.pdf",
            mime="application/pdf",
            key="download_pdf_report",
        )

    except Exception as error:
        st.error("The PDF report could not be prepared.")
        st.caption(
            "The report generator encountered an error while preparing "
            "the report."
        )
        st.caption(f"Technical detail: {error}")


# ---------------------------------------------------------
# MAIN APPLICATION
# ---------------------------------------------------------

def main():
    load_custom_css()
    show_hero()

    show_section_heading(
        "01",
        "Product information",
        "Enter a product name and provide customer reviews for screening.",
    )

    product_name = st.text_input(
        "Product name",
        placeholder="e.g., Wireless Bluetooth Headphones",
        key="product_name",
    )

    reviews_text = st.text_area(
        "Customer reviews",
        placeholder=(
            "Paste customer reviews here. Put each review on a separate line.\n\n"
            "Example:\n"
            "Excellent product, works perfectly.\n"
            "Excellent product, works perfectly.\n"
            "Amazing quality, highly recommended."
        ),
        height=190,
        key="customer_reviews",
    )

    show_section_heading(
        "02",
        "Product image comparison",
        "Optionally compare a listing image with a reference image.",
    )

    image_column_1, image_column_2 = st.columns(2)

    with image_column_1:
        listing_image = st.file_uploader(
            "Product listing image",
            type=["png", "jpg", "jpeg", "webp"],
            help="Maximum file size: 5 MB.",
            key="listing_image",
        )

    with image_column_2:
        reference_image = st.file_uploader(
            "Reference product image",
            type=["png", "jpg", "jpeg", "webp"],
            help="Maximum file size: 5 MB.",
            key="reference_image",
        )

    max_file_size = 5 * 1024 * 1024

    if listing_image and listing_image.size > max_file_size:
        st.error("The product listing image exceeds the 5 MB limit.")
        listing_image = None

    if reference_image and reference_image.size > max_file_size:
        st.error("The reference image exceeds the 5 MB limit.")
        reference_image = None

    if listing_image and not reference_image:
        st.info(
            "Upload a reference image as well if you want to compare "
            "the listing image against it."
        )

    if reference_image and not listing_image:
        st.info(
            "Upload a product listing image as well to perform image comparison."
        )

    show_section_heading(
        "03",
        "Run AI-assisted screening",
        "Analyze review patterns and any uploaded product images.",
    )

    st.caption(
        "Review analysis can run without images. Image comparison is optional."
    )

    analyze_button = st.button(
        "Analyze product risk",
        use_container_width=True,
        type="primary",
        key="analyze_product_risk",
    )

    if analyze_button:
        reviews = [
            review.strip()
            for review in reviews_text.splitlines()
            if review.strip()
        ]

        if not reviews:
            st.warning(
                "Please enter at least one customer review before starting "
                "the screening."
            )
            return

        if not product_name.strip():
            st.warning(
                "Please enter a product name so it can be included in "
                "your screening report."
            )
            return

        image_bytes = (
            listing_image.getvalue()
            if listing_image is not None
            else None
        )

        reference_image_bytes = (
            reference_image.getvalue()
            if reference_image is not None
            else None
        )

        with st.spinner(
            "Analyzing review patterns and available product images..."
        ):
            try:
                raw_analysis = run_analysis(
                    reviews=reviews,
                    image_bytes=image_bytes,
                    reference_image_bytes=reference_image_bytes,
                )

                analysis = normalize_analysis(
                    raw_analysis=raw_analysis,
                    input_reviews=reviews,
                    product_name=product_name.strip(),
                )

                st.session_state[
                    "pak_marketguard_last_analysis"
                ] = analysis

            except Exception as error:
                st.error("The screening could not be completed.")
                st.caption(
                    "Check the terminal for the full error and confirm "
                    "that the project dependencies are installed."
                )
                st.exception(error)
                return

    saved_analysis = st.session_state.get(
        "pak_marketguard_last_analysis"
    )

    if saved_analysis:
        show_analysis_results(saved_analysis)

    else:
        st.markdown(
            """
            <div class="result-panel">
                <div style="
                    color: #f1f7ff;
                    font-size: 20px;
                    font-weight: 750;
                    margin-bottom: 8px;
                ">
                    Your analysis will appear here
                </div>

                <div style="
                    color: #b1c4dc;
                    font-size: 14px;
                    line-height: 1.8;
                ">
                    Enter customer reviews and select
                    <strong>Analyze product risk</strong>
                    to view the screening results.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="footer-text">
            Pak-MarketGuard AI · AI-assisted e-commerce risk screening<br>
            Screening indicators support informed decisions; they do not
            prove that a seller, product, or review is fraudulent.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
