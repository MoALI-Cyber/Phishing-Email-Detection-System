# PHISHIOR - Phishing Email Detection Website

## Overview
PHISHIOR is an intelligent, web-based system designed to analyze incoming emails and determine whether they are phishing or legitimate. By detecting suspicious patterns such as urgent language, fake login requests, suspicious links, and phishing-related keywords, this tool helps protect everyday users from online fraud, data breaches, and identity theft. 

## Problem Statement & Solution
Phishing attacks are becoming increasingly sophisticated, making it difficult for non-technical users to distinguish between real and fake emails. PHISHIOR provides an accessible, user-friendly platform where users can paste or upload suspicious email content. The system automates the analysis using machine learning and text classification algorithms, providing a clear verdict along with an explanation of the warning signs.

## Key Features
* **Multiple Input Types:** Supports analyzing uploaded EML files, copied phone messages, direct URLs, or plain text.
* **Advanced & Quick Scans:** Offers advanced analysis using email headers, sender details, and links, as well as a quick scan for copied text.
* **URL Insights:** Evaluates the top 3 important URLs in the email by checking WHOIS records, TLS certificates, and optionally integrating with the VirusTotal API.
* **Machine Learning Analysis:** Uses a model trained on labelled datasets of phishing and legitimate emails, utilizing TF-IDF to represent important words and patterns inside the email content.
* **Clear Reporting:** Displays a clear verdict (Phishing or Legitimate), a confidence score, and a plain language explanation of the reasons and ratings (e.g., SPF/DKIM pass, known company context).

## Tech Stack
* **Backend:** Python (Flask)
* **Frontend:** HTML, CSS, JavaScript
* **Machine Learning:** Natural Language Processing (NLP), TF-IDF vectorization, and text classification algorithms

## System Workflow
1. The user opens the PHISHIOR website and inputs the suspicious email content or EML file.
2. The Flask backend validates the input to prevent empty or unsuitable submissions.
3. The feature extraction phase cleans the text, detects URLs, and creates TF-IDF vectors.
4. The machine learning model predicts whether the content is phishing or legitimate and calculates a confidence score.
5. The result page displays the final verdict and a simple explanation to the user.

## Future Enhancements
* Expanding the system to scan for attachments, images, and QR-code phishing attempts.
* Integrating the tool directly with email clients.
* Implementing advanced deep-learning or transformer models for higher accuracy.

## Included fixes

- The old visual design is preserved.
- Computer / Phone mode now works coherently with the backend.
- Phone mode does quick copied-message/link checks only.
- Computer mode supports email text and EML header checks.
- Scores `70+` return `Likely Phishing` with `High` confidence.
- Generic words like `Here` and `Information` are no longer treated as company names.
- Real trusted companies are stored in `data/companies.csv`.
- Blacklist management endpoints work.
- Results are saved in `logs`.

## Run

```bash
pip install -r requirements.txt
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

The app runs with:

```python
app.run(debug=True, host="0.0.0.0", port=5000)
```

## Author
**Mohamed Ali Mohamed Ahmed**
* **Project:** Arab Open University - TM471 Final Year Project
* **Supervisor:** Mostafa Salem
