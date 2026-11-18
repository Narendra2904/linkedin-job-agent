# 🤖 Narendra's Autonomous AI/ML LinkedIn Job Agent & Application Tracker

An intelligent automation suite built specifically for **Narendra Yenagandula** (`yenagandula.narendra@gmail.com`). 
It fetches real-time jobs from LinkedIn, compares each job's requirements against your resume profile (`AIML.pdf`), calculates a precise match percentage, automatically routes high-match jobs (&ge;70%) for application, dispatches email alerts, and maintains a comprehensive application tracker in both SQLite and formatted Excel (`.xlsx`).

---

## 🌟 Key Features

1. **Live LinkedIn Job Scraping (Zero Risk)**:
   - Fetches real-time jobs in **Hyderabad**, **Bengaluru**, **Remote**, or any custom location.
   - Uses LinkedIn guest endpoints: does not trigger bot-detection or risk your personal account.
2. **AI Requirement Matching Engine**:
   - Uses TF-IDF cosine similarity, keyword extraction, and skill overlap scoring.
   - Evaluates your core skills (*Python, Machine Learning, SVM, Image Classification, FastAPI, MySQL, Scikit-Learn*).
   - Generates detailed match reports with **Matched Skills** vs **Missing Skills**.
3. **Automated Application & Action Routing**:
   - **&ge; 70% Match**: Automatically queued and marked as `Applied (Auto >=70%)`. Prepares tailored recruiter pitch notes and dispatches an instant High-Match Email.
   - **< 70% Match**: Dispatches an Email Alert with the direct job link and missing skills breakdown for your review.
4. **Complete Application Tracker Sheet**:
   - Maintains `data/job_applications_tracker.xlsx` with interactive KPI Dashboard and color-coded status badges:
     - 🟢 `Applied (Auto >=70%)`
     - 🟡 `Sent for Review (<70%)`
     - 🔵 `Interview Scheduled`
     - 🔴 `Rejected` (with full reason/feedback tracking)
     - 🟢 `Offer Received`
5. **Interactive Web Dashboard**:
   - Local FastAPI portal running at `http://localhost:8000` to browse scanned jobs, filter rejections, change statuses, and download the Excel file with 1 click.

---

## 🚀 Quick Start Guide

### 1. Run Job Agent (Scan & Match)
To fetch and evaluate the latest 10 AI/ML jobs in Hyderabad:
```bash
python main.py --scan
```

### 2. Search Specific Roles or Locations
```bash
# Search Python Developer roles
python main.py --scan --keyword "Python Developer" --location "Hyderabad" --limit 10

# Search Machine Learning roles in Bengaluru
python main.py --scan --keyword "Machine Learning Engineer" --location "Bengaluru" --limit 15
```

### 3. Launch Local Web Tracker Dashboard
```bash
python main.py --dashboard
```
Open **http://localhost:8000** in your browser.

### 4. Check Tracker Statistics
```bash
python main.py --stats
```

### 5. Mark a Job as Rejected or Interview Scheduled
```bash
# Mark as Rejected with feedback notes
python main.py --update 4457416123 --status "Rejected" --reason "Required 4+ years in microservices"

# Mark as Interview Scheduled
python main.py --update 4489540748 --status "Interview Scheduled" --notes "HR screening on Monday at 3 PM"
```

### 6. Open Excel Tracker Directly
```bash
python main.py --open-excel
```
Or open `data/job_applications_tracker.xlsx` in Microsoft Excel.

---

## 📧 Email Alerts Setup (Optional)
To receive real emails to `yenagandula.narendra@gmail.com`:
1. Open your Google Account: [App Passwords](https://myaccount.google.com/apppasswords).
2. Generate a 16-character App Password for "Mail".
3. Open `.env` in this folder and paste it into `SMTP_PASSWORD`:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=yenagandula.narendra@gmail.com
   SMTP_PASSWORD=your_16_char_password_here
   RECIPIENT_EMAIL=yenagandula.narendra@gmail.com
   ```
*(Note: If left empty, the agent saves local HTML email previews in `data/email_previews/` so you can review them locally).*

---

## 📁 Project Architecture
```
linkedin/
├── AIML.pdf                           # Candidate Resume
├── profile_data.py                    # Structured candidate skills & profile knowledge base
├── matcher.py                         # TF-IDF & Skill matching scoring engine
├── job_scraper.py                     # Safe LinkedIn public guest API scraper
├── auto_applier.py                    # Application dispatcher & custom cover pitch generator
├── email_notifier.py                  # HTML email alert generator & SMTP dispatcher
├── tracker.py                         # SQLite & openpyxl Excel tracker generator
├── dashboard.py                       # FastAPI local interactive web portal
├── main.py                            # Unified CLI controller
├── .env                               # SMTP & search configuration
└── data/
    ├── job_tracker.db                 # SQLite persistent database
    ├── job_applications_tracker.xlsx  # Styled Excel tracker spreadsheet
    ├── jobs_cache.json                # Job description cache
    └── email_previews/                # Generated HTML email alerts
```
