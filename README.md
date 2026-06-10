# Shreyas Mahimkar - Resume Dashboard

An interactive, high-fidelity Streamlit web application that dynamically reads and displays the resume of Shreyas Mahimkar from Google Docs.

- **Google Doc Source:** [Shreyas Mahimkar Resume](https://docs.google.com/document/d/1bbPRlF2jy3Jkh94Vuw2scdsqQUB51RF8pINoiZ3GUv8/edit?tab=t.0)
- **Local Fallback:** Cached structure saved in `resume_fallback.json` to allow offline rendering.

---

## Technical Features

1. **Dynamic Resume Parsing:** The application fetches the raw text from the Google Doc export endpoint `https://docs.google.com/document/d/1bbPRlF2jy3Jkh94Vuw2scdsqQUB51RF8pINoiZ3GUv8/export?format=txt`.
2. **Intelligent Grouping & Cleaning:** Custom parsing functions process contact headers, handle complex formatting boundaries (like nested list punctuation/parentheses), format the professional experience timeline, and group education institutions with their degrees.
3. **Premium UX/UI:** Structured tab layout, responsive columns, and Google Fonts CSS injection for state-of-the-art visual presentation in Streamlit.
4. **Resilient Architecture:** Features a local JSON fallback caching mechanism. If the external fetch fails, it gracefully serves the cached version.

---

## Getting Started

### Prerequisites
- Python 3.11+ (tested with Python 3.14.5)

### Installation

1. Create a Python virtual environment:
   ```bash
   python3 -m venv .venv
   ```

2. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```

3. Install required dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Running the App

Start the Streamlit application local development server:
```bash
streamlit run app.py
```

After running the command, Streamlit will open a tab in your default web browser (typically at `http://localhost:8501`).

To sync any updates made to the Google Doc live, click the **"Sync Live from Google Doc"** button in the sidebar.
