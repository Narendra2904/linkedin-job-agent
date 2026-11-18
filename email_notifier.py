"""
Email Notifier for Narendra Yenagandula's Job Agent.
Dispatches modern HTML email alerts via SMTP (e.g. Gmail) for:
- High Match Jobs (>= 70%)
- Review Jobs (< 70%)
- Daily Execution Digest
Falls back gracefully to local HTML preview file generation if SMTP credentials are unconfigured.
"""

import os
import sys
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

load_dotenv()

PREVIEW_DIR = Path("data/email_previews")


class EmailNotifier:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "yenagandula.narendra@gmail.com")
        raw_pwd = os.getenv("SMTP_PASSWORD", "")
        # Remove any internal spaces commonly present in 16-character Google App Passwords
        self.smtp_password = raw_pwd.replace(" ", "").strip()
        self.recipient = os.getenv("RECIPIENT_EMAIL", "yenagandula.narendra@gmail.com")
        self.sender_name = os.getenv("SENDER_NAME", "Narendra's AI Job Agent")
        PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    def is_configured(self) -> bool:
        """Returns True if SMTP password is set."""
        return bool(self.smtp_password and len(self.smtp_password) > 4)

    def _save_preview(self, subject: str, html_content: str) -> Path:
        """Saves HTML preview for local review."""
        safe_subject = "".join(c if c.isalnum() else "_" for c in subject[:30])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{safe_subject}.html"
        filepath = PREVIEW_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        return filepath

    def send_email(self, subject: str, html_body: str) -> bool:
        """Sends email via SMTP or writes to local preview if unconfigured."""
        if not self.is_configured():
            preview_path = self._save_preview(subject, html_body)
            print(f"[EmailNotifier (Preview Mode)] SMTP not configured with password. Saved HTML email to: {preview_path}")
            return False

        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = f"{self.sender_name} <{self.smtp_user}>"
            msg["To"] = self.recipient
            msg.set_content("Please enable HTML viewing to see the detailed job match report.")
            msg.add_alternative(html_body, subtype="html")

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            print(f"[EmailNotifier] Successfully sent email to {self.recipient}: '{subject}'")
            return True
        except Exception as e:
            print(f"[EmailNotifier] Failed to send email: {e}")
            preview_path = self._save_preview(subject, html_body)
            print(f"[EmailNotifier] Saved fallback preview to: {preview_path}")
            return False

    def notify_job(self, job_data: Dict[str, Any], match_result: Dict[str, Any]) -> bool:
        """Sends targeted email based on match percentage."""
        score = match_result.get("score", 0.0)
        title = job_data.get("title", "Job Posting")
        company = job_data.get("company", "Unknown")
        location = job_data.get("location", "Hyderabad")
        job_url = job_data.get("job_url", "https://www.linkedin.com/jobs/")
        matched_skills = match_result.get("matched_skills", [])
        missing_skills = match_result.get("missing_skills", [])

        if score >= 70.0:
            subject = f"🎯 HIGH MATCH ({score:.1f}%): {title} at {company}"
            badge_color = "#059669"
            header_title = "🎯 High Match Job Discovered (>70%)"
            action_desc = "This role strongly matches your AI/ML profile and was auto-queued for application!"
        else:
            subject = f"📋 Job for Review ({score:.1f}%): {title} at {company}"
            badge_color = "#D97706"
            header_title = "📋 Job Recommendation for Review (<70%)"
            action_desc = "This role partially matches your profile. Check the missing skills below to decide if you want to apply."

        matched_badges = "".join([f'<span style="display:inline-block;background:#D1FAE5;color:#065F46;padding:4px 8px;border-radius:12px;margin:2px 4px;font-size:12px;">✓ {s}</span>' for s in matched_skills]) or "<em>None identified</em>"
        missing_badges = "".join([f'<span style="display:inline-block;background:#FEE2E2;color:#991B1B;padding:4px 8px;border-radius:12px;margin:2px 4px;font-size:12px;">+ {s}</span>' for s in missing_skills]) or "<em>None</em>"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #F3F4F6; margin: 0; padding: 20px; color: #1F2937; }}
            .container {{ max-width: 650px; margin: 0 auto; background: #FFFFFF; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #E5E7EB; }}
            .header {{ background-color: #1E3A8A; color: #FFFFFF; padding: 24px; text-align: center; }}
            .content {{ padding: 24px; }}
            .score-card {{ text-align: center; margin: 20px 0; padding: 16px; background-color: #F8FAFC; border-radius: 6px; border: 1px solid #E2E8F0; }}
            .score-val {{ font-size: 32px; font-weight: bold; color: {badge_color}; }}
            .btn {{ display: inline-block; background-color: #2563EB; color: #FFFFFF; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 16px; }}
            .section-title {{ font-size: 14px; font-weight: bold; color: #4B5563; text-transform: uppercase; margin-top: 16px; margin-bottom: 8px; }}
            .footer {{ background-color: #F9FAFB; padding: 16px; text-align: center; font-size: 12px; color: #6B7280; border-top: 1px solid #E5E7EB; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h2 style="margin:0;">{header_title}</h2>
              <p style="margin:6px 0 0 0; font-size:14px; opacity:0.9;">AI Job Agent for Narendra Yenagandula</p>
            </div>
            <div class="content">
              <h3 style="margin-top:0; color:#111827;">{title}</h3>
              <p style="color:#4B5563; margin-top:-8px;"><strong>Company:</strong> {company} | <strong>Location:</strong> {location}</p>

              <div class="score-card">
                <div>Candidate Profile Match Score:</div>
                <div class="score-val">{score:.1f}%</div>
                <div style="font-size:13px; color:#4B5563; margin-top:4px;">{action_desc}</div>
              </div>

              <div class="section-title">Matched Technical Skills ({len(matched_skills)})</div>
              <div>{matched_badges}</div>

              <div class="section-title">Additional / Missing Technologies ({len(missing_skills)})</div>
              <div>{missing_badges}</div>

              <div style="text-align: center; margin-top: 28px;">
                <a href="{job_url}" target="_blank" class="btn">View & Apply on LinkedIn &rarr;</a>
              </div>
            </div>
            <div class="footer">
              This job has been recorded into your <strong>job_applications_tracker.xlsx</strong> spreadsheet.<br/>
              To change application status or log interview feedback, run <code>python tracker.py</code> or visit your local dashboard.
            </div>
          </div>
        </body>
        </html>
        """
        return self.send_email(subject, html)
