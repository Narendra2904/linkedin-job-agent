"""
Automated Application Engine for Narendra Yenagandula.
Handles application dispatch, customized cover note generation, and Playwright Easy Apply flow.
"""

import os
import sys
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional
from profile_data import CANDIDATE_PROFILE

RESUME_PATH = Path("AIML.pdf").resolve()


class AutoApplier:
    def __init__(self, resume_path: Path = RESUME_PATH):
        self.resume_path = resume_path
        self.candidate = CANDIDATE_PROFILE

    def generate_pitch_message(self, job_title: str, company: str, matched_skills: list) -> str:
        """Generates tailored recruiter pitch / application message."""
        skills_str = ", ".join(matched_skills[:4]) if matched_skills else "Python, Machine Learning, and FastAPI"
        return (
            f"Dear Hiring Team at {company},\n\n"
            f"I am writing to express my strong enthusiasm for the {job_title} position. "
            f"As a Computer Science (AI & ML) graduate from Vaageswari College of Engineering with hands-on "
            f"experience building Machine Learning models (SVM, classification) and AI-integrated backend systems "
            f"using {skills_str}, I am confident in my ability to contribute effectively from day one.\n\n"
            f"I have attached my resume ({self.resume_path.name}) highlighting my practical projects, including an "
            f"image-based Disease Detection System and an AI-driven results portal with FastAPI.\n\n"
            f"I would welcome the opportunity to discuss how my technical skills align with {company}'s goals.\n\n"
            f"Best regards,\n"
            f"Narendra Yenagandula\n"
            f"Hyderabad, India | +91 9989114207\n"
            f"LinkedIn: {self.candidate['linkedin_url']}\n"
            f"GitHub: {self.candidate['github_url']}"
        )

    def apply_job(self, job_data: Dict[str, Any], match_result: Dict[str, Any], open_browser: bool = False) -> Dict[str, Any]:
        """
        Dispatches application workflow:
        1. Generates customized pitch message.
        2. Prepares resume file attachment.
        3. Marks status and optionally opens job posting in browser.
        """
        job_id = job_data.get("job_id", "")
        title = job_data.get("title", "")
        company = job_data.get("company", "")
        url = job_data.get("job_url", "")
        matched_skills = match_result.get("matched_skills", [])

        pitch = self.generate_pitch_message(title, company, matched_skills)

        result = {
            "job_id": job_id,
            "status": "Applied (Auto >=70%)",
            "resume_used": str(self.resume_path),
            "cover_pitch": pitch,
            "job_url": url,
            "message": f"Successfully processed application for {title} at {company}."
        }

        if open_browser and url:
            try:
                webbrowser.open(url)
            except Exception as e:
                print(f"[AutoApplier] Could not open browser: {e}")

        return result

    async def run_playwright_easy_apply(self, job_url: str, headless: bool = False) -> bool:
        """
        Optional browser automation for LinkedIn Easy Apply.
        Requires active LinkedIn login session.
        """
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=headless)
                context = await browser.new_context()
                page = await context.new_page()
                await page.goto(job_url)
                print(f"[Playwright] Navigated to {job_url}")
                # Wait for Easy Apply button
                easy_apply_btn = await page.query_selector("button.jobs-apply-button")
                if easy_apply_btn:
                    print("[Playwright] Found Easy Apply button. Clicking...")
                    await easy_apply_btn.click()
                    # User or automated modal steps can continue here
                else:
                    print("[Playwright] Job requires external apply or login.")
                await browser.close()
                return True
        except Exception as e:
            print(f"[Playwright] Automation notice: {e}")
            return False
