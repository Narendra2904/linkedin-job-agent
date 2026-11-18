"""
Job requirement comparator and scoring engine for Narendra Yenagandula.
Computes precise percentage match between job postings and candidate profile.
"""

import re
from typing import Dict, List, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from profile_data import CANDIDATE_PROFILE, get_all_candidate_skills, get_profile_summary_text

# Comprehensive catalog of relevant tech keywords to detect in job descriptions
KNOWN_TECH_KEYWORDS = {
    "python", "javascript", "typescript", "c++", "java", "sql", "mysql", "postgresql",
    "machine learning", "deep learning", "artificial intelligence", "ai", "ml", "nlp",
    "natural language processing", "computer vision", "opencv", "svm", "support vector machine",
    "random forest", "decision trees", "xgboost", "linear regression", "logistic regression",
    "clustering", "classification", "supervised learning", "unsupervised learning",
    "model training", "model evaluation", "data preprocessing", "feature engineering",
    "scikit-learn", "sklearn", "tensorflow", "pytorch", "keras", "pandas", "numpy",
    "matplotlib", "seaborn", "fastapi", "flask", "django", "rest api", "api", "graphql",
    "html", "html5", "css", "css3", "react", "node", "git", "github", "docker", "kubernetes",
    "aws", "azure", "gcp", "google colab", "vs code", "vercel", "excel", "linux"
}


class JobMatcher:
    def __init__(self):
        self.candidate_skills = get_all_candidate_skills()
        self.profile_text = get_profile_summary_text()
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def extract_keywords_from_text(self, text: str) -> List[str]:
        """Extracts recognizable technical keywords from text."""
        lowered = text.lower()
        # Clean punctuation for exact word boundary matching
        found = set()
        for kw in KNOWN_TECH_KEYWORDS:
            # Word boundary regex pattern
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, lowered):
                found.add(kw)
        return sorted(list(found))

    def check_experience_requirement(self, text: str) -> Tuple[bool, int]:
        """Checks if the job requires high years of experience (e.g. 5+ years)."""
        # Look for patterns like '5+ years', '3-5 years', '8+ years'
        exp_matches = re.findall(r'(\d+)\+?\s*(?:to|-)\s*(\d+)?\s*years?', text.lower())
        years = []
        for match in exp_matches:
            if match[0]:
                years.append(int(match[0]))
            if match[1]:
                years.append(int(match[1]))
        max_exp = max(years) if years else 0
        is_senior = max_exp >= 4
        return is_senior, max_exp

    def evaluate_match(self, job_title: str, job_description: str) -> Dict[str, Any]:
        """
        Calculates match percentage and returns breakdown.
        Formula:
          Match% = 0.45 * (Skill Overlap) + 0.30 * (TF-IDF Similarity) + 0.25 * (Title Relevance)
          With adjustments for senior roles or entry-level friendly keywords.
        """
        job_full_text = f"{job_title}\n{job_description}"
        job_keywords = self.extract_keywords_from_text(job_full_text)

        # 1. Skill Overlap Score
        matched_skills = []
        missing_skills = []

        for kw in job_keywords:
            if kw in self.candidate_skills:
                matched_skills.append(kw)
            else:
                missing_skills.append(kw)

        if job_keywords:
            skill_overlap_ratio = len(matched_skills) / len(job_keywords)
        else:
            # If no specific tech keywords identified, default to neutral
            skill_overlap_ratio = 0.5

        # 2. TF-IDF Text Cosine Similarity
        try:
            tfidf_matrix = self.vectorizer.fit_transform([self.profile_text, job_full_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except Exception:
            similarity = skill_overlap_ratio

        # 3. Title Relevance Score
        title_low = job_title.lower()
        title_score = 0.0
        target_roles_low = [r.lower() for r in CANDIDATE_PROFILE["target_roles"]]
        
        if any(role in title_low for role in target_roles_low):
            title_score = 1.0
        elif any(k in title_low for k in ["ai", "ml", "machine learning", "python", "data"]):
            title_score = 0.85
        elif any(k in title_low for k in ["software", "developer", "engineer", "intern"]):
            title_score = 0.65
        else:
            title_score = 0.35

        # Raw weighted score
        raw_score = (0.45 * skill_overlap_ratio) + (0.30 * similarity) + (0.25 * title_score)
        percentage = round(raw_score * 100, 1)

        # Apply boost for entry level / graduate / intern
        is_entry = any(k in job_full_text.lower() for k in ["fresher", "intern", "entry level", "junior", "0-1", "0-2", "graduate"])
        if is_entry:
            percentage = min(100.0, percentage + 8.0)

        # Apply penalty for high years of experience requirement
        is_senior, years_req = self.check_experience_requirement(job_full_text)
        if is_senior and years_req >= 5:
            percentage = max(10.0, percentage - 20.0)

        # Keep score in realistic 0-100 bounds
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
            "action": action,
            "recommendation": recommendation,
            "matched_skills": [s.title() for s in matched_skills],
            "missing_skills": [s.title() for s in missing_skills[:8]],  # Top missing skills
            "job_keywords_count": int(len(job_keywords)),
            "matched_keywords_count": int(len(matched_skills)),
            "is_entry_level": bool(is_entry),
            "is_senior": bool(is_senior),
            "years_required": int(years_req)
        }
