"""
LinkedIn Job Scraper using LinkedIn Guest Public API.
Fetches real-time job listings and descriptions without requiring credentials or risking account bans.
"""

import time
import random
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup


class LinkedInJobScraper:
    def __init__(self, cache_file: str = "data/jobs_cache.json"):
        self.cache_path = Path(cache_file)
        self.cache: Dict[str, Any] = self._load_cache()
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def _load_cache(self) -> Dict[str, Any]:
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, indent=2)

    def extract_job_id_from_url(self, url: str) -> Optional[str]:
        match = re.search(r'(\d{8,12})', url)
        return match.group(1) if match else None

    def search_jobs(
        self,
        keywords: str = "AI ML Engineer",
        location: str = "Hyderabad",
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """Searches for jobs matching keywords and location."""
        jobs = []
        start = 0
        batch_size = 10

        while len(jobs) < limit:
            search_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            search_params = {
                "keywords": keywords,
                "location": location,
                "start": start
            }

            try:
                time.sleep(random.uniform(0.8, 1.6))
                with httpx.Client(timeout=15.0, headers=self.headers, follow_redirects=True) as client:
                    response = client.get(search_url, params=search_params)

                if response.status_code != 200:
                    break

                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.find_all("li")
                if not cards:
                    break

                found_in_batch = 0
                for card in cards:
                    title_elem = card.find("h3", class_="base-search-card__title")
                    company_elem = card.find("h4", class_="base-search-card__subtitle")
                    location_elem = card.find("span", class_="job-search-card__location")
                    link_elem = card.find("a", class_="base-card__full-link")
                    date_elem = card.find("time")

                    if not title_elem or not link_elem:
                        continue

                    raw_url = link_elem.get("href", "")
                    clean_url = raw_url.split("?")[0] if raw_url else ""
                    job_id = self.extract_job_id_from_url(clean_url)

                    if not job_id:
                        continue

                    job_item = {
                        "job_id": job_id,
                        "title": title_elem.text.strip(),
                        "company": company_elem.text.strip() if company_elem else "Unknown Company",
                        "location": location_elem.text.strip() if location_elem else location,
                        "job_url": clean_url,
                        "posted_date": date_elem.text.strip() if date_elem else "Recent",
                    }
                    jobs.append(job_item)
                    found_in_batch += 1
                    if len(jobs) >= limit:
                        break

                if found_in_batch == 0:
                    break

                start += batch_size

            except Exception as e:
                print(f"[Scraper] Error fetching batch at start={start}: {e}")
                break

        return jobs

    def fetch_job_details(self, job_id: str) -> Dict[str, Any]:
        """Fetches detailed description for a job posting."""
        if job_id in self.cache and self.cache[job_id].get("description"):
            return self.cache[job_id]

        url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
        details = {
            "description": "",
            "seniority_level": "Entry level",
            "employment_type": "Full-time",
            "job_function": "Engineering / IT"
        }

        try:
            time.sleep(random.uniform(0.7, 1.4))
            with httpx.Client(timeout=15.0, headers=self.headers, follow_redirects=True) as client:
                response = client.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                desc_elem = soup.find("div", class_="show-more-less-html__markup")
                if desc_elem:
                    # Clean up text
                    details["description"] = desc_elem.get_text(separator="\n").strip()

                # Extract criteria
                criteria_items = soup.find_all("li", class_="description__job-criteria-item")
                for item in criteria_items:
                    header = item.find("h3")
                    val = item.find("span")
                    if header and val:
                        h_text = header.text.strip().lower()
                        v_text = val.text.strip()
                        if "seniority" in h_text:
                            details["seniority_level"] = v_text
                        elif "employment" in h_text:
                            details["employment_type"] = v_text
                        elif "function" in h_text:
                            details["job_function"] = v_text
            else:
                details["description"] = "Job details could not be retrieved from guest endpoint."

        except Exception as e:
            print(f"[Scraper] Error fetching job details for {job_id}: {e}")
            details["description"] = "Error retrieving description."

        # Cache result
        self.cache[job_id] = details
        self._save_cache()
        return details
