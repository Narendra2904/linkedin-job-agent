"""
FastAPI Web Dashboard & Cloud Service for Narendra Yenagandula's AI Job Tracker.
Provides multi-platform tracking (LinkedIn, Arbeitnow, RemoteOK, Naukri Helper),
real-time scoring for Fresher Frontend, Backend, and AI/ML tracks,
and 1-click cloud scan triggers for Render deployment.
"""

import os
import asyncio
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from tracker import JobTracker, EXCEL_PATH
from matcher import JobMatcher
from email_notifier import EmailNotifier
from auto_applier import AutoApplier

app = FastAPI(title="Narendra's Multi-Platform AI Job Agent")
tracker = JobTracker()
matcher = JobMatcher()
notifier = EmailNotifier()
applier = AutoApplier()

# Background task state
IS_SCANNING = False
LAST_SCAN_STATUS = "Ready"


def run_full_scan_sync(track: str = "all", location: str = "Hyderabad", limit_per_source: int = 5):
    """Background worker to fetch across platforms, match fresher roles, and email notifications."""
    global IS_SCANNING, LAST_SCAN_STATUS
    IS_SCANNING = True
    LAST_SCAN_STATUS = f"Scanning {track.upper()} roles across platforms..."
    print(f"\n[Dashboard Background Worker] Starting multi-platform scan for track: '{track}'...")

    try:
        from unified_scraper import UnifiedJobScraper
        scraper = UnifiedJobScraper()
        jobs = scraper.search_all_platforms(track=track, location=location, limit_per_source=limit_per_source)
        print(f"[Dashboard Background Worker] Retrieved {len(jobs)} total jobs across platforms.")

        high_matches = 0
        review_count = 0

        for j in jobs:
            job_id = j["job_id"]
            title = j["title"]
            company = j["company"]
            desc = j.get("description", "")
            source = j.get("source", "Web")

            # Evaluate match percentage
            match_res = matcher.evaluate_match(title, desc)
            score = match_res["score"]
            already_notified = tracker.is_already_notified(job_id)
            email_sent = 1 if already_notified else 0

            if score >= 70.0:
                status = f"Applied ({source} >=70%)"
                high_matches += 1
                if not already_notified:
                    sent = notifier.notify_job(j, match_res)
                    if sent:
                        email_sent = 1
            else:
                status = f"Review ({source} <70%)"
                review_count += 1
                if not already_notified and score >= 45.0:
                    sent = notifier.notify_job(j, match_res)
                    if sent:
                        email_sent = 1

            # Save in tracker
            tracker.upsert_job({
                "job_id": job_id,
                "title": f"[{source}] {title}",
                "company": company,
                "location": j.get("location", location),
                "job_url": j.get("job_url", ""),
                "match_score": score,
                "matched_skills": match_res.get("matched_skills", []),
                "missing_skills": match_res.get("missing_skills", []),
                "status": status,
                "email_sent": email_sent,
                "notes": f"Track: {match_res.get('track', 'GENERAL')} | Fresher Friendly: {match_res.get('is_fresher_friendly')}"
            })

        tracker.sync_to_excel()
        LAST_SCAN_STATUS = f"Completed at {datetime.now().strftime('%H:%M')} ({len(jobs)} jobs evaluated, {high_matches} >=70%)"
    except Exception as e:
        print(f"[Dashboard Background Worker] Error during scan: {e}")
        LAST_SCAN_STATUS = f"Scan error: {str(e)[:40]}"
    finally:
        IS_SCANNING = False


