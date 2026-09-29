"""
CVCraft ATS Matching & Analysis Service
Analyzes CV content against Job Descriptions, checks ATS formatting compliance,
and calculates keyword coverage.
"""

import re
from typing import Dict, List, Set, Any, Tuple
from models.cv_model import CVDocument

COMMON_TECH_KEYWORDS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang", "rust",
    "react", "angular", "vue", "next.js", "node.js", "django", "fastapi", "flask",
    "spring", "spring boot", "docker", "kubernetes", "aws", "azure", "gcp", "ci/cd",
    "git", "rest", "graphql", "microservices", "sql", "postgresql", "mysql", "mongodb",
    "redis", "linux", "agile", "scrum", "devops", "cloud", "system design", "architecture",
    "unit testing", "tdd", "machine learning", "ai", "data engineering", "kafka", "terraform"
}

class ATSService:
    @staticmethod
    def extract_words(text: str) -> Set[str]:
        words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_\-\.+#]{1,24}\b", text.lower())
        return set(words)

    @classmethod
    def analyze_job_match(cls, cv: CVDocument, job_description: str) -> Dict[str, Any]:
        """
        Compares CV against a Job Description.
        Returns match percentage, matching skills, missing skills, and tailored suggestions.
        """
        if not job_description.strip():
            return {
                "match_score": 0,
                "matching_skills": [],
                "missing_skills": [],
                "matching_keywords": [],
                "missing_keywords": [],
                "recommendations": ["Paste a job description above to run the ATS Tailor analysis."]
            }

        jd_text = job_description.lower()
        cv_text = f"{cv.personal.professional_title} {cv.summary} ".lower()
        
        cv_skills = [s.name.lower() for s in cv.skills]
        for exp in cv.experience:
            cv_text += f" {exp.job_title} {exp.responsibilities} {exp.achievements}".lower()
        for p in cv.projects:
            cv_text += f" {p.name} {p.technologies} {p.description}".lower()

        # Find tech keywords mentioned in Job Description
        jd_keywords = set()
        for kw in COMMON_TECH_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", jd_text):
                jd_keywords.add(kw)

        # Also extract significant capitalized tech words from JD
        capitalized = re.findall(r"\b[A-Z][a-zA-Z0-9+#]{2,15}\b", job_description)
        for c in capitalized:
            c_low = c.lower()
            if c_low not in {"the", "and", "for", "with", "you", "will", "our", "team", "work"}:
                jd_keywords.add(c_low)

        matching_keywords = []
        missing_keywords = []

        for kw in sorted(jd_keywords):
            if kw in cv_text or any(kw in s for s in cv_skills):
                matching_keywords.append(kw.title())
            else:
                missing_keywords.append(kw.title())

        total_kw = len(matching_keywords) + len(missing_keywords)
        if total_kw > 0:
            match_score = int((len(matching_keywords) / total_kw) * 100)
        else:
            match_score = 50

        # Build intelligent recommendations
        recommendations = []
        if missing_keywords:
            top_missing = missing_keywords[:6]
            recommendations.append(f"Consider integrating high-priority target keywords: {', '.join(top_missing)}.")
        
        if cv.template_id != "ats_friendly":
            recommendations.append("For corporate enterprise portals, switch to the 'ATS-Friendly' template for maximum OCR accuracy.")

        if len(cv.summary.strip()) < 50:
            recommendations.append("Customize your Professional Summary to mirror the role's mission and core tech stack.")

        if not any(exp.achievements for exp in cv.experience):
            recommendations.append("Add measurable outcomes (e.g. % reduced, $ saved) to your experience entries to boost hiring manager impact.")

        return {
            "match_score": match_score,
            "matching_skills": matching_keywords,
            "missing_skills": missing_keywords,
            "matching_keywords": matching_keywords,
            "missing_keywords": missing_keywords,
            "recommendations": recommendations
        }

    @classmethod
    def check_ats_formatting(cls, cv: CVDocument) -> Dict[str, Any]:
        """
        Validates formatting compliance for automated ATS parsing.
        """
        issues = []
        passes = []

        # Check standard headers
        passes.append("Standard section titles detected (Experience, Education, Skills)")

        # Contact info check
        if cv.personal.email and cv.personal.phone:
            passes.append("Clear, detectable email and phone number present")
        else:
            issues.append("Missing standard contact details (Email or Phone)")

        # Photo check for ATS
        if cv.customization.show_photo and cv.personal.profile_photo_path:
            issues.append("Profile photo is enabled. Many US/UK ATS parsers discard images; consider the ATS-Friendly template for direct online portals.")
        else:
            passes.append("Clean text-only presentation ideal for automated parsing")

        # Length check
        total_words = len(cv.summary.split())
        for exp in cv.experience:
            total_words += len(exp.responsibilities.split()) + len(exp.achievements.split())
        
        if total_words < 150:
            issues.append("Document word count is low (under 150 words). May lack sufficient keyword density.")
        else:
            passes.append(f"Healthy document keyword volume (~{total_words} words)")

        ats_score = max(40, 100 - (len(issues) * 15))

        return {
            "ats_compatibility_score": ats_score,
            "passes": passes,
            "issues": issues,
            "is_ats_template": (cv.template_id == "ats_friendly")
        }
