"""
Main Entrypoint for Narendra Yenagandula's AI Job Application Agent & Tracker.

Usage:
  python main.py --scan                        # Run job fetch, match, apply/email, tracker update
  python main.py --scan --limit 15             # Fetch and analyze 15 jobs
  python main.py --dashboard                   # Launch interactive web UI on http://localhost:8000
  python main.py --stats                       # View overall tracker metrics
  python main.py --update <id> --status "..."  # Update an application status
  python main.py --open-excel                  # Open Excel tracker spreadsheet
"""

import argparse
import sys
import os
from pathlib import Path

# Fix Windows console UTF-8 encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from profile_data import CANDIDATE_PROFILE
from job_scraper import LinkedInJobScraper
from unified_scraper import UnifiedJobScraper
from matcher import JobMatcher
from tracker import JobTracker, EXCEL_PATH
from email_notifier import EmailNotifier
from auto_applier import AutoApplier


def run_job_agent(keywords: str = "AI ML Engineer", location: str = "Hyderabad", limit: int = 5, threshold: float = 70.0, dry_run: bool = False, track: str = "all"):
    print("=" * 70)
    print("🤖 STARTING NARENDRA'S MULTI-PLATFORM FRESHER JOB AGENT")
    print(f"Role Track: {track.upper()} | Target Location: {location} | Match Threshold: {threshold}%")
    print("Platforms : LinkedIn, Arbeitnow, RemoteOK (with direct Naukri portal links)")
    print("=" * 70)

    scraper = UnifiedJobScraper()
    matcher = JobMatcher()
    tracker = JobTracker()
    notifier = EmailNotifier()
    applier = AutoApplier()

    print(f"\n[1/4] 🔍 Searching across platforms for '{track.upper()}' fresher roles in '{location}'...")
    raw_jobs = scraper.search_all_platforms(track=track, location=location, limit_per_source=limit)
    print(f"      Retrieved {len(raw_jobs)} unique jobs across platforms.")

    if not raw_jobs:
        print("[!] No jobs found. Check internet connection or broaden search keywords.")
        return

    processed_count = 0
    auto_applied_count = 0
    review_email_count = 0

    print("\n[2/4] 🧠 Analyzing Job Requirements against Fresher Profile & Track...")
    for idx, job in enumerate(raw_jobs, 1):
        job_id = job["job_id"]
        title = job["title"]
        company = job["company"]
        source = job.get("source", "Web")
        description = job.get("description", "")

        print(f"\n[{idx}/{len(raw_jobs)}] [{source}] Job #{job_id}: '{title}' at '{company}'")

        # Compute Track-Aware Match
        match_result = matcher.evaluate_match(title, description)
        score = match_result["score"]
        recommendation = match_result["recommendation"]
        matched_skills = match_result["matched_skills"]
        missing_skills = match_result["missing_skills"]
        is_fresher = match_result["is_fresher_friendly"]
        detected_track = match_result["track"]

        print(f"      Track: {detected_track} | Fresher Friendly: {is_fresher}")
        print(f"      Match Score: {score:.1f}% -> {recommendation}")
        print(f"      Matched Skills: {', '.join(matched_skills[:5]) if matched_skills else 'None'}")
        if missing_skills:
            print(f"      Missing Skills: {', '.join(missing_skills[:4])}")

        # Deduplication check: Ensure an email is never sent twice for the same job
        already_notified = tracker.is_already_notified(job_id)
        email_sent = 1 if already_notified else 0

        # Routing logic:
        if score >= threshold:
            print("      🎯 HIGH MATCH (>= 70%)! Auto-applying and preparing application...")
            app_result = applier.apply_job(job, match_result, open_browser=False)
            status = f"Applied ({source} >=70%)"
            auto_applied_count += 1

            if already_notified:
                print(f"      ℹ️ [Deduplication] Alert email was already sent previously for Job #{job_id}. Skipping resend.")
            elif not dry_run:
                sent = notifier.notify_job(job, match_result)
                if sent:
                    email_sent = 1
        else:
            print("      📋 Moderate/Low Match (< 70%). Queuing review email...")
            status = f"Review ({source} <70%)"
            review_email_count += 1

            if already_notified:
                print(f"      ℹ️ [Deduplication] Review email was already sent previously for Job #{job_id}. Skipping resend.")
            elif not dry_run and score >= 45.0:  # Avoid spamming for completely irrelevant roles
                sent = notifier.notify_job(job, match_result)
                if sent:
                    email_sent = 1

        # Record in Tracker
        tracker_entry = {
            "job_id": job_id,
            "title": f"[{source}] {title}",
            "company": company,
            "location": job.get("location", location),
            "job_url": job["job_url"],
            "match_score": score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "status": status,
            "email_sent": email_sent,
            "notes": f"Track: {detected_track} | Fresher: {is_fresher}"
        }
        tracker.upsert_job(tracker_entry)
        processed_count += 1

    print("\n[3/4] 📊 Updating SQLite Database & Excel Tracker...")
    tracker.sync_to_excel()
    print(f"      Excel updated: {EXCEL_PATH.resolve()}")

    print("\n[4/4] 🏁 EXECUTION SUMMARY:")
    stats = tracker.get_statistics()
    print(f"      - Jobs Processed This Run : {processed_count}")
    print(f"      - High Matches (>= 70%)   : {auto_applied_count}")
    print(f"      - Review Alerts (< 70%)   : {review_email_count}")
    print(f"      - Total In Tracker DB     : {stats['total_jobs_tracked']}")
    print(f"      - Applications Submitted  : {stats['total_applied']}")
    print(f"      - Rejections Monitored    : {stats['rejected_count']}")
    print(f"      - Interviews Scheduled    : {stats['interviews_scheduled']}")
    print("=" * 70)


