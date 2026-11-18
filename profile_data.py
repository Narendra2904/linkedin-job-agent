"""
Candidate profile knowledge base for Narendra Yenagandula.
Extracted and enriched from AIML.pdf for automated matching, scoring, and application.
"""

from typing import List, Dict, Any

CANDIDATE_PROFILE: Dict[str, Any] = {
    "name": "Narendra Yenagandula",
    "headline": "Aspiring AI/ML Engineer | Python & Machine Learning | FastAPI, Computer Vision & Scikit-Learn | B.Tech CSE (AI & ML) '26",
    "email": "yenagandula.narendra@gmail.com",
    "phone": "+91 9989114207",
    "location": "Hyderabad, Telangana, India",
    "linkedin_url": "https://www.linkedin.com/in/narendra-yenagandula/",
    "github_url": "https://github.com/Narendra2904",
    "education": [
        {
            "degree": "B.Tech – Computer Science and Engineering (AI & ML)",
            "institution": "Vaageswari College of Engineering",
            "location": "Karimnagar, Telangana",
            "years": "2023 – 2026",
            "gpa": "7.2/10"
        },
        {
            "degree": "Diploma – Electronics and Communication Engineering",
            "institution": "Vaageswari College of Engineering",
            "location": "Karimnagar, Telangana",
            "years": "2020 – 2023",
            "gpa": "8.56/10"
        },
        {
            "degree": "Secondary School Certificate (SSC)",
            "institution": "Zilla Parishad High School, Sircilla",
            "location": "Sircilla, Telangana",
            "years": "2020",
            "gpa": "10/10"
        }
    ],
    "target_roles": [
        "AI/ML Engineer",
        "Machine Learning Engineer",
        "Junior Machine Learning Engineer",
        "AI Engineer",
        "Python Developer",
        "Junior Python Developer",
        "Data Science Intern",
        "Machine Learning Intern",
        "Backend Developer (Python/FastAPI)"
    ],
    "target_locations": [
        "Hyderabad",
        "Bengaluru",
        "Bangalore",
        "Remote",
        "India"
    ],
    "core_skills": [
        "Python",
        "Machine Learning",
        "Supervised Learning",
        "Classification",
        "Support Vector Machine",
        "SVM",
        "Model Training",
        "Model Evaluation",
        "Image Classification",
        "Computer Vision",
        "FastAPI",
        "REST API",
        "HTML5",
        "CSS3",
        "JavaScript",
        "MySQL",
        "SQL",
        "Git",
        "GitHub",
        "VS Code",
        "Google Colab",
        "Vercel",
        "Microsoft Excel",
        "Data Preprocessing",
        "Scikit-Learn"
    ],
    "extended_skills": [
        "Deep Learning",
        "Neural Networks",
        "Pandas",
        "NumPy",
        "Matplotlib",
        "TensorFlow",
        "PyTorch",
        "Natural Language Processing",
        "NLP",
        "Flask",
        "Django",
        "Docker",
        "PostgreSQL",
        "Linux",
        "Cloud Computing",
        "Data Analysis",
        "Feature Engineering",
        "Algorithm Design",
        "Object-Oriented Programming",
        "OOP"
    ],
    "projects": [
        {
            "title": "Fruit Disease Detection System",
            "technologies": ["Python", "Machine Learning", "SVM", "Image Classification", "Google Colab", "Scikit-Learn"],
            "description": "Developed an image-based classification system to identify fruit diseases using Support Vector Machine (SVM). Applied ML techniques to train and evaluate the classification model with high accuracy."
        },
        {
            "title": "BTech Results Portal with AI Integration",
            "technologies": ["HTML", "Python", "FastAPI", "REST API", "Data Analysis", "AI Integration"],
            "description": "Developed a web platform for accessing university results. Integrated FastAPI backend services for efficient data retrieval and incorporated AI-driven features for student performance analysis."
        },
        {
            "title": "BTech Study Material Portal",
            "technologies": ["HTML5", "CSS3", "JavaScript", "Responsive Design", "Flexbox", "CSS Grid"],
            "description": "Engineered an academic resource platform to organize and provide access to B.Tech study materials with responsive layouts."
        }
    ],
    "certifications": [
        {
            "name": "Artificial Intelligence Foundation",
            "issuer": "Wipro TalentNext"
        },
        {
            "name": "Cloud Computing Foundation",
            "issuer": "Wipro FutureSkills"
        },
        {
            "name": "Python Programming",
            "issuer": "Reliance Academy"
        }
    ]
}


def get_all_candidate_skills() -> List[str]:
    """Returns combined normalized skill list for matching."""
    skills = set(s.lower() for s in CANDIDATE_PROFILE["core_skills"])
    skills.update(s.lower() for s in CANDIDATE_PROFILE["extended_skills"])
    return sorted(list(skills))


def get_profile_summary_text() -> str:
    """Builds a comprehensive text representation of candidate profile for vector/NLP similarity."""
    text_blocks = [
        CANDIDATE_PROFILE["name"],
        CANDIDATE_PROFILE["headline"],
        " ".join(CANDIDATE_PROFILE["target_roles"]),
        "Skills: " + ", ".join(CANDIDATE_PROFILE["core_skills"]),
        "Extended skills: " + ", ".join(CANDIDATE_PROFILE["extended_skills"]),
    ]
    for proj in CANDIDATE_PROFILE["projects"]:
        text_blocks.append(f"{proj['title']}: {proj['description']} ({', '.join(proj['technologies'])})")
    for cert in CANDIDATE_PROFILE["certifications"]:
        text_blocks.append(f"{cert['name']} by {cert['issuer']}")
    return "\n".join(text_blocks)
