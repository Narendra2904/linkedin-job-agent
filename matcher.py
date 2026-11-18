"""
Job requirement comparator and scoring engine for Narendra Yenagandula.
Specialized for Freshers across AI/ML, Backend, and Frontend engineering tracks.
"""

import re
from typing import Dict, List, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from profile_data import CANDIDATE_PROFILE, get_all_candidate_skills, get_profile_summary_text

# Comprehensive catalog of relevant tech keywords to detect in job descriptions
KNOWN_TECH_KEYWORDS = {
    # Frontend
    "html", "html5", "css", "css3", "javascript", "js", "typescript", "react", "react.js",
    "vue", "angular", "bootstrap", "tailwind", "responsive design", "flexbox", "grid",
    "dom", "ui", "ux", "frontend", "front-end", "web development",
    # Backend
    "python", "fastapi", "flask", "django", "rest api", "api", "apis", "graphql",
    "sql", "mysql", "postgresql", "sqlite", "mongodb", "backend", "back-end",
    "data structures", "algorithms", "oop", "object oriented",
    # AI/ML
    "machine learning", "deep learning", "artificial intelligence", "ai", "ml", "nlp",
    "computer vision", "opencv", "svm", "support vector machine", "random forest",
    "classification", "supervised learning", "unsupervised learning", "model training",
    "model evaluation", "data preprocessing", "feature engineering", "scikit-learn",
    "sklearn", "pandas", "numpy", "matplotlib", "seaborn", "tensorflow", "pytorch",
    # Tools & Platforms
    "git", "github", "vs code", "vscode", "google colab", "vercel", "excel", "linux", "docker"
}

# Explicit Fresher and Senior signals
FRESHER_SIGNALS = {
    "fresher", "freshers", "entry level", "entry-level", "junior", "intern", "internship",
    "trainee", "graduate", "0-1", "0-2", "0 to 1", "0 to 2", "zero", "college",
    "batch of", "2024", "2025", "2026", "pass out", "passout", "no experience"
}

SENIOR_SIGNALS = {
    "senior", "lead", "principal", "architect", "staff", "manager", "director",
    "5+", "6+", "7+", "8+", "10+", "5 to", "6 to", "7 to", "8 to"
}


class JobMatcher:
    def __init__(self):
        self.candidate_skills = get_all_candidate_skills()
        self.profile_text = get_profile_summary_text()
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def extract_keywords_from_text(self, text: str) -> List[str]:
        """Extracts recognizable technical keywords from text."""
        lowered = text.lower()
        found = set()
        for kw in KNOWN_TECH_KEYWORDS:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, lowered):
                found.add(kw)
        return sorted(list(found))

    def detect_job_track(self, job_title: str, text: str) -> str:
        """Determines whether the role is Frontend, Backend, AI/ML, or General."""
        t_low = (job_title + " " + text[:500]).lower()
        if any(k in t_low for k in ["front", "frontend", "ui", "react", "html", "web design"]):
            return "frontend"
        elif any(k in t_low for k in ["machine learning", "ai", "ml", "data science", "deep learning"]):
            return "aiml"
        elif any(k in t_low for k in ["backend", "back-end", "python", "fastapi", "django", "flask", "api", "software engineer"]):
            return "backend"
        return "fullstack"

    def check_experience_requirement(self, text: str) -> Tuple[bool, bool, int]:
        """
        Detects if the role is suitable for a fresher vs senior.
        Returns: (is_fresher_friendly, is_senior_disqualified, max_exp)
        """
        lowered = text.lower()
        is_fresher = any(signal in lowered for signal in FRESHER_SIGNALS)
        is_senior = any(signal in lowered for signal in SENIOR_SIGNALS)

        # Look for explicit numerical years
        exp_matches = re.findall(r'(\d+)\+?\s*(?:to|-)\s*(\d+)?\s*years?', lowered)
        years = []
        for match in exp_matches:
            if match[0]:
                years.append(int(match[0]))
            if match[1]:
                years.append(int(match[1]))
        max_exp = max(years) if years else 0

        if max_exp >= 4:
            is_senior = True
        if max_exp <= 2 and not is_senior:
            is_fresher = True

        return is_fresher, is_senior, max_exp

    def evaluate_match(self, job_title: str, job_description: str) -> Dict[str, Any]:
        """
        Evaluates match percentage tailored for Narendra as a Fresher.
        Considers track (Frontend / Backend / AI/ML) and rewards entry-level roles.
        """
        job_full_text = f"{job_title}\n{job_description}"
        job_keywords = self.extract_keywords_from_text(job_full_text)
        track = self.detect_job_track(job_title, job_full_text)

        # 1. Skill Overlap Score (Track-Aware)
        track_skills = [s.lower() for s in CANDIDATE_PROFILE["tracks"].get(track, {}).get("skills", CANDIDATE_PROFILE["all_skills"])]
        matched_skills = []
        missing_skills = []

        for kw in job_keywords:
            if kw in self.candidate_skills or kw in track_skills:
                matched_skills.append(kw)
            else:
                missing_skills.append(kw)

        if job_keywords:
            skill_overlap_ratio = len(matched_skills) / len(job_keywords)
        else:
            skill_overlap_ratio = 0.55

        # 2. TF-IDF Text Cosine Similarity
        try:
            tfidf_matrix = self.vectorizer.fit_transform([self.profile_text, job_full_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except Exception:
            similarity = skill_overlap_ratio

        # 3. Title Relevance Score for Fresher Target Roles
        title_low = job_title.lower()
        title_score = 0.40
        for target_role in CANDIDATE_PROFILE["target_roles"]:
            if target_role.lower() in title_low:
                title_score = 1.0
                break
        if title_score < 1.0:
            if any(k in title_low for k in ["python", "developer", "engineer", "frontend", "backend", "web", "ai", "ml", "intern", "trainee"]):
                title_score = 0.80

        # Weighted calculation
        raw_score = (0.45 * skill_overlap_ratio) + (0.30 * similarity) + (0.25 * title_score)
        percentage = round(raw_score * 100, 1)

        # 4. Fresher vs Senior Multipliers
        is_fresher_friendly, is_senior, years_req = self.check_experience_requirement(job_full_text)

        if is_fresher_friendly:
            # Significant boost for Fresher / Entry Level roles!
            percentage += 15.0

        if is_senior:
            # Harsh penalty for Senior / Lead roles (>4 years)
            percentage -= 35.0

        # Clamp between 0 and 100
        percentage = float(max(0.0, min(100.0, round(percentage, 1))))

        # Recommendation determination
        if percentage >= 70.0:
            recommendation = "APPLY (>= 70%)"
            action = "AUTO_APPLY"
        elif percentage >= 45.0:
            recommendation = "REVIEW (< 70%)"
            action = "EMAIL_REVIEW"
        else:
            recommendation = "SKIP (< 45%)"
            action = "IGNORE"

        return {
            "score": percentage,
            "meets_threshold": bool(percentage >= 70.0),
            "track": track.upper(),
            "action": action,
            "recommendation": recommendation,
            "matched_skills": [s.title() for s in matched_skills],
            "missing_skills": [s.title() for s in missing_skills[:6]],
            "job_keywords_count": int(len(job_keywords)),
            "matched_keywords_count": int(len(matched_skills)),
            "is_fresher_friendly": bool(is_fresher_friendly),
            "is_senior": bool(is_senior),
            "years_required": int(years_req)
        }
