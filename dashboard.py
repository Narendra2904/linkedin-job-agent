"""
FastAPI Web Dashboard for Narendra Yenagandula's AI Job Tracker.
Provides an interactive web interface to view jobs, match percentages, filter rejections/interviews,
and trigger fresh job scans directly from your browser.
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from tracker import JobTracker, EXCEL_PATH

app = FastAPI(title="Narendra's AI Job Application Portal")
tracker = JobTracker()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, filter_status: str = ""):
    stats = tracker.get_statistics()
    jobs = tracker.get_all_jobs(status_filter=filter_status if filter_status else None)

    # Render HTML
    rows_html = ""
    for j in jobs:
        score = float(j.get("match_score", 0.0))
        score_color = "#059669" if score >= 70.0 else ("#D97706" if score >= 45.0 else "#DC2626")
        status = j.get("status", "Review")
        
        # Status badge color
        badge_bg = "#D1FAE5" if "Applied" in status else ("#DBEAFE" if "Interview" in status else ("#FEE2E2" if status == "Rejected" else "#FEF3C7"))
        badge_fg = "#065F46" if "Applied" in status else ("#1E40AF" if "Interview" in status else ("#991B1B" if status == "Rejected" else "#92400E"))

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
                <a href="{url}" target="_blank" style="color:#2563EB;text-decoration:none;font-weight:600;font-size:13px;">Open Job &rarr;</a>
                <div style="margin-top:6px;">
                    <form method="POST" action="/update-status" style="display:inline;">
                        <input type="hidden" name="job_id" value="{job_id}">
                        <select name="new_status" onchange="this.form.submit()" style="font-size:11px;padding:3px 6px;border-radius:4px;border:1px solid #D1D5DB;">
                            <option value="" disabled selected>Change Status...</option>
                            <option value="Applied (Auto >=70%)">Applied (Auto)</option>
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

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Narendra Yenagandula - AI Job Portal & Tracker</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
            body {{ background-color: #F8FAFC; margin: 0; padding: 24px; color: #1E293B; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; background: #FFFFFF; padding: 20px 28px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 24px; border: 1px solid #E2E8F0; }}
            .header-title h1 {{ margin: 0; font-size: 22px; color: #0F172A; }}
            .header-title p {{ margin: 4px 0 0 0; color: #64748B; font-size: 14px; }}
            .btn {{ background-color: #2563EB; color: #FFF; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px; border: none; cursor: pointer; display: inline-flex; align-items: center; }}
            .btn-excel {{ background-color: #107C41; margin-left: 10px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
            .stat-card {{ background: #FFFFFF; padding: 18px 20px; border-radius: 10px; border: 1px solid #E2E8F0; }}
            .stat-label {{ font-size: 13px; color: #64748B; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }}
            .stat-value {{ font-size: 28px; font-weight: 700; color: #0F172A; margin-top: 6px; }}
            .card {{ background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
            .filters {{ display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; }}
            .filter-btn {{ padding: 6px 14px; border-radius: 20px; font-size: 13px; text-decoration: none; font-weight: 500; border: 1px solid #CBD5E1; color: #334155; }}
            .filter-btn.active {{ background: #2563EB; color: #FFFFFF; border-color: #2563EB; }}
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
                    <h1>🚀 Narendra Yenagandula - AI/ML Job Search & Application Tracker</h1>
                    <p>B.Tech CSE (AI & ML) | Target: AI/ML Engineer, Machine Learning, Python Developer</p>
                </div>
                <div>
                    <a href="/download-excel" class="btn btn-excel">📥 Download Excel Sheet</a>
                </div>
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
                    <div class="stat-label">Total Applied</div>
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
                <div class="filters">
                    <strong style="font-size:14px;color:#334155;">Filter Applications:</strong>
                    <a href="/" class="filter-btn {'active' if not filter_status else ''}">All Jobs ({stats['total_jobs_tracked']})</a>
                    <a href="/?filter_status=Applied (Auto >=70%)" class="filter-btn {'active' if filter_status == 'Applied (Auto >=70%)' else ''}">Auto Applied</a>
                    <a href="/?filter_status=Sent for Review (<70%)" class="filter-btn {'active' if 'Review' in filter_status else ''}">Sent for Review</a>
                    <a href="/?filter_status=Interview Scheduled" class="filter-btn {'active' if 'Interview' in filter_status else ''}">Interviews</a>
                    <a href="/?filter_status=Rejected" class="filter-btn {'active' if filter_status == 'Rejected' else ''}">Rejected ({stats['rejected_count']})</a>
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
                                <th style="width:10%;">Notes / Feedback</th>
                                <th style="width:10%;text-align:center;">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html if rows_html else '<tr><td colspan="7" style="text-align:center;padding:32px;color:#94A3B8;">No job applications found matching filter. Run a scan from the CLI or dashboard.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


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
