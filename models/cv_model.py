"""
CVCraft Data Models
Clean, serializable models for CV documents, sections, and items.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
import uuid
from datetime import datetime

@dataclass
class PersonalInfo:
    full_name: str = ""
    professional_title: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    website: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    profile_photo_path: str = ""
    profile_photo_style: str = "circle"  # circle, square, none

@dataclass
class ExperienceItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    company: str = ""
    job_title: str = ""
    location: str = ""
    employment_type: str = "Full-time"  # Full-time, Part-time, Contract, Internship, Freelance
    start_date: str = ""
    end_date: str = ""
    is_current: bool = False
    responsibilities: str = ""
    achievements: str = ""

@dataclass
class EducationItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    start_date: str = ""
    end_date: str = ""
    grade: str = ""
    description: str = ""

@dataclass
class SkillItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: str = "Technical Skills"  # Technical Skills, Soft Skills, Tools, Frameworks, Programming Languages
    proficiency: str = "Advanced"  # Beginner, Intermediate, Advanced, Expert

@dataclass
class ProjectItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    role: str = ""
    technologies: str = ""
    github_url: str = ""
    live_demo_url: str = ""
    description: str = ""

@dataclass
class CertificationItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    issuer: str = ""
    issue_date: str = ""
    expiration_date: str = ""
    credential_id: str = ""
    credential_url: str = ""

@dataclass
class LanguageItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    proficiency: str = "Fluent"  # Basic, Conversational, Intermediate, Fluent, Native

@dataclass
class AchievementItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    date: str = ""
    description: str = ""

@dataclass
class VolunteerItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    organization: str = ""
    role: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""

@dataclass
class ReferenceItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    job_title: str = ""
    company: str = ""
    email: str = ""
    phone: str = ""

@dataclass
class CustomSectionItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    subtitle: str = ""
    date: str = ""
    description: str = ""

@dataclass
class CustomSection:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    section_name: str = "Publications"
    items: List[CustomSectionItem] = field(default_factory=list)

@dataclass
class CVCustomization:
    accent_palette: str = "Deep Indigo"
    custom_accent_hex: str = "#4F46E5"
    font_family: str = "Helvetica"
    font_size: str = "medium"  # small, medium, large
    line_height: float = 1.3
    section_spacing: int = 14
    page_margin: int = 36  # in points (0.5 inch)
    show_photo: bool = True
    photo_style: str = "circle"  # circle, square

DEFAULT_SECTION_ORDER = [
    "summary",
    "experience",
    "education",
    "skills",
    "projects",
    "certifications",
    "languages",
    "achievements",
    "volunteer",
    "references",
    "custom"
]

@dataclass
class CVDocument:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "My Professional CV"
    job_target: str = "Senior Software Engineer"
    template_id: str = "modern"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_favorite: bool = False
    parent_version_id: Optional[str] = None
    version_label: str = "Main"
    
    # Sections
    personal: PersonalInfo = field(default_factory=PersonalInfo)
    summary: str = ""
    experience: List[ExperienceItem] = field(default_factory=list)
    education: List[EducationItem] = field(default_factory=list)
    skills: List[SkillItem] = field(default_factory=list)
    projects: List[ProjectItem] = field(default_factory=list)
    certifications: List[CertificationItem] = field(default_factory=list)
    languages: List[LanguageItem] = field(default_factory=list)
    achievements: List[AchievementItem] = field(default_factory=list)
    volunteer: List[VolunteerItem] = field(default_factory=list)
    references: List[ReferenceItem] = field(default_factory=list)
    references_on_request: bool = False
    custom_sections: List[CustomSection] = field(default_factory=list)
    
    # Configuration & Ordering
    section_order: List[str] = field(default_factory=lambda: list(DEFAULT_SECTION_ORDER))
    customization: CVCustomization = field(default_factory=CVCustomization)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CVDocument':
        if not data:
            return cls()
        
        # Parse nested dataclasses safely
        personal_data = data.get("personal", {})
        personal = PersonalInfo(**personal_data) if isinstance(personal_data, dict) else PersonalInfo()
        
        experience = [
            ExperienceItem(**item) if isinstance(item, dict) else item 
            for item in data.get("experience", [])
        ]
        education = [
            EducationItem(**item) if isinstance(item, dict) else item 
            for item in data.get("education", [])
        ]
        skills = [
            SkillItem(**item) if isinstance(item, dict) else item 
            for item in data.get("skills", [])
        ]
        projects = [
            ProjectItem(**item) if isinstance(item, dict) else item 
            for item in data.get("projects", [])
        ]
        certifications = [
            CertificationItem(**item) if isinstance(item, dict) else item 
            for item in data.get("certifications", [])
        ]
        languages = [
            LanguageItem(**item) if isinstance(item, dict) else item 
            for item in data.get("languages", [])
        ]
        achievements = [
            AchievementItem(**item) if isinstance(item, dict) else item 
            for item in data.get("achievements", [])
        ]
        volunteer = [
            VolunteerItem(**item) if isinstance(item, dict) else item 
            for item in data.get("volunteer", [])
        ]
        references = [
            ReferenceItem(**item) if isinstance(item, dict) else item 
            for item in data.get("references", [])
        ]
        
        custom_sections = []
        for cs in data.get("custom_sections", []):
            if isinstance(cs, dict):
                items = [CustomSectionItem(**i) if isinstance(i, dict) else i for i in cs.get("items", [])]
                custom_sections.append(CustomSection(id=cs.get("id", str(uuid.uuid4())), section_name=cs.get("section_name", "Custom"), items=items))

        customization_data = data.get("customization", {})
        customization = CVCustomization(**customization_data) if isinstance(customization_data, dict) else CVCustomization()

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Untitled CV"),
            job_target=data.get("job_target", ""),
            template_id=data.get("template_id", "modern"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            is_favorite=data.get("is_favorite", False),
            parent_version_id=data.get("parent_version_id"),
            version_label=data.get("version_label", "Main"),
            personal=personal,
            summary=data.get("summary", ""),
            experience=experience,
            education=education,
            skills=skills,
            projects=projects,
            certifications=certifications,
            languages=languages,
            achievements=achievements,
            volunteer=volunteer,
            references=references,
            references_on_request=data.get("references_on_request", False),
            custom_sections=custom_sections,
            section_order=data.get("section_order", list(DEFAULT_SECTION_ORDER)),
            customization=customization
        )