def show_stats():
    tracker = JobTracker()
    stats = tracker.get_statistics()
    print("\n" + "=" * 50)
    print("📊 JOB APPLICATION TRACKER SUMMARY")
    print("=" * 50)
    for k, v in stats.items():
        print(f" {k.replace('_', ' ').title():<28}: {v}")
    print("=" * 50)
    print(f" Excel File: {EXCEL_PATH.resolve()}\n")


def update_status(job_id: str, status: str, notes: str = "", reason: str = ""):
    tracker = JobTracker()
    success = tracker.update_status(job_id, status, notes=notes, rejection_reason=reason)
    if success:
        print(f"✅ Successfully updated Job #{job_id} to status: '{status}'")
    else:
        print(f"❌ Job #{job_id} not found in tracker database.")


def get_network_ip() -> str:
    """Helper to detect the local LAN IP for network access."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def launch_dashboard(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    lan_ip = get_network_ip()
    print("=" * 65)
    print("🚀 NARENDRA'S AI JOB TRACKER BACKEND IS NOW LIVE ON NETWORK")
    print(f"   🏠 Local Machine : http://localhost:{port}")
    print(f"   🌐 On Your Wi-Fi : http://{lan_ip}:{port}")
    print("   📱 Any phone or laptop on your network can access it now!")
    print("=" * 65)
    print("Press Ctrl+C to stop.")
    uvicorn.run("dashboard:app", host=host, port=port, reload=False)


def open_excel():
    if EXCEL_PATH.exists():
        os.startfile(str(EXCEL_PATH.resolve()))
        print(f"Opened {EXCEL_PATH}")
    else:
        print("Excel file not created yet. Run 'python main.py --scan' first.")


def main():
    parser = argparse.ArgumentParser(description="AI Job Application Agent & Tracker for Narendra Yenagandula")
    port_default = int(os.environ.get("PORT", 8000))
    parser.add_argument("--scan", action="store_true", help="Run job search, matching, apply/email workflow")
    parser.add_argument("--track", type=str, default="all", choices=["all", "frontend", "backend", "aiml"], help="Role track: all, frontend, backend, aiml")
    parser.add_argument("--keyword", type=str, default="Fresher Python Developer", help="Job keyword to search")
    parser.add_argument("--location", type=str, default="Hyderabad", help="Job location")
    parser.add_argument("--limit", type=int, default=5, help="Number of jobs to scan per platform")
    parser.add_argument("--threshold", type=float, default=70.0, help="Match percentage threshold for auto-apply")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without dispatching live emails")
    parser.add_argument("--stats", action="store_true", help="Display application tracker statistics")
    parser.add_argument("--update", type=str, help="Job ID to update")
    parser.add_argument("--status", type=str, help="New status (e.g. 'Rejected', 'Interview Scheduled')")
    parser.add_argument("--reason", type=str, default="", help="Rejection reason or interview notes")
    parser.add_argument("--notes", type=str, default="", help="Additional notes")
    parser.add_argument("--dashboard", action="store_true", help="Launch FastAPI web UI dashboard")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface to bind (default 0.0.0.0 for network)")
    parser.add_argument("--port", type=int, default=port_default, help="Port to run web dashboard (default 8000 or $PORT)")
    parser.add_argument("--open-excel", action="store_true", help="Open Excel tracker sheet directly")

    args = parser.parse_args()

    if args.dashboard:
        launch_dashboard(host=args.host, port=args.port)
    elif args.stats:
        show_stats()
    elif args.update:
        if not args.status:
            print("Error: --status is required when updating a job.")
            sys.exit(1)
        update_status(args.update, args.status, notes=args.notes, reason=args.reason)
    elif args.open_excel:
        open_excel()
    elif args.scan:
        run_job_agent(
            keywords=args.keyword,
            location=args.location,
            limit=args.limit,
            threshold=args.threshold,
            dry_run=args.dry_run,
            track=args.track
        )
    else:
        # Default behavior if run without args: show interactive help
        print("\n🤖 Welcome to Narendra's AI Job Application Agent & Tracker!")
        print("Choose an option:")
        print(" 1) python main.py --scan           (Run automated job search & matching)")
        print(" 2) python main.py --dashboard      (Launch local interactive web portal)")
        print(" 3) python main.py --stats          (Check application numbers & rejections)")
        print(" 4) python main.py --open-excel     (Open Excel tracker)")
        print("\nRunning a quick test scan now...\n")
        run_job_agent(keywords="Machine Learning Engineer", location="Hyderabad", limit=5)


if __name__ == "__main__":
    main()