@app.on_event("startup")
async def startup_event():
    print("[Server Startup] Narendra's Job Tracker Backend Initialized.")
    # Run initial sync check
    tracker.sync_to_excel()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, filter_status: str = "", filter_track: str = ""):
    stats = tracker.get_statistics()
    all_jobs = tracker.get_all_jobs()

    # Filter logic
    jobs = []
    for j in all_jobs:
        status_match = True if not filter_status else (filter_status in j.get("status", ""))
        track_match = True
        if filter_track:
            notes = j.get("notes", "").lower()
            title = j.get("title", "").lower()
            if filter_track.lower() == "frontend":
                track_match = "frontend" in notes or any(k in title for k in ["front", "react", "html", "web"])
            elif filter_track.lower() == "backend":
                track_match = "backend" in notes or any(k in title for k in ["back", "python", "fastapi", "django"])
            elif filter_track.lower() == "aiml":
                track_match = "aiml" in notes or any(k in title for k in ["ai", "ml", "machine learning"])
        if status_match and track_match:
            jobs.append(j)

    rows_html = ""
    for j in jobs:
        score = float(j.get("match_score", 0.0))
        score_color = "#059669" if score >= 70.0 else ("#D97706" if score >= 45.0 else "#DC2626")
        status = j.get("status", "Review")

        badge_bg = "#D1FAE5" if "Applied" in status else ("#DBEAFE" if "Interview" in status else ("#FEE2E2" if "Reject" in status else "#FEF3C7"))
        badge_fg = "#065F46" if "Applied" in status else ("#1E40AF" if "Interview" in status else ("#991B1B" if "Reject" in status else "#92400E"))

        matched = j.get("matched_skills", "") or "-"
        missing = j.get("missing_skills", "") or "-"
        url = j.get("job_url", "#")
        job_id = j.get("job_id", "")
        rejection_notes = j.get("rejection_reason", "") or j.get("notes", "")

        rows_html += f"""
        <tr>
            <td style="font-weight:600;">{j.get('title', '')}<br/><span style="color:#6B7280;font-size:12px;">{j.get('company', '')} • {j.get('location', '')}</span></td>
            <td style="text-align:center;"><span style="font-size:16px;font-weight:700;color:{score_color};">{score:.1f}%</span></td>
            <td><span style="background-color:{badge_bg};color:{badge_fg};padding:4px 10px;border-radius:12px;font-size:12px;font-weight:600;">{status}</span></td>
            <td style="font-size:12px;color:#047857;">{matched}</td>
            <td style="font-size:12px;color:#B91C1C;">{missing}</td>
            <td style="font-size:12px;color:#4B5563;">{rejection_notes or '-'}</td>
            <td style="text-align:center;">
                <a href="{url}" target="_blank" style="color:#2563EB;text-decoration:none;font-weight:600;font-size:13px;">Apply / View &rarr;</a>
                <div style="margin-top:6px;">
                    <form method="POST" action="/update-status" style="display:inline;">
                        <input type="hidden" name="job_id" value="{job_id}">
                        <select name="new_status" onchange="this.form.submit()" style="font-size:11px;padding:3px 6px;border-radius:4px;border:1px solid #D1D5DB;">
                            <option value="" disabled selected>Update Status...</option>
                            <option value="Applied (Manual)">Applied (Manual)</option>
                            <option value="Interview Scheduled">Interview Scheduled</option>
                            <option value="Technical Round">Technical Round</option>
                            <option value="Rejected">Mark Rejected</option>
                            <option value="Offer Received">Offer Received</option>
                        </select>
                    </form>
                </div>
            </td>
        </tr>
        """

    scan_button_text = "⏳ Scan Running..." if IS_SCANNING else "🚀 Trigger Multi-Platform Scan"
    disabled_attr = "disabled" if IS_SCANNING else ""

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Narendra Yenagandula - Multi-Platform AI Job Agent</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
            body {{ background-color: #F8FAFC; margin: 0; padding: 24px; color: #1E293B; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; background: #FFFFFF; padding: 20px 28px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #E2E8F0; flex-wrap: wrap; gap: 14px; }}
            .header-title h1 {{ margin: 0; font-size: 22px; color: #0F172A; }}
            .header-title p {{ margin: 4px 0 0 0; color: #64748B; font-size: 14px; }}
            .btn {{ background-color: #2563EB; color: #FFF; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px; border: none; cursor: pointer; display: inline-flex; align-items: center; }}
            .btn:hover {{ opacity: 0.9; }}
            .btn-excel {{ background-color: #107C41; }}
            .btn-scan {{ background-color: #7C3AED; }}
            .action-bar {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 20px; }}
            .stat-card {{ background: #FFFFFF; padding: 16px 18px; border-radius: 10px; border: 1px solid #E2E8F0; }}
            .stat-label {{ font-size: 12px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
            .stat-value {{ font-size: 24px; font-weight: 700; color: #0F172A; margin-top: 4px; }}
            .card {{ background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 20px; }}
            .track-tags {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }}
            .track-badge {{ padding: 6px 14px; border-radius: 16px; font-size: 13px; text-decoration: none; font-weight: 600; border: 1px solid #CBD5E1; color: #334155; }}
            .track-badge.active {{ background: #0F172A; color: #FFFFFF; border-color: #0F172A; }}
            .quick-links {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; padding: 12px 16px; background: #EFF6FF; border-radius: 8px; border: 1px solid #BFDBFE; font-size: 13px; margin-bottom: 16px; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
            th {{ background: #F1F5F9; color: #475569; font-weight: 600; text-align: left; padding: 12px 14px; border-bottom: 2px solid #E2E8F0; }}
            td {{ padding: 12px 14px; border-bottom: 1px solid #F1F5F9; vertical-align: top; }}
            tr:hover {{ background-color: #F8FAFC; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="header-title">
                    <h1>🎯 Narendra Yenagandula - Multi-Platform AI Job Agent</h1>
                    <p>Fresher Candidate (2026 Batch) | <strong>Tracks:</strong> Frontend Developer • Backend (Python/FastAPI) • AI/ML Engineer</p>
                </div>
                <div class="action-bar">
                    <form method="POST" action="/trigger-scan" style="display:inline;">
                        <input type="hidden" name="track" value="{filter_track or 'all'}">
                        <button type="submit" class="btn btn-scan" {disabled_attr}>{scan_button_text}</button>
                    </form>
                    <a href="/download-excel" class="btn btn-excel">📥 Download Excel Sheet</a>
                </div>
            </div>

            <!-- Quick Naukri & Platform Portal Bar -->
            <div class="quick-links">
                <strong>⚡ Direct Naukri & Job Board Fresher Portals:</strong>
                <a href="https://www.naukri.com/fresher-python-developer-jobs-in-hyderabad" target="_blank" style="color:#1D4ED8;font-weight:600;">Naukri (Python Fresher) ↗</a> •
                <a href="https://www.naukri.com/fresher-frontend-developer-jobs-in-hyderabad" target="_blank" style="color:#1D4ED8;font-weight:600;">Naukri (Frontend Fresher) ↗</a> •
                <a href="https://www.naukri.com/fresher-ai-ml-jobs-in-hyderabad" target="_blank" style="color:#1D4ED8;font-weight:600;">Naukri (AI/ML Fresher) ↗</a> •
                <span style="color:#4B5563;">Status: {LAST_SCAN_STATUS}</span>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Jobs Scanned</div>
                    <div class="stat-value">{stats['total_jobs_tracked']}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">High Matches (&ge;70%)</div>
                    <div class="stat-value" style="color:#059669;">{stats['high_matches_70_plus']}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Applications</div>
                    <div class="stat-value" style="color:#2563EB;">{stats['total_applied']}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Interviews Scheduled</div>
                    <div class="stat-value" style="color:#7C3AED;">{stats['interviews_scheduled']}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Rejections Monitored</div>
                    <div class="stat-value" style="color:#DC2626;">{stats['rejected_count']}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Job Offers</div>
                    <div class="stat-value" style="color:#10B981;">{stats['offers_received']}</div>
                </div>
            </div>

            <div class="card">
                <!-- Track Filters -->
                <div class="track-tags">
                    <strong style="font-size:14px;color:#334155;align-self:center;">Role Track:</strong>
                    <a href="/?filter_track=&filter_status={filter_status}" class="track-badge {'active' if not filter_track else ''}">All Roles</a>
                    <a href="/?filter_track=frontend&filter_status={filter_status}" class="track-badge {'active' if filter_track == 'frontend' else ''}">💻 Frontend Track (HTML/CSS/JS)</a>
                    <a href="/?filter_track=backend&filter_status={filter_status}" class="track-badge {'active' if filter_track == 'backend' else ''}">⚙️ Backend Track (Python/FastAPI)</a>
                    <a href="/?filter_track=aiml&filter_status={filter_status}" class="track-badge {'active' if filter_track == 'aiml' else ''}">🤖 AI/ML Track</a>
                </div>

                <div style="overflow-x:auto;">
                    <table>
                        <thead>
                            <tr>
                                <th style="width:24%;">Job Title & Company</th>
                                <th style="width:10%;text-align:center;">Match Score</th>
                                <th style="width:14%;">Status</th>
                                <th style="width:20%;">Matched Skills</th>
                                <th style="width:16%;">Missing Skills</th>
                                <th style="width:10%;">Notes / Track</th>
                                <th style="width:10%;text-align:center;">Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html if rows_html else '<tr><td colspan="7" style="text-align:center;padding:32px;color:#94A3B8;">No job applications found matching filter. Click \"Trigger Multi-Platform Scan\" above to fetch fresh roles!</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.post("/trigger-scan")
async def trigger_scan(background_tasks: BackgroundTasks, track: str = Form("all")):
    global IS_SCANNING
    if not IS_SCANNING:
        background_tasks.add_task(run_full_scan_sync, track=track, location="Hyderabad", limit_per_source=6)
    return RedirectResponse(url=f"/?filter_track={track}", status_code=303)


@app.post("/update-status")
async def update_status(job_id: str = Form(...), new_status: str = Form(...)):
    tracker.update_status(job_id=job_id, new_status=new_status)
    return RedirectResponse(url="/", status_code=303)


@app.get("/download-excel")
async def download_excel():
    tracker.sync_to_excel()
    return FileResponse(
        path=EXCEL_PATH,
        filename="job_applications_tracker.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
