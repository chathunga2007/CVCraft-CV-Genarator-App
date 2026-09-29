"""
CVCraft Configuration and Constants
Product: CVCraft — "Build. Craft. Get Noticed."
"""

import os
from pathlib import Path

APP_NAME = "CVCraft"
APP_TAGLINE = "Build. Craft. Get Noticed."
APP_VERSION = "1.0.0"
APP_DEVELOPER = "CVCraft Team"
APP_LICENSE = "Commercial / Proprietary"

# Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "CVCraft-logo.png"
USER_DATA_DIR = BASE_DIR / "data"
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = USER_DATA_DIR / "cvcraft.db"
EXPORTS_DIR = USER_DATA_DIR / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
BACKUPS_DIR = USER_DATA_DIR / "backups"
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
PHOTOS_DIR = USER_DATA_DIR / "photos"
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

# Color Palettes
COLOR_PALETTES = {
    "Deep Indigo": {
        "primary": "#4F46E5",
        "secondary": "#4338CA",
        "accent": "#6366F1",
        "badge": "#EEF2FF",
        "badge_text": "#3730A3"
    },
    "Royal Purple": {
        "primary": "#7C3AED",
        "secondary": "#6D28D9",
        "accent": "#8B5CF6",
        "badge": "#F5F3FF",
        "badge_text": "#5B21B6"
    },
    "Emerald": {
        "primary": "#059669",
        "secondary": "#047857",
        "accent": "#10B981",
        "badge": "#ECFDF5",
        "badge_text": "#065F46"
    },
    "Navy Blue": {
        "primary": "#1E40AF",
        "secondary": "#1E3A8A",
        "accent": "#3B82F6",
        "badge": "#EFF6FF",
        "badge_text": "#1E40AF"
    },
    "Burgundy": {
        "primary": "#9F1239",
        "secondary": "#881337",
        "accent": "#F43F5E",
        "badge": "#FFF1F2",
        "badge_text": "#9F1239"
    },
    "Slate Charcoal": {
        "primary": "#334155",
        "secondary": "#1E293B",
        "accent": "#64748B",
        "badge": "#F8FAFC",
        "badge_text": "#334155"
    },
    "Obsidian Black": {
        "primary": "#18181B",
        "secondary": "#09090B",
        "accent": "#3F3F46",
        "badge": "#F4F4F5",
        "badge_text": "#18181B"
    }
}

AVAILABLE_FONTS = [
    "Helvetica",
    "Times-Roman",
    "Courier",
    "Arial"
]

TEMPLATES = [
    {
        "id": "modern",
        "name": "Modern Tech",
        "description": "Clean split-column layout with vibrant accents, ideal for tech professionals and modern roles.",
        "badge": "Popular",
        "preview_bg": "#4F46E5"
    },
    {
        "id": "minimal",
        "name": "Minimalist Clean",
        "description": "Sophisticated ultra-clean layout with refined typography and understated elegance.",
        "badge": "Clean",
        "preview_bg": "#18181B"
    },
    {
        "id": "executive",
        "name": "Executive Leadership",
        "description": "Prestigious top-header layout tailored for senior management, directors, and executives.",
        "badge": "Leadership",
        "preview_bg": "#1E3A8A"
    },
    {
        "id": "professional",
        "name": "Corporate Professional",
        "description": "Standard two-column corporate layout with structured sections and high readability.",
        "badge": "Corporate",
        "preview_bg": "#334155"
    },
    {
        "id": "creative",
        "name": "Creative Designer",
        "description": "Bold color block banner and expressive modern styling for design and media specialists.",
        "badge": "Creative",
        "preview_bg": "#7C3AED"
    },
    {
        "id": "developer",
        "name": "Software Engineer",
        "description": "Optimized for developers with prominent skills badges, project links, and GitHub highlights.",
        "badge": "Engineering",
        "preview_bg": "#059669"
    },
    {
        "id": "academic",
        "name": "Academic & Research",
        "description": "Rigorous traditional single-column format built for publications, research, and academia.",
        "badge": "Academic",
        "preview_bg": "#4B5563"
    },
    {
        "id": "ats_friendly",
        "name": "ATS-Friendly Optimized",
        "description": "Zero columns, standardized headers, and clean linear parsing for automated tracking systems.",
        "badge": "ATS 99%",
        "preview_bg": "#2563EB"
    }
]
