"""
CVCraft CV Business Logic Service
Handles validation, completion score calculation, and realistic sample data generation.
"""

import re
from typing import Dict, List, Tuple, Any
from models.cv_model import (
    CVDocument, PersonalInfo, ExperienceItem, EducationItem,
    SkillItem, ProjectItem, CertificationItem, LanguageItem,
    AchievementItem, VolunteerItem, ReferenceItem, CustomSection, CustomSectionItem
)

class CVService:
    @staticmethod
    def calculate_completion(cv: CVDocument) -> Tuple[int, List[str]]:
        """
        Calculates completion percentage (0-100%) and returns list of missing recommendations.
        """
        score = 0
        missing = []

        # 1. Personal Information (30 pts)
        if cv.personal.full_name.strip():
            score += 10
        else:
            missing.append("Full Name is missing")

        if cv.personal.professional_title.strip():
            score += 5
        else:
            missing.append("Professional Title is missing")

        if cv.personal.email.strip() and CVService.validate_email(cv.personal.email):
            score += 5
        else:
            missing.append("Valid Email is missing")

        if cv.personal.phone.strip():
            score += 5
        else:
            missing.append("Phone Number is missing")

        if cv.personal.location.strip():
            score += 5
        else:
            missing.append("Location (City, Country) is missing")

        # 2. Professional Summary (15 pts)
        if len(cv.summary.strip()) >= 50:
            score += 15
        elif len(cv.summary.strip()) > 0:
            score += 8
            missing.append("Professional Summary is too brief (recommend 50+ words)")
        else:
            missing.append("Professional Summary is missing")

        # 3. Work Experience (20 pts)
        if len(cv.experience) >= 2:
            score += 20
        elif len(cv.experience) == 1:
            score += 12
            missing.append("Add at least 2 work experience entries for best impact")
        else:
            missing.append("Work Experience entries are missing")

        # 4. Education (10 pts)
        if len(cv.education) >= 1:
            score += 10
        else:
            missing.append("Education section is empty")

        # 5. Skills (15 pts)
        if len(cv.skills) >= 6:
            score += 15
        elif len(cv.skills) >= 3:
            score += 10
            missing.append("Add more key skills (recommend 6+ skills)")
        else:
            missing.append("Add at least 3 skills")

        # 6. Projects & Certifications (10 pts)
        if len(cv.projects) >= 1 or len(cv.certifications) >= 1:
            score += 10
        else:
            missing.append("Add at least 1 project or certification")

        return min(100, score), missing

    @staticmethod
    def validate_email(email: str) -> bool:
        if not email:
            return False
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        if not phone:
            return False
        pattern = r"^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]{6,15}$"
        return bool(re.match(pattern, phone.strip()))

    @staticmethod
    def validate_url(url: str) -> bool:
        if not url:
            return True  # Optional
        pattern = r"^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
        return bool(re.match(pattern, url.strip()))

    @staticmethod
    def create_sample_cv() -> CVDocument:
        """
        Creates a realistic, high-impact demo CV for a Senior Software Engineer.
        """
        cv = CVDocument(
            name="Alexander Mitchell - Senior Full Stack Engineer",
            job_target="Senior Full Stack Engineer & Cloud Architect",
            template_id="modern"
        )
        
        cv.personal = PersonalInfo(
            full_name="Alexander Mitchell",
            professional_title="Senior Full Stack Engineer & Cloud Architect",
            email="alexander.mitchell@craftmail.dev",
            phone="+1 (555) 234-8901",
            location="San Francisco, CA (Hybrid / Remote)",
            website="https://alexmitchell.tech",
            linkedin="https://linkedin.com/in/alexandermitchell-dev",
            github="https://github.com/alexmitchell-tech",
            portfolio="https://alexmitchell.tech/portfolio",
            profile_photo_style="circle"
        )

        cv.summary = (
            "Innovative and results-driven Senior Full Stack Engineer with 7+ years of experience designing, "
            "scaling, and maintaining distributed web applications and high-throughput microservices. Proven track "
            "record in reducing cloud infrastructure latency by 42% and orchestrating zero-downtime CI/CD pipelines. "
            "Passionate about clean architecture, developer productivity, and building resilient user experiences."
        )

        cv.experience = [
            ExperienceItem(
                company="Aetheris Cloud Technologies",
                job_title="Lead Software Engineer",
                location="San Francisco, CA",
                employment_type="Full-time",
                start_date="2022 - Present",
                end_date="Current",
                is_current=True,
                responsibilities=(
                    "• Spearheaded architecture of enterprise event-driven data streaming platform processing 80M+ daily events.\n"
                    "• Directed a cross-functional team of 9 engineers across web, backend, and DevOps domains.\n"
                    "• Spearheaded migration from monolithic REST backend to gRPC & GraphQL services, slashing payload overhead by 38%."
                ),
                achievements="Awarded 2024 Tech Innovator of the Year for optimizing caching layers, saving $140,000 in AWS billings annually."
            ),
            ExperienceItem(
                company="Nexus Velocity Labs",
                job_title="Senior Python & Frontend Engineer",
                location="Austin, TX (Remote)",
                employment_type="Full-time",
                start_date="2019",
                end_date="2022",
                is_current=False,
                responsibilities=(
                    "• Engineered reactive user interfaces using modern reactive UI frameworks and optimized WebSocket state sync.\n"
                    "• Built asynchronous analytics engines and ETL pipelines using Python, FastAPI, Redis, and PostgreSQL.\n"
                    "• Mentored 6 junior and mid-level developers in automated testing, code reviews, and SOLID design patterns."
                ),
                achievements="Boosted app performance score from 68 to 97 on Lighthouse, elevating user retention by 24%."
            ),
            ExperienceItem(
                company="Starlight Digital Interactive",
                job_title="Software Developer",
                location="Seattle, WA",
                employment_type="Full-time",
                start_date="2017",
                end_date="2019",
                is_current=False,
                responsibilities=(
                    "• Developed customer-facing portal features and secure payment gateway integrations.\n"
                    "• Automated unit and integration test suites, lifting code coverage from 52% to 91%."
                ),
                achievements="Designed an automated invoice reconciliation tool that reduced manual accounting audit time by 60 hours monthly."
            )
        ]

        cv.education = [
            EducationItem(
                institution="University of California, Berkeley",
                degree="Bachelor of Science",
                field_of_study="Computer Science & Information Engineering",
                start_date="2013",
                end_date="2017",
                grade="GPA 3.86 / 4.0 (Dean's Honor List)",
                description="Specialized in Distributed Systems, Algorithm Design, and Human-Computer Interaction."
            )
        ]

        cv.skills = [
            SkillItem(name="Python (FastAPI, Django, AsyncIO)", category="Programming Languages", proficiency="Expert"),
            SkillItem(name="TypeScript & Modern JavaScript", category="Programming Languages", proficiency="Expert"),
            SkillItem(name="Go (Golang)", category="Programming Languages", proficiency="Advanced"),
            SkillItem(name="React & Modern UI Frameworks", category="Frameworks", proficiency="Expert"),
            SkillItem(name="PostgreSQL & MongoDB", category="Tools", proficiency="Expert"),
            SkillItem(name="Docker & Kubernetes", category="Tools", proficiency="Advanced"),
            SkillItem(name="AWS (Lambda, ECS, S3, CloudFront)", category="Technical Skills", proficiency="Advanced"),
            SkillItem(name="Distributed Systems & Microservices", category="Technical Skills", proficiency="Expert"),
            SkillItem(name="CI/CD & DevOps Automation", category="Tools", proficiency="Advanced"),
            SkillItem(name="System Architecture & Scalability", category="Technical Skills", proficiency="Expert"),
            SkillItem(name="Cross-Functional Leadership & Agile", category="Soft Skills", proficiency="Expert"),
            SkillItem(name="Strategic Problem Solving", category="Soft Skills", proficiency="Expert")
        ]

        cv.projects = [
            ProjectItem(
                name="StreamPulse Real-Time Telemetry Engine",
                role="Creator & Lead Architect",
                technologies="Python, WebSockets, Redis, Vue, Docker",
                github_url="https://github.com/alexmitchell-tech/streampulse",
                live_demo_url="https://streampulse.demo.dev",
                description="High-frequency telemetry dashboard providing sub-50ms observability for IoT devices across 12 geographic clusters."
            ),
            ProjectItem(
                name="OmniAuth Secure SSO Gateway",
                role="Principal Developer",
                technologies="OAuth2, OpenID Connect, FastAPI, PyJWT",
                github_url="https://github.com/alexmitchell-tech/omniauth-gateway",
                live_demo_url="",
                description="Lightweight microservices authentication bridge supporting RBAC, multi-factor biometric auth, and rate-limiting."
            )
        ]

        cv.certifications = [
            CertificationItem(
                name="AWS Certified Solutions Architect – Professional",
                issuer="Amazon Web Services",
                issue_date="2023",
                expiration_date="2026",
                credential_id="AWS-PSA-8890214",
                credential_url="https://aws.amazon.com/verification"
            ),
            CertificationItem(
                name="Certified Kubernetes Administrator (CKA)",
                issuer="Cloud Native Computing Foundation (CNCF)",
                issue_date="2022",
                expiration_date="2025",
                credential_id="CKA-992104"
            )
        ]

        cv.languages = [
            LanguageItem(name="English", proficiency="Native"),
            LanguageItem(name="Spanish", proficiency="Conversational"),
            LanguageItem(name="German", proficiency="Basic")
        ]

        cv.achievements = [
            AchievementItem(
                title="1st Place Winner — Silicon Valley Hackathon 2023",
                date="Nov 2023",
                description="Developed an offline-first emergency disaster relief coordination platform with peer-to-peer mesh networking."
            ),
            AchievementItem(
                title="Patent Co-Inventor: Distributed State Synchronization",
                date="Mar 2022",
                description="Filed US Patent for low-latency decentralized data conflict resolution algorithms."
            )
        ]

        cv.volunteer = [
            VolunteerItem(
                organization="Code for Good Community Mentorship",
                role="Volunteer Coding Mentor",
                start_date="2020",
                end_date="Present",
                description="Mentored over 35 underrepresented high school students in fundamental programming and web development."
            )
        ]

        cv.references = [
            ReferenceItem(
                name="Sarah Jenkins",
                job_title="VP of Engineering",
                company="Aetheris Cloud Technologies",
                email="s.jenkins@aetheris.dev",
                phone="+1 (555) 987-6543"
            )
        ]

        cv.references_on_request = True
        return cv
