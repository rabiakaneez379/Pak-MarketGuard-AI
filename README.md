# Pak-MarketGuard AI
### AI-Assisted E-commerce Risk Screening

**Pak-MarketGuard AI** is a Python-based application that helps users identify potential warning signs in e-commerce product listings by analyzing customer-review patterns and optionally comparing product images.

## Project Features

- **Review Pattern Analysis:** Detects exact duplicate reviews and configured generic-praise patterns.
- **Product Image Comparison:** Analyzes image metadata and perceptual hashes to compare a listing image with a supplied reference image.
- **Risk Assessment:** Calculates a rule-based screening score and assigns a risk category.
- **Evidence and Recommendations:** Explains the detected indicators, recommendations, and system limitations.
- **Multilingual Audio:** Provides recommendation audio in English and Urdu.
- **PDF Reports:** Generates a downloadable screening report.

## Technologies Used

- Python 3.11
- Streamlit
- Image processing and perceptual hashing
- Rule-based text analysis
- PDF report generation
- Text-to-speech

## Installation and Setup

1. Install Python 3.11.
2. Open the project folder in Visual Studio Code.
3. Open a terminal in the project root.
4. Activate the project's virtual environment.

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

5. Install the dependencies listed in `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

6. Start the application:

```powershell
python -m streamlit run app/main.py
```

## How to Use

1. Enter the product name.
2. Paste customer reviews into the review field.
3. Optionally upload a product listing image and a reference image.
4. Run the screening.
5. Review the score, detected patterns, image comparison, evidence, and recommendations.
6. Select English or Urdu for audio playback.
7. Download the PDF screening report.

## Testing

The application was tested using:

- Three distinct customer reviews.
- Repeated reviews to test duplicate detection.
- A listing image and a reference image.
- Empty review input.
- PDF report generation.
- English and Urdu recommendation audio.

In one test, three distinct reviews produced a score of 0/100 (Low Risk), with no configured warning indicators detected. This result applies only to that test input.

## Limitations

- The score is a heuristic screening score, not a probability of fraud.
- A low score does not guarantee that a product or seller is trustworthy.
- Perceptual image hashes cannot prove product authenticity.
- Image cropping, editing, and compression can affect image comparisons.
- Roman Urdu and other language variations may be missed.
- The current rule-based system is not a fully trained fraud-classification model.

## Future Improvements

- Evaluate the system on a larger, labeled dataset.
- Measure model performance using precision, recall, and F1-score.
- Improve multilingual review analysis.
- Develop more robust product-image comparison.
- Add further evidence-based screening methods.

## Responsible Use

Pak-MarketGuard AI is intended to support informed shopping decisions. Its results should not be treated as definitive proof of fraudulent behavior. Important claims should be independently verified.

## Project Information

- **Project:** Pak-MarketGuard AI
- **Event:** CSS AI Bootcamp 2026 Capstone
- **Program:** BS Artificial Intelligence
- **Institution:** University of Peshawar
- **Author:** [Enter your full name]
