"""
Candidate profile knowledge base for Narendra Yenagandula.
Optimized for Freshers seeking AI/ML, Backend, and Frontend roles.
"""

from typing import List, Dict, Any

CANDIDATE_PROFILE: Dict[str, Any] = {
    "name": "Narendra Yenagandula",
    "headline": "Fresher Software Engineer | AI/ML, Backend (Python/FastAPI) & Frontend (HTML/CSS/JS) | B.Tech CSE (AI & ML) '26",
    "email": "yenagandula.narendra@gmail.com",
    "phone": "+91 9989114207",
    "location": "Hyderabad, Telangana, India",
    "linkedin_url": "https://www.linkedin.com/in/narendra-yenagandula/",
    "github_url": "https://github.com/Narendra2904",
    "experience_level": "Fresher (0-1 years / Entry-Level / Intern)",
    
    # 3 Major Tracks for Freshers
    "tracks": {
        "frontend": {
            "title": "Frontend Developer (Fresher)",
            "roles": [
                "Frontend Developer",
                "Junior Frontend Developer",
                "Web Developer",
                "Junior Web Developer",
                "HTML CSS JavaScript Developer",
                "UI Developer Fresher",
                "Frontend Intern"
            ],
            "skills": [
                "HTML5", "CSS3", "JavaScript", "Flexbox", "CSS Grid",
                "Responsive Design", "DOM Manipulation", "Bootstrap",
                "Tailwind", "React", "Frontend", "UI", "Web Development",
                "Vercel", "Git", "GitHub"
            ]
        },
        "backend": {
            "title": "Backend Developer (Python/FastAPI)",
            "roles": [
                "Backend Developer",
                "Junior Backend Developer",
                "Python Developer",
                "Junior Python Developer",
                "FastAPI Developer",
                "Software Engineer Fresher",
                "Backend Intern",
                "Python Intern"
            ],
            "skills": [
                "Python", "FastAPI", "REST API", "API", "MySQL", "SQL",
                "Relational Databases", "JSON", "Object-Oriented Programming",
                "OOP", "Data Structures", "Algorithms", "PostgreSQL",
                "Git", "GitHub", "Linux", "VS Code"
            ]
        },
        "aiml": {
            "title": "AI/ML Engineer (Fresher)",
            "roles": [
                "AI/ML Engineer",
                "Machine Learning Engineer",
                "Junior Machine Learning Engineer",
                "AI Engineer",
                "Data Science Intern",
                "Machine Learning Intern",
                "Junior AI Engineer"
            ],
            "skills": [
                "Python", "Machine Learning", "Supervised Learning",
                "Classification", "Support Vector Machine", "SVM",
                "Model Training", "Model Evaluation", "Image Classification",
                "Computer Vision", "Scikit-Learn", "Data Preprocessing",
                "Feature Engineering", "Pandas", "NumPy", "Google Colab"
            ]
        },
        "fullstack": {
            "title": "Full Stack Developer (Fresher)",
            "roles": [
                "Full Stack Developer",
                "Junior Full Stack Developer",
                "Python Full Stack Developer",
                "Software Developer Fresher",
                "Graduate Trainee Engineer"
            ],
            "skills": [
                "HTML5", "CSS3", "JavaScript", "Python", "FastAPI",
                "MySQL", "SQL", "REST API", "Responsive Design",
                "Git", "GitHub", "Vercel"
            ]
        }
    },

    "target_roles": [
        # Fresher AI/ML
        "AI/ML Engineer",
        "Machine Learning Engineer",
        "Junior Machine Learning Engineer",
        "AI Engineer",
        "Data Science Intern",
        "Machine Learning Intern",
        # Fresher Backend
        "Backend Developer",
        "Junior Backend Developer",
        "Python Developer",
        "Junior Python Developer",
        "FastAPI Developer",
        "Python Intern",
        # Fresher Frontend
        "Frontend Developer",
        "Junior Frontend Developer",
        "Web Developer",
        "Junior Web Developer",
        "UI Developer",
        "Frontend Intern",
        # General Fresher
        "Software Engineer Fresher",
        "Graduate Trainee Engineer",
        "Associate Software Engineer",
        "Junior Software Developer"
    ],

    "target_locations": [
        "Hyderabad",
        "Bengaluru",
        "Bangalore",
        "Pune",
        "Chennai",
        "Noida",
        "Gurugram",
        "Remote",
        "India"
    ],

    "all_skills": [
        # Frontend
        "HTML5", "HTML", "CSS3", "CSS", "JavaScript", "Flexbox", "CSS Grid",
        "Responsive Web Design", "DOM", "Vercel",
        # Backend
        "Python", "FastAPI", "REST API", "API", "MySQL", "SQL", "Database Design",
        "OOP", "Data Structures", "Algorithms",
        # AI/ML
        "Machine Learning", "Supervised Learning", "Classification",
        "Support Vector Machine", "SVM", "Model Training", "Model Evaluation",
        "Image Classification", "Computer Vision", "Scikit-Learn",
        "Data Preprocessing", "Feature Engineering",
        # General & Tools
        "Git", "GitHub", "VS Code", "Google Colab", "Microsoft Excel", "Linux"
    ],

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

    "projects": [
        {
            "title": "Fruit Disease Detection System",
            "track": "AI/ML",
            "technologies": ["Python", "Machine Learning", "SVM", "Image Classification", "Google Colab", "Scikit-Learn"],
            "description": "Developed an image-based classification system to identify fruit diseases using Support Vector Machine (SVM) and machine learning techniques."
        },
        {
            "title": "BTech Results Portal with AI Integration",
            "track": "Backend & Full Stack",
            "technologies": ["HTML", "Python", "FastAPI", "MySQL", "REST API", "AI Integration"],
            "description": "Developed a web platform for accessing university results. Integrated FastAPI backend services for efficient data retrieval and incorporated AI-driven performance insights."
        },
        {
            "title": "BTech Study Material Portal",
            "track": "Frontend",
            "technologies": ["HTML5", "CSS3", "JavaScript", "Responsive Design", "Flexbox", "CSS Grid", "Vercel"],
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
    return sorted(list(set(s.lower() for s in CANDIDATE_PROFILE["all_skills"])))


def get_profile_summary_text(track: str = "all") -> str:
    """Builds a comprehensive text representation of candidate profile for vector/NLP similarity."""
    text_blocks = [
        CANDIDATE_PROFILE["name"],
        CANDIDATE_PROFILE["headline"],
        " ".join(CANDIDATE_PROFILE["target_roles"]),
        "Skills: " + ", ".join(CANDIDATE_PROFILE["all_skills"]),
    ]
    for proj in CANDIDATE_PROFILE["projects"]:
        text_blocks.append(f"{proj['title']} ({proj['track']}): {proj['description']} ({', '.join(proj['technologies'])})")
    for cert in CANDIDATE_PROFILE["certifications"]:
        text_blocks.append(f"{cert['name']} by {cert['issuer']}")
    return "\n".join(text_blocks)
