"""
Multi-Platform Job Aggregator for Narendra Yenagandula.
Fetches jobs across LinkedIn, Arbeitnow, and RemoteOK job platforms
for Fresher Frontend, Backend, and AI/ML tracks.
"""

import time
import random
import re
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
from job_scraper import LinkedInJobScraper


class UnifiedJobScraper:
    def __init__(self):
        self.linkedin_scraper = LinkedInJobScraper()
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        }

    def fetch_linkedin_jobs(self, keywords: str, location: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetches from LinkedIn guest endpoint."""
        raw_jobs = self.linkedin_scraper.search_jobs(keywords=keywords, location=location, limit=limit)
        jobs = []
        for j in raw_jobs:
            details = self.linkedin_scraper.fetch_job_details(j["job_id"])
            jobs.append({
                "job_id": f"LI_{j['job_id']}",
                "raw_id": j["job_id"],
                "source": "LinkedIn",
                "title": j["title"],
                "company": j["company"],
                "location": j["location"],
                "job_url": j["job_url"],
                "description": details.get("description", ""),
                "posted_date": j.get("posted_date", "Recent")
            })
        return jobs

    def fetch_arbeitnow_jobs(self, keywords: str = "python", limit: int = 10) -> List[Dict[str, Any]]:
        """Fetches developer and fresher roles from Arbeitnow open API."""
        jobs = []
        url = "https://www.arbeitnow.com/api/job-board-api"
        kw_low = keywords.lower()

        try:
            with httpx.Client(timeout=15.0, headers=self.headers) as client:
                resp = client.get(url)
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                for item in data:
                    title = item.get("title", "")
                    desc_html = item.get("description", "")
                    clean_desc = BeautifulSoup(desc_html, "html.parser").get_text(separator="\n")
                    combined = f"{title} {clean_desc}".lower()

                    # Match keyword filter
                    terms = kw_low.split()
                    if any(t in combined for t in terms) or "fresher" in combined or "junior" in combined:
                        job_slug = item.get("slug", str(random.randint(100000, 999999)))
                        jobs.append({
                            "job_id": f"AN_{job_slug[:12]}",
                            "raw_id": job_slug,
                            "source": "Arbeitnow",
                            "title": title,
                            "company": item.get("company_name", "Tech Company"),
                            "location": item.get("location", "Remote"),
                            "job_url": item.get("url", ""),
                            "description": clean_desc[:2500],
                            "posted_date": "Recent"
                        })
                        if len(jobs) >= limit:
                            break
        except Exception as e:
            print(f"[UnifiedScraper] Error fetching from Arbeitnow: {e}")
        return jobs

    def fetch_remoteok_jobs(self, keywords: str = "python", limit: int = 8) -> List[Dict[str, Any]]:
        """Fetches remote developer jobs from RemoteOK public API."""
        jobs = []
        url = "https://remoteok.com/api"
        kw_low = keywords.lower()

        try:
            with httpx.Client(timeout=15.0, headers=self.headers) as client:
                resp = client.get(url)
            if resp.status_code == 200:
                raw_items = resp.json()
                # Skip first item if it's metadata
                items = [x for x in raw_items if isinstance(x, dict) and x.get("id")]
                for item in items:
                    title = item.get("position", "")
                    desc_html = item.get("description", "")
                    clean_desc = BeautifulSoup(desc_html, "html.parser").get_text(separator="\n")
                    tags = " ".join(item.get("tags", [])).lower()
                    combined = f"{title} {tags} {clean_desc}".lower()

                    terms = kw_low.split()
                    if any(t in combined for t in terms):
                        job_id = str(item.get("id"))
                        jobs.append({
                            "job_id": f"ROK_{job_id}",
                            "raw_id": job_id,
                            "source": "RemoteOK",
                            "title": title,
                            "company": item.get("company", "Tech Company"),
                            "location": item.get("location", "Remote"),
                            "job_url": item.get("url", "https://remoteok.com"),
                            "description": clean_desc[:2500],
                            "posted_date": "Recent"
                        })
                        if len(jobs) >= limit:
                            break
        except Exception as e:
            print(f"[UnifiedScraper] Error fetching from RemoteOK: {e}")
        return jobs

    def search_all_platforms(
        self,
        track: str = "all",
        location: str = "Hyderabad",
        limit_per_source: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Queries multiple sources (LinkedIn, Arbeitnow, RemoteOK)
        across specified tracks (frontend, backend, aiml, all).
        """
        all_jobs = []

        # Determine search keywords based on track
        track_queries = {
            "frontend": ["Fresher Frontend Developer", "Junior Web Developer HTML CSS JavaScript"],
            "backend": ["Fresher Python Developer", "Junior Backend Developer FastAPI"],
            "aiml": ["AI ML Engineer", "Machine Learning Intern"],
            "all": [
                "Fresher Python Developer",
                "Fresher Frontend Developer",
                "AI ML Engineer"
            ]
        }

        queries = track_queries.get(track.lower(), track_queries["all"])

        # 1. Fetch from LinkedIn
        for q in queries:
            try:
                print(f"[Scraper] Querying LinkedIn for '{q}' in '{location}'...")
                li_jobs = self.fetch_linkedin_jobs(keywords=q, location=location, limit=limit_per_source)
                all_jobs.extend(li_jobs)
            except Exception as e:
                print(f"[Scraper] LinkedIn query '{q}' notice: {e}")

        # 2. Fetch from Arbeitnow (for remote / developer roles)
        try:
            print("[Scraper] Querying Arbeitnow job board...")
            an_jobs = self.fetch_arbeitnow_jobs(keywords="developer python javascript", limit=limit_per_source)
            all_jobs.extend(an_jobs)
        except Exception as e:
            print(f"[Scraper] Arbeitnow query notice: {e}")

        # 3. Fetch from RemoteOK
        try:
            print("[Scraper] Querying RemoteOK job board...")
            rok_jobs = self.fetch_remoteok_jobs(keywords="python javascript", limit=limit_per_source)
            all_jobs.extend(rok_jobs)
        except Exception as e:
            print(f"[Scraper] RemoteOK query notice: {e}")

        # Deduplicate by job_id
        seen_ids = set()
        unique_jobs = []
        for j in all_jobs:
            jid = j.get("job_id")
            if jid and jid not in seen_ids:
                seen_ids.add(jid)
                unique_jobs.append(j)

        return unique_jobs
