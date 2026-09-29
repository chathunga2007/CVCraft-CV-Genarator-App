"""
CVCraft PDF Service
Production-grade multi-page A4 PDF rendering with 8 distinct template layouts,
exact styling, color palettes, and real-time page rendering via PyMuPDF.
"""

import io
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

import pymupdf
from PIL import Image as PILImage, ImageDraw, ImageOps

from models.cv_model import CVDocument
from config import COLOR_PALETTES

def hex_to_rl_color(hex_str: str, default=colors.HexColor("#4F46E5")):
    try:
        if not hex_str.startswith("#"):
            hex_str = "#" + hex_str
        return colors.HexColor(hex_str)
    except Exception:
        return default

class NumberedCanvas(canvas.Canvas):
    """Adds professional dynamic page numbering (e.g. Page 1 of 2)"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if page_count > 1:
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#9CA3AF"))
            text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(A4[0] - 36, 20, text)
            self.drawString(36, 20, "CVCraft — Professional Resume")
            self.restoreState()


class PDFService:
    @staticmethod
    def get_palette_colors(palette_name: str) -> Dict[str, colors.Color]:
        pal = COLOR_PALETTES.get(palette_name, COLOR_PALETTES["Deep Indigo"])
        return {
            "primary": hex_to_rl_color(pal["primary"]),
            "secondary": hex_to_rl_color(pal["secondary"]),
            "accent": hex_to_rl_color(pal["accent"]),
            "badge": hex_to_rl_color(pal["badge"]),
            "badge_text": hex_to_rl_color(pal["badge_text"]),
            "dark": colors.HexColor("#111827"),
            "gray": colors.HexColor("#4B5563"),
            "light_gray": colors.HexColor("#9CA3AF"),
            "bg_subtle": colors.HexColor("#F9FAFB"),
            "border": colors.HexColor("#E5E7EB")
        }

    @staticmethod
    def prepare_photo(photo_path: str, style: str = "circle", size: int = 120) -> Optional[io.BytesIO]:
        if not photo_path or not os.path.exists(photo_path):
            return None
        try:
            im = PILImage.open(photo_path).convert("RGBA")
            # Square crop first
            min_dim = min(im.size)
            left = (im.width - min_dim) / 2
            top = (im.height - min_dim) / 2
            right = (im.width + min_dim) / 2
            bottom = (im.height + min_dim) / 2
            im = im.crop((left, top, right, bottom))
            im = im.resize((size, size), PILImage.Resampling.LANCZOS)

            if style == "circle":
                mask = PILImage.new('L', (size, size), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, size, size), fill=255)
                output = PILImage.new('RGBA', (size, size), (255, 255, 255, 0))
                output.paste(im, (0, 0), mask=mask)
                im = output
            elif style == "square":
                # Rounded corners for square
                mask = PILImage.new('L', (size, size), 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle((0, 0, size, size), radius=14, fill=255)
                output = PILImage.new('RGBA', (size, size), (255, 255, 255, 0))
                output.paste(im, (0, 0), mask=mask)
                im = output

            buf = io.BytesIO()
            im.save(buf, format="PNG")
            buf.seek(0)
            return buf
        except Exception:
            return None

    @classmethod
    def generate_pdf_bytes(cls, cv: CVDocument) -> bytes:
        """Generates standard A4 PDF document in memory and returns bytes."""
        buffer = io.BytesIO()
        template_id = cv.template_id or "modern"
        
        # Build according to selected template
        if template_id == "ats_friendly":
            cls._build_ats_friendly(buffer, cv)
        elif template_id == "minimal":
            cls._build_minimal(buffer, cv)
        elif template_id == "executive":
            cls._build_executive(buffer, cv)
        elif template_id == "developer":
            cls._build_developer(buffer, cv)
        elif template_id == "creative":
            cls._build_creative(buffer, cv)
        elif template_id == "academic":
            cls._build_academic(buffer, cv)
        elif template_id == "professional":
            cls._build_professional(buffer, cv)
        else: # "modern" or default
            cls._build_modern(buffer, cv)

        buffer.seek(0)
        return buffer.getvalue()

    @classmethod
    def export_pdf_file(cls, cv: CVDocument, destination_path: str) -> str:
        pdf_bytes = cls.generate_pdf_bytes(cv)
        with open(destination_path, "wb") as f:
            f.write(pdf_bytes)
        return destination_path

    @classmethod
    def render_pdf_to_images(cls, pdf_bytes: bytes, dpi: int = 150) -> List[PILImage.Image]:
        """Renders every page of the generated PDF into high-res PIL images for live preview."""
        images = []
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=dpi)
            img = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        doc.close()
        return images

    # =========================================================================
    # TEMPLATE 1: MODERN TECH (Two-Column Split Layout)
    # =========================================================================
    @classmethod
    def _build_modern(cls, buffer: io.BytesIO, cv: CVDocument):
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=30,
            rightMargin=30,
            topMargin=32,
            bottomMargin=32
        )
        pal = cls.get_palette_colors(cv.customization.accent_palette)
        font = cv.customization.font_family or "Helvetica"
        content_w = A4[0] - 60

        story = []
        
        # Header Table: Photo + Name/Title + Contact Info
        header_data = []
        photo_buf = cls.prepare_photo(cv.personal.profile_photo_path, cv.customization.photo_style, size=90)
        
        name_style = ParagraphStyle(
            'ModName',
            fontName=f"{font}-Bold" if font in ["Helvetica", "Times-Roman", "Courier"] else "Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=pal["primary"]
        )
        title_style = ParagraphStyle(
            'ModTitle',
            fontName=font,
            fontSize=11,
            leading=14,
            textColor=pal["gray"]
        )
        contact_style = ParagraphStyle(
            'ModContact',
            fontName=font,
            fontSize=8.5,
            leading=12,
            textColor=pal["dark"]
        )

        name_cell = [
            Paragraph(f"<b>{cv.personal.full_name or 'Your Name'}</b>", name_style),
            Spacer(1, 2),
            Paragraph(f"<b>{cv.personal.professional_title or 'Professional Title'}</b>", title_style)
        ]

        contacts = []
        if cv.personal.email: contacts.append(f"<b>Email:</b> {cv.personal.email}")
        if cv.personal.phone: contacts.append(f"<b>Phone:</b> {cv.personal.phone}")
        if cv.personal.location: contacts.append(f"<b>Location:</b> {cv.personal.location}")
        if cv.personal.linkedin: contacts.append(f"<b>LinkedIn:</b> {cv.personal.linkedin}")
        if cv.personal.github: contacts.append(f"<b>GitHub:</b> {cv.personal.github}")
        if cv.personal.website: contacts.append(f"<b>Web:</b> {cv.personal.website}")

        contact_p = Paragraph(" • ".join(contacts), contact_style)

        if photo_buf and cv.customization.show_photo:
            rl_img = RLImage(photo_buf, width=65, height=65)
            header_table = Table([[rl_img, [name_cell, Spacer(1, 4), contact_p]]], colWidths=[75, content_w - 75])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (1,0), (1,0), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ]))
        else:
            header_table = Table([[[name_cell, Spacer(1, 4), contact_p]]], colWidths=[content_w])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ]))

        story.append(header_table)
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=pal["primary"], spaceAfter=10))

        # Main Body: Split Column (Left: Skills, Education, Certs, Languages) (Right: Summary, Experience, Projects)
        left_w = content_w * 0.35
        right_w = content_w * 0.65 - 12

        left_story = []
        right_story = []

        # Styles
        sec_h2 = ParagraphStyle('SecH2', fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=pal["primary"], spaceAfter=4)
        body_p = ParagraphStyle('BodyP', fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=pal["dark"])
        item_h = ParagraphStyle('ItemH', fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=pal["dark"])
        item_sub = ParagraphStyle('ItemSub', fontName="Helvetica", fontSize=8, leading=10, textColor=pal["gray"])
        badge_p = ParagraphStyle('BadgeP', fontName="Helvetica-Bold", fontSize=7.5, leading=9, textColor=pal["badge_text"])

        # RIGHT COLUMN: Summary, Experience, Projects, Achievements
        if cv.summary:
            right_story.append(Paragraph("PROFESSIONAL SUMMARY", sec_h2))
            right_story.append(Paragraph(cv.summary, body_p))
            right_story.append(Spacer(1, 10))

        if cv.experience:
            right_story.append(Paragraph("WORK EXPERIENCE", sec_h2))
            for exp in cv.experience:
                date_str = f"{exp.start_date} – {exp.end_date or ('Current' if exp.is_current else '')}"
                right_story.append(Paragraph(f"<b>{exp.job_title}</b>", item_h))
                right_story.append(Paragraph(f"<i>{exp.company}</i> | {exp.location} | {date_str}", item_sub))
                if exp.responsibilities:
                    lines = exp.responsibilities.replace('\n', '<br/>')
                    right_story.append(Paragraph(lines, body_p))
                if exp.achievements:
                    right_story.append(Paragraph(f"<b>Key Achievement:</b> {exp.achievements}", body_p))
                right_story.append(Spacer(1, 6))
            right_story.append(Spacer(1, 4))

        if cv.projects:
            right_story.append(Paragraph("KEY PROJECTS", sec_h2))
            for proj in cv.projects:
                urls = []
                if proj.github_url: urls.append(f"<a href='{proj.github_url}' color='{pal['accent'].hexval()}'>GitHub</a>")
                if proj.live_demo_url: urls.append(f"<a href='{proj.live_demo_url}' color='{pal['accent'].hexval()}'>Live Demo</a>")
                link_str = f" ({' | '.join(urls)})" if urls else ""
                right_story.append(Paragraph(f"<b>{proj.name}</b> {link_str}", item_h))
                if proj.technologies:
                    right_story.append(Paragraph(f"<b>Tech:</b> {proj.technologies}", item_sub))
                if proj.description:
                    right_story.append(Paragraph(proj.description, body_p))
                right_story.append(Spacer(1, 5))
            right_story.append(Spacer(1, 4))

        # LEFT COLUMN: Skills, Education, Certifications, Languages, Volunteer
        if cv.skills:
            left_story.append(Paragraph("SKILLS & EXPERTISE", sec_h2))
            skills_by_cat = {}
            for s in cv.skills:
                skills_by_cat.setdefault(s.category, []).append(s)
            
            for cat, items in skills_by_cat.items():
                left_story.append(Paragraph(f"<b>{cat}</b>", item_sub))
                skill_names = [f"• {item.name}" for item in items]
                left_story.append(Paragraph("<br/>".join(skill_names), body_p))
                left_story.append(Spacer(1, 4))
            left_story.append(Spacer(1, 6))

        if cv.education:
            left_story.append(Paragraph("EDUCATION", sec_h2))
            for edu in cv.education:
                left_story.append(Paragraph(f"<b>{edu.degree}</b>", item_h))
                left_story.append(Paragraph(f"{edu.institution}", item_sub))
                date_str = f"{edu.start_date} – {edu.end_date}" if edu.start_date or edu.end_date else ""
                if date_str or edu.grade:
                    left_story.append(Paragraph(f"{date_str} {('• ' + edu.grade) if edu.grade else ''}", item_sub))
                if edu.description:
                    left_story.append(Paragraph(edu.description, body_p))
                left_story.append(Spacer(1, 5))
            left_story.append(Spacer(1, 6))

        if cv.certifications:
            left_story.append(Paragraph("CERTIFICATIONS", sec_h2))
            for cert in cv.certifications:
                left_story.append(Paragraph(f"<b>{cert.name}</b>", item_h))
                left_story.append(Paragraph(f"{cert.issuer} ({cert.issue_date})", item_sub))
                left_story.append(Spacer(1, 4))
            left_story.append(Spacer(1, 6))

        if cv.languages:
            left_story.append(Paragraph("LANGUAGES", sec_h2))
            lang_strs = [f"• <b>{l.name}</b> ({l.proficiency})" for l in cv.languages]
            left_story.append(Paragraph("<br/>".join(lang_strs), body_p))
            left_story.append(Spacer(1, 6))

        if cv.achievements:
            left_story.append(Paragraph("ACHIEVEMENTS", sec_h2))
            for ach in cv.achievements:
                left_story.append(Paragraph(f"<b>{ach.title}</b>", item_h))
                if ach.description:
                    left_story.append(Paragraph(ach.description, body_p))
                left_story.append(Spacer(1, 4))

        if cv.references_on_request:
            right_story.append(Paragraph("REFERENCES", sec_h2))
            right_story.append(Paragraph("Professional references available upon request.", body_p))
        elif cv.references:
            right_story.append(Paragraph("REFERENCES", sec_h2))
            for ref in cv.references:
                right_story.append(Paragraph(f"<b>{ref.name}</b> — {ref.job_title}, {ref.company}", item_h))
                right_story.append(Paragraph(f"{ref.email} | {ref.phone}", item_sub))
                right_story.append(Spacer(1, 3))

        # Pack into Table with 2 columns
        main_layout_table = Table([[left_story, right_story]], colWidths=[left_w, right_w])
        main_layout_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (0,0), 0),
            ('RIGHTPADDING', (0,0), (0,0), 10),
            ('LEFTPADDING', (1,0), (1,0), 10),
            ('RIGHTPADDING', (1,0), (1,0), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('LINEAFTER', (0,0), (0,0), 0.75, pal["border"]),
        ]))
        story.append(main_layout_table)

        doc.build(story, canvasmaker=NumberedCanvas)

    # =========================================================================
    # TEMPLATE 2: MINIMALIST CLEAN (Refined single-column, elegant spacing)
    # =========================================================================
    @classmethod
    def _build_minimal(cls, buffer: io.BytesIO, cv: CVDocument):
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        pal = cls.get_palette_colors(cv.customization.accent_palette)
        content_w = A4[0] - 72

        h1 = ParagraphStyle('MinH1', fontName="Helvetica", fontSize=24, leading=28, textColor=colors.HexColor("#111827"), alignment=1)
        sub1 = ParagraphStyle('MinSub', fontName="Helvetica", fontSize=11, leading=14, textColor=pal["primary"], alignment=1)
        contact = ParagraphStyle('MinContact', fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#6B7280"), alignment=1)
        sec_h = ParagraphStyle('MinSec', fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=colors.HexColor("#111827"), spaceBefore=10, spaceAfter=4)
        body = ParagraphStyle('MinBody', fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#374151"))
        item_title = ParagraphStyle('MinItemT', fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=colors.HexColor("#111827"))
        item_sub = ParagraphStyle('MinItemSub', fontName="Helvetica", fontSize=8, leading=10, textColor=colors.HexColor("#6B7280"))

        story = []
        story.append(Paragraph(cv.personal.full_name.upper(), h1))
        if cv.personal.professional_title:
            story.append(Spacer(1, 2))
            story.append(Paragraph(cv.personal.professional_title, sub1))

        contacts = [c for c in [cv.personal.email, cv.personal.phone, cv.personal.location, cv.personal.linkedin, cv.personal.github, cv.personal.website] if c]
        if contacts:
            story.append(Spacer(1, 4))
            story.append(Paragraph(" • ".join(contacts), contact))

        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D1D5DB"), spaceAfter=10))

        if cv.summary:
            story.append(Paragraph("ABOUT", sec_h))
            story.append(Paragraph(cv.summary, body))
            story.append(Spacer(1, 8))

        if cv.experience:
            story.append(Paragraph("EXPERIENCE", sec_h))
            for exp in cv.experience:
                date_str = f"{exp.start_date} – {exp.end_date or ('Current' if exp.is_current else '')}"
                t_row = Table([[
                    Paragraph(f"<b>{exp.job_title}</b>, {exp.company}", item_title),
                    Paragraph(f"{exp.location} | {date_str}", item_sub)
                ]], colWidths=[content_w*0.65, content_w*0.35])
                t_row.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'RIGHT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
                story.append(t_row)
                if exp.responsibilities:
                    story.append(Paragraph(exp.responsibilities.replace('\n', '<br/>'), body))
                if exp.achievements:
                    story.append(Paragraph(f"<i>Achievement:</i> {exp.achievements}", body))
                story.append(Spacer(1, 6))

        if cv.education:
            story.append(Paragraph("EDUCATION", sec_h))
            for edu in cv.education:
                date_str = f"{edu.start_date} – {edu.end_date}" if edu.start_date or edu.end_date else ""
                t_row = Table([[
                    Paragraph(f"<b>{edu.degree}</b> in {edu.field_of_study}, {edu.institution}", item_title),
                    Paragraph(f"{date_str} {edu.grade}", item_sub)
                ]], colWidths=[content_w*0.7, content_w*0.3])
                t_row.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'RIGHT'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
                story.append(t_row)
                if edu.description:
                    story.append(Paragraph(edu.description, body))
                story.append(Spacer(1, 4))

        if cv.skills:
            story.append(Paragraph("SKILLS", sec_h))
            skills_str = ", ".join([f"<b>{s.name}</b>" for s in cv.skills])
            story.append(Paragraph(skills_str, body))
            story.append(Spacer(1, 6))

        if cv.projects:
            story.append(Paragraph("PROJECTS", sec_h))
            for p in cv.projects:
                story.append(Paragraph(f"<b>{p.name}</b> — <i>{p.technologies}</i>", item_title))
                if p.description:
                    story.append(Paragraph(p.description, body))
                story.append(Spacer(1, 4))

        doc.build(story, canvasmaker=NumberedCanvas)

    # =========================================================================
    # TEMPLATE 3: EXECUTIVE LEADERSHIP (Dark header banner, prestige look)
    # =========================================================================
    @classmethod
    def _build_executive(cls, buffer: io.BytesIO, cv: CVDocument):
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=32, rightMargin=32, topMargin=28, bottomMargin=28)
        pal = cls.get_palette_colors(cv.customization.accent_palette)
        content_w = A4[0] - 64

        h1 = ParagraphStyle('ExecH1', fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=colors.white)
        sub1 = ParagraphStyle('ExecSub', fontName="Helvetica", fontSize=11, leading=14, textColor=pal["badge"])
        contact = ParagraphStyle('ExecContact', fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#F3F4F6"))

        banner_content = [
            Paragraph(cv.personal.full_name.upper(), h1),
            Spacer(1, 2),
            Paragraph(cv.personal.professional_title, sub1),
            Spacer(1, 4),
            Paragraph(" • ".join([c for c in [cv.personal.email, cv.personal.phone, cv.personal.location, cv.personal.linkedin] if c]), contact)
        ]

        banner_table = Table([[banner_content]], colWidths=[content_w])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), pal["primary"]),
            ('LEFTPADDING', (0,0), (-1,-1), 16),
            ('RIGHTPADDING', (0,0), (-1,-1), 16),
            ('TOPPADDING', (0,0), (-1,-1), 14),
            ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ]))

        story = [banner_table, Spacer(1, 14)]
        sec_h = ParagraphStyle('ExecSec', fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=pal["primary"], spaceAfter=4)
        body = ParagraphStyle('ExecBody', fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#1F2937"))
        item_h = ParagraphStyle('ExecItemH', fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=colors.HexColor("#111827"))
        item_sub = ParagraphStyle('ExecItemSub', fontName="Helvetica", fontSize=8, leading=10, textColor=pal["gray"])

        if cv.summary:
            story.append(Paragraph("EXECUTIVE PROFILE", sec_h))
            story.append(Paragraph(cv.summary, body))
            story.append(Spacer(1, 8))

        if cv.experience:
            story.append(Paragraph("KEY LEADERSHIP & PROFESSIONAL EXPERIENCE", sec_h))
            for exp in cv.experience:
                date_str = f"{exp.start_date} – {exp.end_date or ('Current' if exp.is_current else '')}"
                t_row = Table([[
                    Paragraph(f"<b>{exp.job_title}</b> | {exp.company}", item_h),
                    Paragraph(f"{exp.location} • {date_str}", item_sub)
                ]], colWidths=[content_w*0.7, content_w*0.3])
                t_row.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'RIGHT'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
                story.append(t_row)
                if exp.responsibilities:
                    story.append(Paragraph(exp.responsibilities.replace('\n', '<br/>'), body))
                if exp.achievements:
                    story.append(Paragraph(f"<b>Key Deliverable:</b> {exp.achievements}", body))
                story.append(Spacer(1, 6))

        if cv.skills:
            story.append(Paragraph("CORE COMPETENCIES", sec_h))
            skills_str = " | ".join([f"<b>{s.name}</b>" for s in cv.skills])
            story.append(Paragraph(skills_str, body))
            story.append(Spacer(1, 8))

        if cv.education:
            story.append(Paragraph("EDUCATION & CREDENTIALS", sec_h))
            for edu in cv.education:
                story.append(Paragraph(f"<b>{edu.degree}</b> — {edu.institution} ({edu.start_date} – {edu.end_date})", item_h))
            story.append(Spacer(1, 6))

        doc.build(story, canvasmaker=NumberedCanvas)

    # =========================================================================
    # TEMPLATE 4: DEVELOPER (Terminal/Tech badges & GitHub links)
    # =========================================================================
    @classmethod
    def _build_developer(cls, buffer: io.BytesIO, cv: CVDocument):
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=32, rightMargin=32, topMargin=30, bottomMargin=30)
        pal = cls.get_palette_colors(cv.customization.accent_palette)
        content_w = A4[0] - 64

        h1 = ParagraphStyle('DevH1', fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=pal["primary"])
        sub1 = ParagraphStyle('DevSub', fontName="Courier-Bold", fontSize=10, leading=13, textColor=colors.HexColor("#059669"))
        contact = ParagraphStyle('DevContact', fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#4B5563"))
        sec_h = ParagraphStyle('DevSec', fontName="Courier-Bold", fontSize=11, leading=14, textColor=pal["primary"], spaceAfter=4)
        body = ParagraphStyle('DevBody', fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=colors.HexColor("#1F2937"))
        code_p = ParagraphStyle('DevCode', fontName="Courier", fontSize=8, leading=10, textColor=pal["dark"])

        story = []
        story.append(Paragraph(cv.personal.full_name, h1))
        story.append(Paragraph(f"// {cv.personal.professional_title}", sub1))
        contacts = [c for c in [cv.personal.email, cv.personal.phone, cv.personal.location, cv.personal.github, cv.personal.linkedin, cv.personal.website] if c]
        story.append(Paragraph(" • ".join(contacts), contact))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1, color=pal["primary"], spaceAfter=8))

        if cv.summary:
            story.append(Paragraph("$ cat summary.txt", sec_h))
            story.append(Paragraph(cv.summary, body))
            story.append(Spacer(1, 6))

        if cv.skills:
            story.append(Paragraph("$ stack --list-skills", sec_h))
            tech_skills = [s.name for s in cv.skills]
            story.append(Paragraph(" <b>[</b> " + " • ".join(tech_skills) + " <b>]</b>", code_p))
            story.append(Spacer(1, 8))

        if cv.experience:
            story.append(Paragraph("$ git log --experience", sec_h))
            for exp in cv.experience:
                date_str = f"{exp.start_date} – {exp.end_date or ('Current' if exp.is_current else '')}"
                story.append(Paragraph(f"<b>commit: {exp.job_title}</b> @ {exp.company} ({date_str})", ParagraphStyle('DevExpT', fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=pal["primary"])))
                if exp.responsibilities:
                    story.append(Paragraph(exp.responsibilities.replace('\n', '<br/>'), body))
                if exp.achievements:
                    story.append(Paragraph(f"<b>Key Metric:</b> {exp.achievements}", body))
                story.append(Spacer(1, 6))

        if cv.projects:
            story.append(Paragraph("$ repo --featured-projects", sec_h))
            for p in cv.projects:
                story.append(Paragraph(f"<b>{p.name}</b> [ {p.technologies} ]", ParagraphStyle('DevPrjH', fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=pal["dark"])))
                if p.github_url or p.live_demo_url:
                    urls = [u for u in [p.github_url, p.live_demo_url] if u]
                    story.append(Paragraph(" | ".join(urls), code_p))
                if p.description:
                    story.append(Paragraph(p.description, body))
                story.append(Spacer(1, 5))

        if cv.education:
            story.append(Paragraph("$ cat education.log", sec_h))
            for edu in cv.education:
                story.append(Paragraph(f"<b>{edu.degree}</b> — {edu.institution} ({edu.start_date} – {edu.end_date})", body))
            story.append(Spacer(1, 6))

        doc.build(story, canvasmaker=NumberedCanvas)

    # =========================================================================
    # TEMPLATE 5: ATS-FRIENDLY (Standardized headings, 100% linear, zero parsing errors)
    # =========================================================================
    @classmethod
    def _build_ats_friendly(cls, buffer: io.BytesIO, cv: CVDocument):
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
        
        # Strictly high contrast standard colors for ATS scanners
        black = colors.HexColor("#000000")
        gray = colors.HexColor("#333333")

        h1 = ParagraphStyle('ATSH1', fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=black, alignment=1)
        sub1 = ParagraphStyle('ATSSub', fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=gray, alignment=1)
        contact = ParagraphStyle('ATSContact', fontName="Helvetica", fontSize=9, leading=12, textColor=black, alignment=1)
        sec_h = ParagraphStyle('ATSSec', fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=black, spaceBefore=8, spaceAfter=2)
        body = ParagraphStyle('ATSBody', fontName="Helvetica", fontSize=9, leading=12, textColor=black)
        item_h = ParagraphStyle('ATSItem', fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=black)

        story = []
        story.append(Paragraph(cv.personal.full_name.upper(), h1))
        if cv.personal.professional_title:
            story.append(Paragraph(cv.personal.professional_title, sub1))
        
        contacts = [c for c in [cv.personal.email, cv.personal.phone, cv.personal.location, cv.personal.linkedin, cv.personal.github, cv.personal.website] if c]
        story.append(Paragraph(" | ".join(contacts), contact))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1, color=black, spaceAfter=8))

        if cv.summary:
            story.append(Paragraph("PROFESSIONAL SUMMARY", sec_h))
            story.append(Paragraph(cv.summary, body))
            story.append(Spacer(1, 6))

        if cv.skills:
            story.append(Paragraph("CORE SKILLS", sec_h))
            skills_text = ", ".join([s.name for s in cv.skills])
            story.append(Paragraph(skills_text, body))
            story.append(Spacer(1, 6))

        if cv.experience:
            story.append(Paragraph("WORK EXPERIENCE", sec_h))
            for exp in cv.experience:
                date_str = f"{exp.start_date} - {exp.end_date or ('Present' if exp.is_current else '')}"
                story.append(Paragraph(f"{exp.job_title} | {exp.company} | {exp.location} | {date_str}", item_h))
                if exp.responsibilities:
                    story.append(Paragraph(exp.responsibilities.replace('\n', '<br/>'), body))
                if exp.achievements:
                    story.append(Paragraph(f"Key Achievements: {exp.achievements}", body))
                story.append(Spacer(1, 5))

        if cv.education:
            story.append(Paragraph("EDUCATION", sec_h))
            for edu in cv.education:
                date_str = f"{edu.start_date} - {edu.end_date}" if edu.start_date or edu.end_date else ""
                story.append(Paragraph(f"{edu.degree}, {edu.field_of_study} - {edu.institution} ({date_str}) {edu.grade}", item_h))
                if edu.description:
                    story.append(Paragraph(edu.description, body))
                story.append(Spacer(1, 4))

        if cv.certifications:
            story.append(Paragraph("CERTIFICATIONS", sec_h))
            for cert in cv.certifications:
                story.append(Paragraph(f"{cert.name} - {cert.issuer} ({cert.issue_date})", body))
            story.append(Spacer(1, 4))

        doc.build(story, canvasmaker=NumberedCanvas)

    # =========================================================================
    # TEMPLATE 6: CREATIVE DESIGNER (Bold color block accents & creative pills)
    # =========================================================================
    @classmethod
    def _build_creative(cls, buffer: io.BytesIO, cv: CVDocument):
        # Build creative layout with vibrant accents
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=32, rightMargin=32, topMargin=28, bottomMargin=28)
        pal = cls.get_palette_colors(cv.customization.accent_palette)
        content_w = A4[0] - 64

        h1 = ParagraphStyle('CrtH1', fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=pal["primary"])
        sub1 = ParagraphStyle('CrtSub', fontName="Helvetica", fontSize=11, leading=14, textColor=pal["accent"])
        sec_h = ParagraphStyle('CrtSec', fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=pal["primary"], spaceAfter=4)
        body = ParagraphStyle('CrtBody', fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#1F2937"))

        story = [
            Paragraph(cv.personal.full_name, h1),
            Paragraph(cv.personal.professional_title, sub1),
            Spacer(1, 4),
            Paragraph(" • ".join([c for c in [cv.personal.email, cv.personal.phone, cv.personal.location, cv.personal.portfolio, cv.personal.linkedin] if c]), body),
            Spacer(1, 8),
            HRFlowable(width="100%", thickness=3, color=pal["accent"], spaceAfter=10)
        ]

        if cv.summary:
            story.append(Paragraph("CREATIVE PROFILE", sec_h))
            story.append(Paragraph(cv.summary, body))
            story.append(Spacer(1, 8))

        if cv.projects:
            story.append(Paragraph("SELECTED PORTFOLIO & PROJECTS", sec_h))
            for p in cv.projects:
                story.append(Paragraph(f"<b>{p.name}</b> — {p.technologies}", ParagraphStyle('PjT', fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=pal["primary"])))
                if p.description:
                    story.append(Paragraph(p.description, body))
                story.append(Spacer(1, 5))

        if cv.experience:
            story.append(Paragraph("PROFESSIONAL JOURNEY", sec_h))
            for exp in cv.experience:
                story.append(Paragraph(f"<b>{exp.job_title}</b> @ {exp.company}", ParagraphStyle('EpT', fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=colors.HexColor("#111827"))))
                if exp.responsibilities:
                    story.append(Paragraph(exp.responsibilities.replace('\n', '<br/>'), body))
                story.append(Spacer(1, 5))

        if cv.skills:
            story.append(Paragraph("CREATIVE TOOLKIT & SKILLS", sec_h))
            story.append(Paragraph(" • ".join([f"<b>{s.name}</b>" for s in cv.skills]), body))
            story.append(Spacer(1, 8))

        if cv.education:
            story.append(Paragraph("EDUCATION", sec_h))
            for edu in cv.education:
                story.append(Paragraph(f"<b>{edu.degree}</b> — {edu.institution}", body))

        doc.build(story, canvasmaker=NumberedCanvas)

    # =========================================================================
    # TEMPLATE 7: ACADEMIC & RESEARCH (Strict single column, detailed hierarchy)
    # =========================================================================
    @classmethod
    def _build_academic(cls, buffer: io.BytesIO, cv: CVDocument):
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        content_w = A4[0] - 72

        h1 = ParagraphStyle('AcdH1', fontName="Times-Bold", fontSize=20, leading=24, textColor=colors.black, alignment=1)
        sub1 = ParagraphStyle('AcdSub', fontName="Times-Roman", fontSize=11, leading=14, textColor=colors.HexColor("#333333"), alignment=1)
        sec_h = ParagraphStyle('AcdSec', fontName="Times-Bold", fontSize=11, leading=14, textColor=colors.black, spaceBefore=8, spaceAfter=3)
        body = ParagraphStyle('AcdBody', fontName="Times-Roman", fontSize=9, leading=13, textColor=colors.black)

        story = [
            Paragraph(cv.personal.full_name, h1),
            Paragraph(cv.personal.professional_title, sub1),
            Spacer(1, 3),
            Paragraph(" • ".join([c for c in [cv.personal.email, cv.personal.phone, cv.personal.location, cv.personal.website] if c]), sub1),
            Spacer(1, 6),
            HRFlowable(width="100%", thickness=0.8, color=colors.black, spaceAfter=8)
        ]

        if cv.education:
            story.append(Paragraph("EDUCATION", sec_h))
            for edu in cv.education:
                date_str = f"{edu.start_date} – {edu.end_date}" if edu.start_date or edu.end_date else ""
                story.append(Paragraph(f"<b>{edu.degree}</b>, {edu.field_of_study}, {edu.institution} ({date_str})", body))
                if edu.grade or edu.description:
                    story.append(Paragraph(f"{edu.grade} • {edu.description}", body))
                story.append(Spacer(1, 4))

        if cv.experience:
            story.append(Paragraph("ACADEMIC & RESEARCH APPOINTMENTS", sec_h))
            for exp in cv.experience:
                story.append(Paragraph(f"<b>{exp.job_title}</b>, {exp.company} ({exp.start_date} – {exp.end_date})", body))
                if exp.responsibilities:
                    story.append(Paragraph(exp.responsibilities.replace('\n', '<br/>'), body))
                story.append(Spacer(1, 4))

        if cv.achievements:
            story.append(Paragraph("HONORS & AWARDS", sec_h))
            for ach in cv.achievements:
                story.append(Paragraph(f"<b>{ach.title}</b> ({ach.date}): {ach.description}", body))
                story.append(Spacer(1, 3))

        if cv.skills:
            story.append(Paragraph("RESEARCH METHODOLOGIES & SKILLS", sec_h))
            story.append(Paragraph(", ".join([s.name for s in cv.skills]), body))

        doc.build(story, canvasmaker=NumberedCanvas)

    # =========================================================================
    # TEMPLATE 8: CORPORATE PROFESSIONAL (Clean structured corporate 2-column)
    # =========================================================================
    @classmethod
    def _build_professional(cls, buffer: io.BytesIO, cv: CVDocument):
        cls._build_modern(buffer, cv)
