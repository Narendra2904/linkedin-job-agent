"""
Application Tracker for Narendra Yenagandula.
Stores job applications in SQLite and maintains a professional, beautifully styled Excel tracker sheet.
Tracks applied, under review, interviews, rejected, and offers with full history and notes.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


DB_PATH = Path("data/job_tracker.db")
EXCEL_PATH = Path("data/job_applications_tracker.xlsx")
CSV_PATH = Path("data/job_applications_tracker.csv")


class JobTracker:
    def __init__(self, db_path: Path = DB_PATH, excel_path: Path = EXCEL_PATH):
        self.db_path = db_path
        self.excel_path = excel_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_applications (
                    job_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    job_url TEXT,
                    match_score REAL,
                    matched_skills TEXT,
                    missing_skills TEXT,
                    status TEXT NOT NULL,
                    discovery_date TEXT,
                    applied_date TEXT,
                    last_updated TEXT,
                    rejection_reason TEXT,
                    notes TEXT,
                    email_sent INTEGER DEFAULT 0,
                    email_sent_at TEXT
                )
            """)
            # Ensure new columns exist for existing databases
            try:
                cursor.execute("ALTER TABLE job_applications ADD COLUMN email_sent INTEGER DEFAULT 0")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE job_applications ADD COLUMN email_sent_at TEXT")
            except Exception:
                pass
            conn.commit()

    def is_already_notified(self, job_id: str) -> bool:
        """Checks if an email notification was already dispatched for this job."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT email_sent FROM job_applications WHERE job_id = ?", (str(job_id),))
            row = cursor.fetchone()
            if row and row[0] and int(row[0]) == 1:
                return True
        return False

    def mark_notified(self, job_id: str):
        """Marks a job as notified with current timestamp so it is never resent."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE job_applications
                SET email_sent = 1, email_sent_at = ?
                WHERE job_id = ?
            """, (now, str(job_id)))
            conn.commit()

    def upsert_job(self, job_dict: Dict[str, Any]) -> str:
        """Inserts or updates a job in the tracker."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        job_id = str(job_dict.get("job_id", "")).strip()
        if not job_id:
            return ""

        status = job_dict.get("status")
        if not status:
            score = float(job_dict.get("match_score", 0.0))
            status = "Applied (Auto >=70%)" if score >= 70.0 else "Sent for Review (<70%)"

        matched_skills = ", ".join(job_dict.get("matched_skills", [])) if isinstance(job_dict.get("matched_skills"), list) else str(job_dict.get("matched_skills", ""))
        missing_skills = ", ".join(job_dict.get("missing_skills", [])) if isinstance(job_dict.get("missing_skills"), list) else str(job_dict.get("missing_skills", ""))

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, discovery_date, applied_date, email_sent, email_sent_at FROM job_applications WHERE job_id = ?", (job_id,))
            existing = cursor.fetchone()

            email_sent_val = 1 if job_dict.get("email_sent") else 0
            email_sent_time = job_dict.get("email_sent_at", "")

            if existing:
                # Keep user-modified status if it was already marked as Interview, Rejected, etc.
                existing_status = existing[0]
                discovery_date = existing[1]
                applied_date = existing[2] or (now if "Applied" in status else "")
                
                # Preserve email_sent status if already sent
                if existing[3] and int(existing[3]) == 1:
                    email_sent_val = 1
                    email_sent_time = existing[4] or email_sent_time

                # If existing is already progressed or rejected, don't overwrite status
                if existing_status in ["Interview Scheduled", "Technical Round", "Rejected", "Offer Received", "Applied (Manual)"]:
                    final_status = existing_status
                else:
                    final_status = status

                cursor.execute("""
                    UPDATE job_applications
                    SET title = ?, company = ?, location = ?, job_url = ?, match_score = ?,
                        matched_skills = ?, missing_skills = ?, status = ?, applied_date = ?, last_updated = ?,
                        email_sent = ?, email_sent_at = ?
                    WHERE job_id = ?
                """, (
                    job_dict.get("title", ""),
                    job_dict.get("company", ""),
                    job_dict.get("location", ""),
                    job_dict.get("job_url", ""),
                    float(job_dict.get("match_score", 0.0)),
                    matched_skills,
                    missing_skills,
                    final_status,
                    applied_date,
                    now,
                    email_sent_val,
                    email_sent_time,
                    job_id
                ))
            else:
                applied_date = now if "Applied" in status else ""
                cursor.execute("""
                    INSERT INTO job_applications (
                        job_id, title, company, location, job_url, match_score,
                        matched_skills, missing_skills, status, discovery_date,
                        applied_date, last_updated, rejection_reason, notes,
                        email_sent, email_sent_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job_id,
                    job_dict.get("title", ""),
                    job_dict.get("company", ""),
                    job_dict.get("location", ""),
                    job_dict.get("job_url", ""),
                    float(job_dict.get("match_score", 0.0)),
                    matched_skills,
                    missing_skills,
                    status,
                    now,
                    applied_date,
                    now,
                    job_dict.get("rejection_reason", ""),
                    job_dict.get("notes", ""),
                    email_sent_val,
                    email_sent_time
                ))
            conn.commit()
            conn.commit()

        # Update Excel sheet automatically
        self.sync_to_excel()
        return job_id

    def update_status(self, job_id: str, new_status: str, notes: Optional[str] = None, rejection_reason: Optional[str] = None) -> bool:
        """Updates status, rejection notes, or feedback for a specific job."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT job_id, notes, rejection_reason FROM job_applications WHERE job_id = ?", (job_id,))
            row = cursor.fetchone()
            if not row:
                return False

            updated_notes = (row[1] or "") + (f"\n[{now}] {notes}" if notes else "")
            updated_rejection = rejection_reason if rejection_reason is not None else row[2]

            cursor.execute("""
                UPDATE job_applications
                SET status = ?, last_updated = ?, notes = ?, rejection_reason = ?
                WHERE job_id = ?
            """, (new_status, now, updated_notes.strip(), updated_rejection, job_id))
            conn.commit()

        self.sync_to_excel()
        return True

    def get_all_jobs(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if status_filter:
                cursor.execute("SELECT * FROM job_applications WHERE status = ? ORDER BY match_score DESC", (status_filter,))
            else:
                cursor.execute("SELECT * FROM job_applications ORDER BY match_score DESC, discovery_date DESC")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_statistics(self) -> Dict[str, Any]:
        """Calculates breakdown and metrics for the dashboard and reports."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM job_applications")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM job_applications WHERE match_score >= 70.0")
            high_matches = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM job_applications WHERE status LIKE 'Applied%'")
            applied = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM job_applications WHERE status LIKE 'Sent for Review%'")
            review = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM job_applications WHERE status LIKE '%Interview%' OR status LIKE '%Technical%'")
            interviews = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM job_applications WHERE status = 'Rejected'")
            rejected = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM job_applications WHERE status = 'Offer Received'")
            offers = cursor.fetchone()[0]

        return {
            "total_jobs_tracked": total,
            "high_matches_70_plus": high_matches,
            "total_applied": applied,
            "in_review": review,
            "interviews_scheduled": interviews,
            "rejected_count": rejected,
            "offers_received": offers,
            "interview_rate": f"{(interviews / applied * 100):.1f}%" if applied > 0 else "0.0%"
        }

    def sync_to_excel(self, destination: Optional[Path] = None):
        """Generates a professional, stylized Excel workbook with multiple tabs and conditional coloring."""
        dest = destination or self.excel_path
        jobs = self.get_all_jobs()
        stats = self.get_statistics()

        wb = openpyxl.Workbook()
        
        # ----------------- SHEET 1: Summary Dashboard -----------------
        ws_dash = wb.active
        ws_dash.title = "Summary Dashboard"
        ws_dash.views.sheetView[0].showGridLines = True

        title_font = Font(name="Segoe UI", size=16, bold=True, color="1E3A8A")
        sub_font = Font(name="Segoe UI", size=10, italic=True, color="4B5563")
        kpi_label_font = Font(name="Segoe UI", size=10, bold=True, color="1F2937")
        kpi_val_font = Font(name="Segoe UI", size=18, bold=True, color="1E3A8A")

        ws_dash["B2"] = "🎯 Narendra Yenagandula - AI/ML Job Application Tracker"
        ws_dash["B2"].font = title_font
        ws_dash["B3"] = f"Candidate: Narendra Yenagandula | B.Tech CSE (AI & ML) | Target: AI/ML Engineer | Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ws_dash["B3"].font = sub_font

        # KPI Cards Setup
        kpis = [
            ("Total Jobs Tracked", stats["total_jobs_tracked"], "EFF6FF", "1E40AF"),
            ("High Matches (>=70%)", stats["high_matches_70_plus"], "ECFDF5", "047857"),
            ("Applications Submitted", stats["total_applied"], "F0FDF4", "15803D"),
            ("Interviews Scheduled", stats["interviews_scheduled"], "EFF6FF", "2563EB"),
            ("Applications Rejected", stats["rejected_count"], "FEF2F2", "B91C1C"),
            ("Job Offers", stats["offers_received"], "ECFDF5", "059669"),
        ]

        card_row = 5
        col_start = 2
        for title, val, bg_hex, fg_hex in kpis:
            c_label = ws_dash.cell(row=card_row, column=col_start, value=title)
            c_val = ws_dash.cell(row=card_row + 1, column=col_start, value=val)

            c_label.font = Font(name="Segoe UI", size=9, bold=True, color="4B5563")
            c_label.fill = PatternFill(start_color=bg_hex, end_color=bg_hex, fill_type="solid")
            c_label.alignment = Alignment(horizontal="center", vertical="center")

            c_val.font = Font(name="Segoe UI", size=16, bold=True, color=fg_hex)
            c_val.fill = PatternFill(start_color=bg_hex, end_color=bg_hex, fill_type="solid")
            c_val.alignment = Alignment(horizontal="center", vertical="center")

            thin_border = Border(
                left=Side(style='thin', color='D1D5DB'),
                right=Side(style='thin', color='D1D5DB'),
                top=Side(style='thin', color='D1D5DB'),
                bottom=Side(style='thin', color='D1D5DB')
            )
            c_label.border = thin_border
            c_val.border = thin_border

            ws_dash.column_dimensions[get_column_letter(col_start)].width = 24
            col_start += 1

        # Quick Instructions & Legend
        ws_dash["B8"] = "📌 Tracker Status Workflow & Action Guide"
        ws_dash["B8"].font = Font(name="Segoe UI", size=12, bold=True, color="1E3A8A")

        workflow_rows = [
            ("Status", "Description", "Required Candidate Action"),
            ("Applied (Auto >=70%)", "Job matched >= 70% and application was queued / dispatched.", "Follow up with HR in 5-7 days using LinkedIn template."),
            ("Sent for Review (<70%)", "Job matched 45%-69%. Potential match needing skill brush-up.", "Review job requirements, tailor resume, or apply manually."),
            ("Applied (Manual)", "Candidate applied directly on company careers site.", "Record application date & track interview stages."),
            ("Interview Scheduled", "HR / Technical interviewer reached out for a screening or interview.", "Prepare project stories (Fruit Disease SVM & FastAPI portal)."),
            ("Rejected", "Application rejected or closed without offer.", "Log rejection feedback in Tracker to analyze skill gaps."),
            ("Offer Received", "Official job offer received from company.", "Review compensation and role alignment.")
        ]

        for idx, row_data in enumerate(workflow_rows):
            r = 10 + idx
            for c_idx, val in enumerate(row_data):
                cell = ws_dash.cell(row=r, column=2 + c_idx, value=val)
                if idx == 0:
                    cell.font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
                else:
                    cell.font = Font(name="Segoe UI", size=9)
                    cell.fill = PatternFill(start_color="F9FAFB" if idx % 2 == 0 else "FFFFFF", end_color="F9FAFB" if idx % 2 == 0 else "FFFFFF", fill_type="solid")
                cell.border = Border(
                    left=Side(style='thin', color='E5E7EB'),
                    right=Side(style='thin', color='E5E7EB'),
                    top=Side(style='thin', color='E5E7EB'),
                    bottom=Side(style='thin', color='E5E7EB')
                )

        # ----------------- SHEET 2: Applications Tracker -----------------
        ws_apps = wb.create_sheet(title="Applications Tracker")
        ws_apps.views.sheetView[0].showGridLines = True

        headers = [
            "Job ID", "Job Title", "Company", "Location", "Match %",
            "Matched Skills", "Missing Skills", "Status", "Discovery Date",
            "Applied Date", "Rejection Reason / Notes", "LinkedIn Job URL"
        ]

        header_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        header_border = Border(
            left=Side(style='thin', color='1E40AF'),
            right=Side(style='thin', color='1E40AF'),
            top=Side(style='thin', color='1E40AF'),
            bottom=Side(style='thin', color='1E40AF')
        )

        for col_idx, header in enumerate(headers, 1):
            cell = ws_apps.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.border = header_border
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        ws_apps.row_dimensions[1].height = 28

        # Color mapping for Status column
        STATUS_COLORS = {
            "Applied (Auto >=70%)": {"bg": "D1FAE5", "fg": "065F46"}, # Soft Green
            "Applied (Manual)": {"bg": "D1FAE5", "fg": "065F46"},
            "Sent for Review (<70%)": {"bg": "FEF3C7", "fg": "92400E"}, # Soft Amber
            "Interview Scheduled": {"bg": "DBEAFE", "fg": "1E40AF"},   # Soft Blue
            "Technical Round": {"bg": "E0E7FF", "fg": "3730A3"},       # Indigo
            "Rejected": {"bg": "FEE2E2", "fg": "991B1B"},              # Soft Red
            "Offer Received": {"bg": "A7F3D0", "fg": "047857"},        # Bright Emerald
        }

        cell_border = Border(
            left=Side(style='thin', color='E5E7EB'),
            right=Side(style='thin', color='E5E7EB'),
            top=Side(style='thin', color='E5E7EB'),
            bottom=Side(style='thin', color='E5E7EB')
        )

        for r_idx, job in enumerate(jobs, 2):
            status = job.get("status", "Sent for Review (<70%)")
            score = float(job.get("match_score", 0.0))

            row_values = [
                job.get("job_id", ""),
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                f"{score:.1f}%",
                job.get("matched_skills", ""),
                job.get("missing_skills", ""),
                status,
                job.get("discovery_date", ""),
                job.get("applied_date", ""),
                job.get("rejection_reason", "") or job.get("notes", ""),
                job.get("job_url", "")
            ]

            for c_idx, val in enumerate(row_values, 1):
                cell = ws_apps.cell(row=r_idx, column=c_idx, value=val)
                cell.font = Font(name="Segoe UI", size=9)
                cell.border = cell_border
                cell.alignment = Alignment(vertical="center")

                # Column-specific formatting
                if c_idx == 5:  # Match %
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    if score >= 70.0:
                        cell.font = Font(name="Segoe UI", size=9, bold=True, color="047857")
                    else:
                        cell.font = Font(name="Segoe UI", size=9, color="B45309")

                elif c_idx == 8:  # Status
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    color_style = STATUS_COLORS.get(status, {"bg": "F3F4F6", "fg": "374151"})
                    cell.fill = PatternFill(start_color=color_style["bg"], end_color=color_style["bg"], fill_type="solid")
                    cell.font = Font(name="Segoe UI", size=9, bold=True, color=color_style["fg"])

                elif c_idx == 12 and val:  # Job URL link
                    cell.hyperlink = val
                    cell.font = Font(name="Segoe UI", size=9, color="2563EB", underline="single")

            ws_apps.row_dimensions[r_idx].height = 22

        # Adjust Column Widths
        col_widths = {
            1: 14, 2: 30, 3: 24, 4: 20, 5: 12,
            6: 30, 7: 30, 8: 24, 9: 18, 10: 18,
            11: 35, 12: 45
        }
        for col_idx, width in col_widths.items():
            ws_apps.column_dimensions[get_column_letter(col_idx)].width = width

        # Enable auto-filter on the header row
        ws_apps.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{max(2, len(jobs) + 1)}"

        # Save workbook
        dest.parent.mkdir(parents=True, exist_ok=True)
        wb.save(dest)


if __name__ == "__main__":
    tracker = JobTracker()
    stats = tracker.get_statistics()
    print("Tracker Initialized. Stats:", stats)
