# 🤖 Narendra's Multi-Platform Fresher Job Agent & Application Tracker

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Narendra2904/linkedin-job-agent)

An autonomous job discovery, requirement matching, and application tracking platform designed for **Narendra Yenagandula** (`yenagandula.narendra@gmail.com`).

Built specifically for **Fresher Roles (2026 Batch)** across three core engineering tracks:
1. **Frontend Development Track**: HTML5, CSS3, JavaScript, Flexbox, CSS Grid, Responsive Web Design, Vercel
2. **Backend Development Track**: Python, FastAPI, MySQL, REST APIs, JSON, SQL
3. **AI / Machine Learning Track**: Machine Learning, Supervised Learning, Support Vector Machines (SVM), Image Classification, Scikit-Learn

Aggregates real-time listings across **LinkedIn**, **Arbeitnow**, and **RemoteOK**, with quick portals for **Naukri**, compares them against your resume, routes $\ge 70\%$ high matches, prevents duplicate emails, and tracks everything in both SQLite and a stylized Excel workbook.

---

## 🌟 Key Features

1. **Multi-Platform Job Discovery**:
   - **LinkedIn Guest API**: Safe, real-time scraping without bot blocks or account risks.
   - **Arbeitnow Public API**: Instant access to tech & remote developer positions.
   - **RemoteOK API**: Developer & AI job postings.
   - **Naukri Direct Fresher Portals**: Instant 1-click links directly into pre-filtered fresher search pages.
2. **Fresher-Optimized Matching Engine**:
   - **Fresher Boost (+15%)**: Prioritizes jobs mentioning *Fresher*, *Entry Level*, *Junior*, *Intern*, *0-1 years*, *2026 passout*.
   - **Senior Role Protection**: Automatically discounts senior, lead, or 4+ year roles so you only apply to suitable positions.
   - **Track-Aware Scoring**: Tailors skill evaluation according to whether the role is Frontend, Backend, or AI/ML.
3. **Smart Idempotency (Zero Duplicate Emails)**:
   - Database-backed deduplication records every notified job ID in SQLite.
   - Re-running scans will **never send the same job twice**.
4. **Excel Application Tracker & Cloud Dashboard**:
   - Beautiful multi-tab Excel tracker [`data/job_applications_tracker.xlsx`](file:///C:/Users/yenag/Downloads/linkedin/data/job_applications_tracker.xlsx) with KPI summary cards and status coloring.
   - Web UI accessible at `http://localhost:8000` or on your local network (`http://10.193.18.214:8000`).
5. **Render & Cloud Ready**:
   - Pre-configured `render.yaml` for 1-click deployment on Render.

---

## 🚀 Quick Usage (CLI)

### 1. Scan by Track
```bash
# Scan all tracks (Frontend, Backend, AI/ML)
python main.py --scan --track all

# Scan Frontend Fresher roles
python main.py --scan --track frontend --limit 5

# Scan Backend Fresher roles (Python / FastAPI)
python main.py --scan --track backend --limit 5

# Scan AI/ML Fresher roles
python main.py --scan --track aiml --limit 5
```

### 2. Launch Local / Network Web Dashboard
```bash
python main.py --dashboard
```
- Open **http://localhost:8000** on your computer.
- Open **http://10.193.18.214:8000** from your phone or any device on your Wi-Fi!

### 3. Update Status / Log Rejection
```bash
# Mark as Rejected with notes
python main.py --update <job_id> --status "Rejected" --reason "Experience mismatch"

# Mark as Interview Scheduled
python main.py --update <job_id> --status "Interview Scheduled" --notes "Technical screening on Friday"
```

---

## ☁️ Deploying to Render (Free Cloud Hosting)

This project includes a ready-to-use [`render.yaml`](file:///C:/Users/yenag/Downloads/linkedin/render.yaml) blueprint:

1. **Push your code to GitHub** (see below).
2. Go to **[dashboard.render.com](https://dashboard.render.com/)** and click **New +** &rarr; **Blueprint**.
3. Connect your GitHub repository (`linkedin-job-agent`).
4. Under Environment Variables, set:
   - `SMTP_PASSWORD`: Your 16-character Google App Password (`hbsa plaz cfwu rthm`).
   - `RECIPIENT_EMAIL`: `yenagandula.narendra@gmail.com`.
5. Click **Apply**. Render will automatically build, deploy, and give you a live public HTTPS URL (e.g. `https://narendra-ai-job-agent.onrender.com`) where you can trigger scans and track jobs from anywhere!

---

## 📤 Pushing to GitHub

Run these commands in PowerShell:
```powershell
# 1. Add your GitHub repository as remote (replace with your repo URL)
git remote add origin https://github.com/Narendra2904/linkedin-job-agent.git

# 2. Push to GitHub
git push -u origin main
```
*(Your secrets in `.env` are protected by `.gitignore` and will never be pushed).*
