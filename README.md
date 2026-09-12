# Phishior - old UI with new detection logic

This version keeps your uploaded old interface shape from `index.html` and `main.js`, while updating the backend logic.

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