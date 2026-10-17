import streamlit as st
from gtts import gTTS
from io import BytesIO

from app.agent import run_analysis
from app.report_generator import generate_pdf_report


st.set_page_config(
    page_title="Pak-MarketGuard AI",
    page_icon="🛡️",
    layout="wide",
)


# --------------------------------------------------
# TEXT-TO-SPEECH: GENERATE MP3 AUDIO
# --------------------------------------------------

@st.cache_data(show_spinner=False)
def generate_speech(text, language):
    """Generate audio bytes for the requested language."""
    audio_buffer = BytesIO()

    tts = gTTS(
        text=text,
        lang=language,
        slow=False,
    )
    tts.write_to_fp(audio_buffer)

    audio_buffer.seek(0)
    return audio_buffer.getvalue()


def safe_int(value, default=0):
    """Safely convert a value into an integer."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_review_metrics(review_result, reviews):
    """Get the exact metrics used by both dashboard and speech."""
    return {
        "review_count": safe_int(
            review_result.get("review_count", len(reviews)),
            len(reviews),
        ),
        "exact_group_count": len(
            review_result.get("exact_duplicate_groups", [])
        ),
        "similar_pair_count": len(
            review_result.get("near_duplicate_pairs", [])
        ),
        "generic_praise_count": safe_int(
            review_result.get("generic_review_count", 0)
        ),
    }


def make_english_report(
    score,
    risk_level,
    recommendation,
    metrics,
):
    """Build English speech from the current analysis results."""
    return (
        "Pak Market Guard analysis report. "
        f"Risk score: {score} out of 100. "
        f"Risk level: {risk_level}. "
        f"Reviews analyzed: {metrics['review_count']}. "
        f"Groups of exact duplicate reviews: "
        f"{metrics['exact_group_count']}. "
        f"Similar review pairs: "
        f"{metrics['similar_pair_count']}. "
        f"Generic praise reviews: "
        f"{metrics['generic_praise_count']}. "
        f"Recommendation: {recommendation}. "
        "This score is a heuristic screening result, "
        "not proof of fraud."
    )


def make_urdu_report(
    score,
    risk_level,
    recommendation,
    metrics,
):
    """Build an Urdu-language report from the same results."""

    urdu_levels = {
        "Low": "کم خطرہ",
        "Moderate": "درمیانہ خطرہ",
        "High": "زیادہ خطرہ",
    }

    urdu_recommendations = {
        "Low": (
            "اس لسٹنگ میں کم خطرے کے اشارے ملے ہیں۔ "
            "خریداری سے پہلے تفصیلات ضرور دیکھیں۔"
        ),
        "Moderate": (
            "اس لسٹنگ میں کچھ خطرے کے اشارے ملے ہیں۔ "
            "خریداری سے پہلے مزید تحقیق کریں۔"
        ),
        "High": (
            "اس لسٹنگ میں خطرے کے کئی اشارے ملے ہیں۔ "
            "خریداری سے پہلے احتیاط سے تصدیق کریں۔"
        ),
    }

    level_urdu = urdu_levels.get(
        risk_level,
        str(risk_level),
    )

    recommendation_urdu = urdu_recommendations.get(
        risk_level,
        str(recommendation),
    )

    return (
        "پاکستان مارکیٹ گارڈ کی تجزیاتی رپورٹ۔ "
        f"خطرے کا اسکور ایک سو میں سے {score} ہے۔ "
        f"خطرے کی سطح {level_urdu} ہے۔ "
        f"تجزیہ کیے گئے ریویوز کی تعداد "
        f"{metrics['review_count']} ہے۔ "
        f"بالکل ایک جیسے ریویوز کے گروپس کی تعداد "
        f"{metrics['exact_group_count']} ہے۔ "
        f"ملتے جلتے ریویوز کے جوڑوں کی تعداد "
        f"{metrics['similar_pair_count']} ہے۔ "
        f"عمومی تعریف والے ریویوز کی تعداد "
        f"{metrics['generic_praise_count']} ہے۔ "
        f"تجویز: {recommendation_urdu} "
        "یہ اسکور خطرے کے اشاروں پر مبنی ہے، "
        "دھوکہ دہی کا حتمی ثبوت نہیں۔"
    )


# --------------------------------------------------
# DISPLAY EVIDENCE
# --------------------------------------------------

def show_review_evidence(review_result):
    st.subheader("Review Analysis Evidence")

    exact_groups = review_result.get(
        "exact_duplicate_groups", []
    )
    similar_pairs = review_result.get(
        "near_duplicate_pairs", []
    )

    with st.expander("Exact duplicate review groups"):
        if exact_groups:
            for index, group in enumerate(exact_groups, start=1):
                st.write(f"**Group {index}**")
                st.write(group)
        else:
            st.info("No exact duplicate groups detected.")

    with st.expander("Similar review pairs"):
        if similar_pairs:
            for index, pair in enumerate(similar_pairs, start=1):
                st.write(f"**Pair {index}**")
                st.write(pair)
        else:
            st.info("No similar review pairs detected.")


def show_image_evidence(image_result):
    st.subheader("Image Analysis Evidence")

    if not image_result:
        st.info("No image comparison was performed.")
        return

    if isinstance(image_result, dict):
        for key, value in image_result.items():
            st.write(f"**{key.replace('_', ' ').title()}:**")
            st.write(value)
    else:
        st.write(image_result)


# --------------------------------------------------
# MAIN APPLICATION
# --------------------------------------------------

def main():
    st.title("🛡️ Pak-MarketGuard AI")
    st.subheader(
        "AI-Assisted E-commerce Risk Screening"
    )

    st.write(
        "Analyze product reviews and optionally compare "
        "a listing image with a reference image to identify "
        "potential risk indicators."
    )

    st.warning(
        "This tool provides heuristic risk screening. "
        "Its score is not a probability of fraud and does "
        "not prove that a seller or product is fraudulent."
    )

    st.divider()

    # Product information
    st.header("1. Product Information")

    product_name = st.text_input(
        "Product name (optional)",
        placeholder="e.g., Wireless Headphones",
    )

    # Reviews
    st.header("2. Product Reviews")

    review_text = st.text_area(
        "Enter reviews, one review per line",
        height=220,
        placeholder=(
            "Excellent product and fast delivery\n"
            "Very good quality\n"
            "Excellent product and fast delivery"
        ),
    )

    reviews = [
        line.strip()
        for line in review_text.splitlines()
        if line.strip()
    ]

    # Images
    st.header("3. Optional Image Comparison")

    col1, col2 = st.columns(2)

    with col1:
        listing_file = st.file_uploader(
            "Upload product listing image",
            type=["png", "jpg", "jpeg", "webp"],
            key="listing_image",
        )

    with col2:
        reference_file = st.file_uploader(
            "Upload reference image",
            type=["png", "jpg", "jpeg", "webp"],
            key="reference_image",
        )

    if listing_file:
        st.image(
            listing_file,
            caption="Product listing image",
            width=300,
        )

    if reference_file:
        st.image(
            reference_file,
            caption="Reference image",
            width=300,
        )

    st.divider()

    # Run analysis
    if st.button(
        "Analyze Product",
        type="primary",
        use_container_width=True,
    ):
        if not reviews and not listing_file:
            st.error(
                "Please enter at least one review "
                "or upload a product listing image."
            )
            return

        try:
            with st.spinner("Analyzing product risk..."):
                image_bytes = (
                    listing_file.getvalue()
                    if listing_file
                    else None
                )

                reference_image_bytes = (
                    reference_file.getvalue()
                    if reference_file
                    else None
                )

                result = run_analysis(
                    reviews=reviews,
                    image_bytes=image_bytes,
                    reference_image_bytes=reference_image_bytes,
                )

            review_result = result.get(
                "review_result", {}
            )
            image_result = result.get(
                "image_result", {}
            )
            risk_result = result.get(
                "risk_result", {}
            )

            # Read values once, then reuse them everywhere.
            metrics = get_review_metrics(
                review_result,
                reviews,
            )

            score = safe_int(
                risk_result.get("risk_score", 0)
            )
            score = max(0, min(100, score))

            risk_level = risk_result.get(
                "risk_level", "Unknown"
            )

            recommendation = risk_result.get(
                "recommendation",
                "Review the available evidence before purchasing.",
            )

            # Save the latest result for the report section.
            st.session_state["latest_analysis"] = {
                "product_name": product_name,
                "reviews": reviews,
                "review_result": review_result,
                "image_result": image_result,
                "risk_result": risk_result,
                "metrics": metrics,
                "score": score,
                "risk_level": risk_level,
                "recommendation": recommendation,
            }

        except Exception as error:
            st.error(
                "Analysis failed. Please check your project "
                "modules and try again."
            )
            st.exception(error)
            return

    # Display the latest result, including after a rerun.
    analysis = st.session_state.get("latest_analysis")

    if not analysis:
        return

    st.divider()
    st.header("4. Risk Assessment")

    score = analysis["score"]
    risk_level = analysis["risk_level"]
    recommendation = analysis["recommendation"]
    metrics = analysis["metrics"]

    metric1, metric2 = st.columns(2)

    with metric1:
        st.metric(
            "Risk Score",
            f"{score}/100",
        )

    with metric2:
        st.metric(
            "Risk Level",
            risk_level,
        )

    st.progress(score / 100)

    st.subheader("Recommendation")
    st.write(recommendation)

    # These counts use the same metrics as the audio reports.
    st.subheader("Review Metrics")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Reviews Analyzed",
        metrics["review_count"],
    )

    m2.metric(
        "Exact Duplicate Groups",
        metrics["exact_group_count"],
    )

    m3.metric(
        "Similar Review Pairs",
        metrics["similar_pair_count"],
    )

    m4.metric(
        "Generic Praise Reviews",
        metrics["generic_praise_count"],
    )

    # Evidence sections
    show_review_evidence(
        analysis["review_result"]
    )

    show_image_evidence(
        analysis["image_result"]
    )

    # --------------------------------------------------
    # ENGLISH AND URDU AUDIO
    # --------------------------------------------------

    st.divider()
    st.header("5. Listen to the Risk Report")

    english_report = make_english_report(
        score,
        risk_level,
        recommendation,
        metrics,
    )

    urdu_report = make_urdu_report(
        score,
        risk_level,
        recommendation,
        metrics,
    )

    audio_col1, audio_col2 = st.columns(2)

    with audio_col1:
        st.subheader("English Voice")

        if st.button(
            "Generate English Audio",
            use_container_width=True,
        ):
            try:
                with st.spinner(
                    "Generating English speech..."
                ):
                    audio_bytes = generate_speech(
                        english_report,
                        "en",
                    )

                st.session_state["english_audio"] = (
                    audio_bytes
                )

            except Exception:
                st.error(
                    "English audio generation failed. "
                    "Check your internet connection and retry."
                )

        if st.session_state.get("english_audio"):
            st.audio(
                st.session_state["english_audio"],
                format="audio/mp3",
            )

    with audio_col2:
        st.subheader("Urdu Voice")

        if st.button(
            "Generate Urdu Audio",
            use_container_width=True,
        ):
            try:
                with st.spinner(
                    "Generating Urdu speech..."
                ):
                    audio_bytes = generate_speech(
                        urdu_report,
                        "ur",
                    )

                st.session_state["urdu_audio"] = (
                    audio_bytes
                )

            except Exception:
                st.error(
                    "Urdu audio generation failed. "
                    "Check your internet connection and retry."
                )

        if st.session_state.get("urdu_audio"):
            st.audio(
                st.session_state["urdu_audio"],
                format="audio/mp3",
            )

    # --------------------------------------------------
    # PDF REPORT
    # --------------------------------------------------

    st.divider()
    st.header("6. Download Report")

    if st.button(
        "Generate PDF Report",
        use_container_width=True,
    ):
        try:
            pdf_data = generate_pdf_report(
    analysis["reviews"],
    analysis["review_result"],
    analysis["image_result"],
    analysis["risk_result"],
    metrics=analysis["metrics"],
    product_name=analysis["product_name"],
    display_score=analysis["score"],
    display_risk_level=analysis["risk_level"],
    recommendation=analysis["recommendation"],
)
            st.session_state["pdf_report"] = pdf_data

        except Exception as error:
            st.error(
                "PDF generation failed. Check "
                "app/report_generator.py."
            )
            st.exception(error)

    if st.session_state.get("pdf_report") is not None:
        st.download_button(
            label="Download PDF",
            data=st.session_state["pdf_report"],
            file_name="pak_marketguard_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
