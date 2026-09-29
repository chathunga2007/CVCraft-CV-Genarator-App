"""
CVCraft PDF Service
Production-grade multi-page A4 PDF rendering with 8 distinct template layouts,
exact styling, color palettes, custom section rendering, and real-time page rendering via PyMuPDF.
"""

import io
import os
import html
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

def xml_escape(text: Optional[str]) -> str:
    """Escapes user input string so ReportLab Paragraph XML parser will never crash on &, <, >, etc."""
    if not text:
        return ""
    return html.escape(str(text), quote=False)

def xml_multiline(text: Optional[str]) -> str:
    """Safely escapes text and replaces newlines with <br/> for ReportLab."""
    if not text:
        return ""
    escaped = html.escape(str(text), quote=False)
    return escaped.replace("\n", "<br/>")

def get_font_names(family_name: Optional[str]) -> Tuple[str, str, str]:
    """Returns (regular, bold, italic) ReportLab core font names."""
    family = (family_name or "Helvetica").strip().lower()
    if "times" in family or "serif" in family:
        return ("Times-Roman", "Times-Bold", "Times-Italic")
    elif "courier" in family or "mono" in family:
        return ("Courier", "Courier-Bold", "Courier-Oblique")
    else:
        return ("Helvetica", "Helvetica-Bold", "Helvetica-Oblique")


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
            self.drawRightString(A4[0] - 36, 18, text)
            self.drawString(36, 18, "CVCraft — Professional Resume")
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
            topMargin=30,
            bottomMargin=30
        )
        pal = cls.get_palette_colors(cv.customization.accent_palette)
        f_reg, f_bold, f_italic = get_font_names(cv.customization.font_family)
        content_w = A4[0] - 60

        story = []
        full_name = (cv.personal.full_name or "Your Name").strip() or "Your Name"
        pro_title = (cv.personal.professional_title or "Professional Title").strip()

        # Header Styles
        name_style = ParagraphStyle('ModName', fontName=f_bold, fontSize=22, leading=26, textColor=pal["primary"])
        title_style = ParagraphStyle('ModTitle', fontName=f_reg, fontSize=11, leading=14, textColor=pal["gray"])
        contact_style = ParagraphStyle('ModContact', fontName=f_reg, fontSize=8.5, leading=12, textColor=pal["dark"])

        name_cell = [
            Paragraph(f"<b>{xml_escape(full_name)}</b>", name_style),
            Spacer(1, 2),
            Paragraph(f"<b>{xml_escape(pro_title)}</b>", title_style)
        ]

        contacts = []
        if cv.personal.email: contacts.append(f"<b>Email:</b> {xml_escape(cv.personal.email)}")
        if cv.personal.phone: contacts.append(f"<b>Phone:</b> {xml_escape(cv.personal.phone)}")
        if cv.personal.location: contacts.append(f"<b>Location:</b> {xml_escape(cv.personal.location)}")
        if cv.personal.linkedin: contacts.append(f"<b>LinkedIn:</b> {xml_escape(cv.personal.linkedin)}")
        if cv.personal.github: contacts.append(f"<b>GitHub:</b> {xml_escape(cv.personal.github)}")
        if cv.personal.website: contacts.append(f"<b>Web:</b> {xml_escape(cv.personal.website)}")

        contact_p = Paragraph(" • ".join(contacts), contact_style)

        photo_buf = None
        if cv.customization.show_photo and cv.customization.photo_style != "none":
            photo_buf = cls.prepare_photo(cv.personal.profile_photo_path, cv.customization.photo_style, size=90)

        if photo_buf:
            rl_img = RLImage(photo_buf, width=65, height=65)
            header_table = Table([[rl_img, [name_cell, Spacer(1, 4), contact_p]]], colWidths=[75, content_w - 75])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (1,0), (1,0), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(header_table)
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

        # Main Body: Split Column (Left 35% Skills/Edu/Certs) (Right 65% Exp/Projects/Summary)
        left_w = content_w * 0.35
        right_w = content_w * 0.65 - 12
        left_story = []
        right_story = []

        sec_h2 = ParagraphStyle('SecH2', fontName=f_bold, fontSize=10.5, leading=13, textColor=pal["primary"], spaceAfter=4)
        body_p = ParagraphStyle('BodyP', fontName=f_reg, fontSize=8.5, leading=11.5, textColor=pal["dark"])
        item_h = ParagraphStyle('ItemH', fontName=f_bold, fontSize=9, leading=11, textColor=pal["dark"])
        item_sub = ParagraphStyle('ItemSub', fontName=f_reg, fontSize=8, leading=10, textColor=pal["gray"])

        # RIGHT COLUMN: Summary, Experience, Projects, Achievements, Volunteer, References
        if cv.summary:
            right_story.append(Paragraph("PROFESSIONAL SUMMARY", sec_h2))
            right_story.append(Paragraph(xml_multiline(cv.summary), body_p))
            right_story.append(Spacer(1, 10))

        if cv.experience:
            right_story.append(Paragraph("WORK EXPERIENCE", sec_h2))
            for exp in cv.experience:
                date_str = f"{xml_escape(exp.start_date)} – {xml_escape(exp.end_date) or ('Current' if exp.is_current else '')}"
                right_story.append(Paragraph(f"<b>{xml_escape(exp.job_title)}</b>", item_h))
                right_story.append(Paragraph(f"<i>{xml_escape(exp.company)}</i> | {xml_escape(exp.location)} | {date_str}", item_sub))
                if exp.responsibilities:
                    right_story.append(Paragraph(xml_multiline(exp.responsibilities), body_p))
                if exp.achievements:
                    right_story.append(Paragraph(f"<b>Key Achievement:</b> {xml_escape(exp.achievements)}", body_p))
                right_story.append(Spacer(1, 6))
            right_story.append(Spacer(1, 4))

        if cv.projects:
            right_story.append(Paragraph("KEY PROJECTS", sec_h2))
            for proj in cv.projects:
                urls = []
                if proj.github_url: urls.append(f"<a href='{proj.github_url}' color='{pal['accent'].hexval()}'>GitHub</a>")
                if proj.live_demo_url: urls.append(f"<a href='{proj.live_demo_url}' color='{pal['accent'].hexval()}'>Live Demo</a>")
                link_str = f" ({' | '.join(urls)})" if urls else ""
                right_story.append(Paragraph(f"<b>{xml_escape(proj.name)}</b> {link_str}", item_h))
                if proj.technologies:
                    right_story.append(Paragraph(f"<b>Tech:</b> {xml_escape(proj.technologies)}", item_sub))
                if proj.description:
                    right_story.append(Paragraph(xml_multiline(proj.description), body_p))
                right_story.append(Spacer(1, 5))
            right_story.append(Spacer(1, 4))

        if cv.volunteer:
            right_story.append(Paragraph("VOLUNTEER & LEADERSHIP", sec_h2))
            for v in cv.volunteer:
                d_str = f" ({xml_escape(v.start_date)} – {xml_escape(v.end_date)})" if v.start_date or v.end_date else ""
                right_story.append(Paragraph(f"<b>{xml_escape(v.role)}</b> — {xml_escape(v.organization)}{d_str}", item_h))
                if v.description:
                    right_story.append(Paragraph(xml_multiline(v.description), body_p))
                right_story.append(Spacer(1, 4))
            right_story.append(Spacer(1, 4))

        # References
        if cv.references_on_request:
            right_story.append(Paragraph("REFERENCES", sec_h2))
            right_story.append(Paragraph("Professional references available upon request.", body_p))
        elif cv.references:
            right_story.append(Paragraph("REFERENCES", sec_h2))
            for ref in cv.references:
                right_story.append(Paragraph(f"<b>{xml_escape(ref.name)}</b> — {xml_escape(ref.job_title)}, {xml_escape(ref.company)}", item_h))
                right_story.append(Paragraph(f"{xml_escape(ref.email)} | {xml_escape(ref.phone)}", item_sub))
                right_story.append(Spacer(1, 3))

        # LEFT COLUMN: Skills, Education, Certifications, Languages, Achievements, Custom Sections
        if cv.skills:
            left_story.append(Paragraph("SKILLS & EXPERTISE", sec_h2))
            skills_by_cat = {}
            for s in cv.skills:
                skills_by_cat.setdefault(s.category, []).append(s)
            for cat, items in skills_by_cat.items():
                left_story.append(Paragraph(f"<b>{xml_escape(cat)}</b>", item_sub))
                skill_names = [f"• {xml_escape(item.name)}" for item in items]
                left_story.append(Paragraph("<br/>".join(skill_names), body_p))
                left_story.append(Spacer(1, 4))
            left_story.append(Spacer(1, 6))

        if cv.education:
            left_story.append(Paragraph("EDUCATION", sec_h2))
            for edu in cv.education:
                left_story.append(Paragraph(f"<b>{xml_escape(edu.degree)}</b>", item_h))
                left_story.append(Paragraph(f"{xml_escape(edu.institution)}", item_sub))
                date_str = f"{xml_escape(edu.start_date)} – {xml_escape(edu.end_date)}" if edu.start_date or edu.end_date else ""
                if date_str or edu.grade:
                    left_story.append(Paragraph(f"{date_str} {('• ' + xml_escape(edu.grade)) if edu.grade else ''}", item_sub))
                if edu.description:
                    left_story.append(Paragraph(xml_multiline(edu.description), body_p))
                left_story.append(Spacer(1, 5))
            left_story.append(Spacer(1, 6))

        if cv.certifications:
            left_story.append(Paragraph("CERTIFICATIONS", sec_h2))
            for cert in cv.certifications:
                left_story.append(Paragraph(f"<b>{xml_escape(cert.name)}</b>", item_h))
                left_story.append(Paragraph(f"{xml_escape(cert.issuer)} ({xml_escape(cert.issue_date)})", item_sub))
                left_story.append(Spacer(1, 4))
            left_story.append(Spacer(1, 6))

        if cv.languages:
            left_story.append(Paragraph("LANGUAGES", sec_h2))
            lang_strs = [f"• <b>{xml_escape(l.name)}</b> ({xml_escape(l.proficiency)})" for l in cv.languages]
            left_story.append(Paragraph("<br/>".join(lang_strs), body_p))
            left_story.append(Spacer(1, 6))

        if cv.achievements:
            left_story.append(Paragraph("HONORS & AWARDS", sec_h2))
            for ach in cv.achievements:
                left_story.append(Paragraph(f"<b>{xml_escape(ach.title)}</b>", item_h))
                if ach.description:
                    left_story.append(Paragraph(xml_multiline(ach.description), body_p))
                left_story.append(Spacer(1, 4))
            left_story.append(Spacer(1, 6))

        if cv.custom_sections:
            for csec in cv.custom_sections:
                if csec.title:
                    left_story.append(Paragraph(xml_escape(csec.title.upper()), sec_h2))
                    for itm in csec.items:
                        t_str = xml_escape(itm.title)
                        if itm.subtitle: t_str += f" — {xml_escape(itm.subtitle)}"
                        left_story.append(Paragraph(f"<b>{t_str}</b>", item_h))
                        if itm.description:
                            left_story.append(Paragraph(xml_multiline(itm.description), body_p))
                        left_story.append(Spacer(1, 3))
                    left_story.append(Spacer(1, 5))

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
    # TEMPLATE 2: MINIMALIST CLEAN (Refined single-column, Swiss typography)
    # =========================================================================
    @classmethod
    def _build_minimal(cls, buffer: io.BytesIO, cv: CVDocument):
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        pal = cls.get_palette_colors(cv.customization.accent_palette)
        f_reg, f_bold, f_italic = get_font_names(cv.customization.font_family)
        content_w = A4[0] - 72

        full_name = (cv.personal.full_name or "Your Name").strip() or "Your Name"
        pro_title = (cv.personal.professional_title or "").strip()

        h1 = ParagraphStyle('MinH1', fontName=f_bold, fontSize=24, leading=28, textColor=colors.HexColor("#111827"), alignment=1)
        sub1 = ParagraphStyle('MinSub', fontName=f_reg, fontSize=11, leading=14, textColor=pal["primary"], alignment=1)
        contact = ParagraphStyle('MinContact', fontName=f_reg, fontSize=8.5, leading=12, textColor=colors.HexColor("#6B7280"), alignment=1)
        sec_h = ParagraphStyle('MinSec', fontName=f_bold, fontSize=10, leading=13, textColor=colors.HexColor("#111827"), spaceBefore=10, spaceAfter=4)
        body = ParagraphStyle('MinBody', fontName=f_reg, fontSize=8.5, leading=12, textColor=colors.HexColor("#374151"))
        item_title = ParagraphStyle('MinItemT', fontName=f_bold, fontSize=9, leading=11, textColor=colors.HexColor("#111827"))
        item_sub = ParagraphStyle('MinItemSub', fontName=f_reg, fontSize=8, leading=10, textColor=colors.HexColor("#6B7280"))

        story = [
            Paragraph(xml_escape(full_name.upper()), h1)
        ]
        if pro_title:
            story.append(Spacer(1, 2))
            story.append(Paragraph(xml_escape(pro_title), sub1))

        contacts = [xml_escape(c) for c in [cv.personal.email, cv.personal.phone, cv.personal.location, cv.personal.linkedin, cv.personal.github, cv.personal.website] if c]
        if contacts:
            story.append(Spacer(1, 4))
            story.append(Paragraph(" • ".join(contacts), contact))

        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D1D5DB"), spaceAfter=10))

        if cv.summary:
            story.append(Paragraph("ABOUT", sec_h))
            story.append(Paragraph(xml_multiline(cv.summary), body))
            story.append(Spacer(1, 8))

        if cv.experience:
            story.append(Paragraph("EXPERIENCE", sec_h))
            for exp in cv.experience:
                date_str = f"{xml_escape(exp.start_date)} – {xml_escape(exp.end_date) or ('Current' if exp.is_current else '')}"
                t_row = Table([[
                    Paragraph(f"<b>{xml_escape(exp.job_title)}</b>, {xml_escape(exp.company)}", item_title),
                    Paragraph(f"{xml_escape(exp.location)} | {date_str}", item_sub)
                ]], colWidths=[content_w*0.65, content_w*0.35])
                t_row.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'RIGHT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
                story.append(t_row)
                if exp.responsibilities:
                    story.append(Paragraph(xml_multiline(exp.responsibilities), body))
                if exp.achievements:
                    story.append(Paragraph(f"<i>Achievement:</i> {xml_escape(exp.achievements)}", body))
                story.append(Spacer(1, 6))

        if cv.education:
            story.append(Paragraph("EDUCATION", sec_h))
            for edu in cv.education:
                date_str = f"{xml_escape(edu.start_date)} – {xml_escape(edu.end_date)}" if edu.start_date or edu.end_date else ""
                t_row = Table([[
                    Paragraph(f"<b>{xml_escape(edu.degree)}</b> in {xml_escape(edu.field_of_study)}, {xml_escape(edu.institution)}", item_title),
                    Paragraph(f"{date_str} {xml_escape(edu.grade)}", item_sub)
                ]], colWidths=[content_w*0.7, content_w*0.3])
                t_row.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'RIGHT'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
                story.append(t_row)
                if edu.description:
                    story.append(Paragraph(xml_multiline(edu.description), body))
                story.append(Spacer(1, 4))

        if cv.skills:
            story.append(Paragraph("SKILLS", sec_h))
            skills_str = ", ".join([f"<b>{xml_escape(s.name)}</b>" for s in cv.skills])
            story.append(Paragraph(skills_str, body))
            story.append(Spacer(1, 6))

        if cv.projects:
            story.append(Paragraph("PROJECTS", sec_h))
            for p in cv.projects:
                story.append(Paragraph(f"<b>{xml_escape(p.name)}</b> — <i>{xml_escape(p.technologies)}</i>", item_title))
                if p.description:
                    story.append(Paragraph(xml_multiline(p.description), body))
                story.append(Spacer(1, 4))

        if cv.custom_sections:
            for csec in cv.custom_sections:
                if csec.title:
                    story.append(Paragraph(xml_escape(csec.title.upper()), sec_h))
                    for itm in csec.items:
                        story.append(Paragraph(f"<b>{xml_escape(itm.title)}</b> {f'— {xml_escape(itm.subtitle)}' if itm.subtitle else ''}", item_title))
                        if itm.description:
                            story.append(Paragraph(xml_multiline(itm.description), body))
                        story.append(Spacer(1, 3))

        doc.build(story, canvasmaker=NumberedCanvas)

    # =========================================================================
    # TEMPLATE 3: EXECUTIVE LEADERSHIP (Dark header banner, prestige look)
    # =========================================================================
    @classmethod
    def _build_executive(cls, buffer: io.BytesIO, cv: CVDocument):
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=32, rightMargin=32, topMargin=28, bottomMargin=28)
        pal = cls.get_palette_colors(cv.customization.accent_palette)
        f_reg, f_bold, f_italic = get_font_names(cv.customization.font_family)
        content_w = A4[0] - 64

        full_name = (cv.personal.full_name or "Your Name").strip() or "Your Name"
        pro_title = (cv.personal.professional_title or "Executive Leadership").strip()

        h1 = ParagraphStyle('ExecH1', fontName=f_bold, fontSize=22, leading=26, textColor=colors.white)
        sub1 = ParagraphStyle('ExecSub', fontName=f_reg, fontSize=11, leading=14, textColor=pal["badge"])
        contact = ParagraphStyle('ExecContact', fontName=f_reg, fontSize=8, leading=11, textColor=colors.HexColor("#F3F4F6"))

        banner_content = [
            Paragraph(xml_escape(full_name.upper()), h1),
            Spacer(1, 2),
            Paragraph(xml_escape(pro_title), sub1),
            Spacer(1, 4),
            Paragraph(" • ".join([xml_escape(c) for c in [cv.personal.email, cv.personal.phone, cv.personal.location, cv.personal.linkedin] if c]), contact)
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
        sec_h = ParagraphStyle('ExecSec', fontName=f_bold, fontSize=11, leading=14, textColor=pal["primary"], spaceAfter=4)
        body = ParagraphStyle('ExecBody', fontName=f_reg, fontSize=8.5, leading=12, textColor=colors.HexColor("#1F2937"))
        item_h = ParagraphStyle('ExecItemH', fontName=f_bold, fontSize=9.5, leading=12, textColor=colors.HexColor("#111827"))
        item_sub = ParagraphStyle('ExecItemSub', fontName=f_reg, fontSize=8, leading=10, textColor=pal["gray"])

        if cv.summary:
            story.append(Paragraph("EXECUTIVE PROFILE", sec_h))
            story.append(Paragraph(xml_multiline(cv.summary), body))
            story.append(Spacer(1, 8))

        if cv.experience:
            story.append(Paragraph("KEY LEADERSHIP & PROFESSIONAL EXPERIENCE", sec_h))
            for exp in cv.experience:
                date_str = f"{xml_escape(exp.start_date)} – {xml_escape(exp.end_date) or ('Current' if exp.is_current else '')}"
                t_row = Table([[
                    Paragraph(f"<b>{xml_escape(exp.job_title)}</b> | {xml_escape(exp.company)}", item_h),
                    Paragraph(f"{xml_escape(exp.location)} • {date_str}", item_sub)
                ]], colWidths=[content_w*0.7, content_w*0.3])
                t_row.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'RIGHT'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
                story.append(t_row)
                if exp.responsibilities:
                    story.append(Paragraph(xml_multiline(exp.responsibilities), body))
                if exp.achievements:
                    story.append(Paragraph(f"<b>Key Deliverable:</b> {xml_escape(exp.achievements)}", body))
                story.append(Spacer(1, 6))

        if cv.skills:
            story.append(Paragraph("CORE COMPETENCIES & EXPERTISE", sec_h))
            skills_str = " | ".join([f"<b>{xml_escape(s.name)}</b>" for s in cv.skills])
            story.append(Paragraph(skills_str, body))
            story.append(Spacer(1, 8))

        if cv.education:
            story.append(Paragraph("EDUCATION & CREDENTIALS", sec_h))
            for edu in cv.education:
                story.append(Paragraph(f"<b>{xml_escape(edu.degree)}</b> — {xml_escape(edu.institution)} ({xml_escape(edu.start_date)} – {xml_escape(edu.end_date)})", item_h))
            story.append(Spacer(1, 6))

        if cv.custom_sections:
            for csec in cv.custom_sections:
                if csec.title:
                    story.append(Paragraph(xml_escape(csec.title.upper()), sec_h))
                    for itm in csec.items:
                        story.append(Paragraph(f"<b>{xml_escape(itm.title)}</b> {f'— {xml_escape(itm.subtitle)}' if itm.subtitle else ''}", item_h))
                        if itm.description:
                            story.append(Paragraph(xml_multiline(itm.description), body))
                        story.append(Spacer(1, 3))

        doc.build(story, canvasmaker=NumberedCanvas)

    # =========================================================================
    # TEMPLATE 4: DEVELOPER (Terminal/Tech badges & GitHub links)
    # =========================================================================
    @classmethod
    def _build_developer(cls, buffer: io.BytesIO, cv: CVDocument):
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=32, rightMargin=32, topMargin=30, bottomMargin=30)
        pal = cls.get_palette_colors(cv.customization.accent_palette)
        content_w = A4[0] - 64

        full_name = (cv.personal.full_name or "Your Name").strip() or "Your Name"
        pro_title = (cv.personal.professional_title or "Software Engineer").strip()

        h1 = ParagraphStyle('DevH1', fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=pal["primary"])
        sub1 = ParagraphStyle('DevSub', fontName="Courier-Bold", fontSize=10, leading=13, textColor=colors.HexColor("#059669"))
        contact = ParagraphStyle('DevContact', fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#4B5563"))
        sec_h = ParagraphStyle('DevSec', fontName="Courier-Bold", fontSize=11, leading=14, textColor=pal["primary"], spaceAfter=4)
        body = ParagraphStyle('DevBody', fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=colors.HexColor("#1F2937"))
        code_p = ParagraphStyle('DevCode', fontName="Courier", fontSize=8, leading=10, textColor=pal["dark"])

        story = [
            Paragraph(xml_escape(full_name), h1),
            Paragraph(f"// {xml_escape(pro_title)}", sub1)
        ]
        contacts = [xml_escape(c) for c in [cv.personal.email, cv.personal.phone, cv.personal.location, cv.personal.github, cv.personal.linkedin, cv.personal.website] if c]
        story.append(Paragraph(" • ".join(contacts), contact))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1, color=pal["primary"], spaceAfter=8))

        if cv.summary:
            story.append(Paragraph("$ cat summary.txt", sec_h))
            story.append(Paragraph(xml_multiline(cv.summary), body))
            story.append(Spacer(1, 6))

        if cv.skills:
            story.append(Paragraph("$ stack --list-skills", sec_h))
            tech_skills = [xml_escape(s.name) for s in cv.skills]
            story.append(Paragraph(" <b>[</b> " + " • ".join(tech_skills) + " <b>]</b>", code_p))
            story.append(Spacer(1, 8))

        if cv.experience:
            story.append(Paragraph("$ git log --experience", sec_h))
            for exp in cv.experience:
                date_str = f"{xml_escape(exp.start_date)} – {xml_escape(exp.end_date) or ('Current' if exp.is_current else '')}"
                story.append(Paragraph(f"<b>commit: {xml_escape(exp.job_title)}</b> @ {xml_escape(exp.company)} ({date_str})", ParagraphStyle('DevExpT', fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=pal["primary"])))
                if exp.responsibilities:
                    story.append(Paragraph(xml_multiline(exp.responsibilities), body))
                if exp.achievements:
                    story.append(Paragraph(f"<b>Key Metric:</b> {xml_escape(exp.achievements)}", body))
                story.append(Spacer(1, 6))

        if cv.projects:
            story.append(Paragraph("$ repo --featured-projects", sec_h))
            for p in cv.projects:
                story.append(Paragraph(f"<b>{xml_escape(p.name)}</b> [ {xml_escape(p.technologies)} ]", ParagraphStyle('DevPrjH', fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=pal["dark"])))
                if p.github_url or p.live_demo_url:
                    urls = []
                    if p.github_url: urls.append(f"<a href='{p.github_url}'>repo</a>")
                    if p.live_demo_url: urls.append(f"<a href='{p.live_demo_url}'>demo</a>")
                    story.append(Paragraph(" | ".join(urls), code_p))
                if p.description:
                    story.append(Paragraph(xml_multiline(p.description), body))
                story.append(Spacer(1, 5))

        if cv.education:
            story.append(Paragraph("$ cat education.log", sec_h))
            for edu in cv.education:
                story.append(Paragraph(f"<b>{xml_escape(edu.degree)}</b> — {xml_escape(edu.institution)} ({xml_escape(edu.start_date)} – {xml_escape(edu.end_date)})", body))
            story.append(Spacer(1, 6))

        doc.build(story, canvasmaker=NumberedCanvas)

    # =========================================================================
    # TEMPLATE 5: ATS-FRIENDLY (Standardized headings, 100% linear, zero parsing errors)
    # =========================================================================
    @classmethod
    def _build_ats_friendly(cls, buffer: io.BytesIO, cv: CVDocument):
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
        black = colors.HexColor("#000000")
        gray = colors.HexColor("#333333")

        full_name = (cv.personal.full_name or "Your Name").strip() or "Your Name"
        pro_title = (cv.personal.professional_title or "").strip()

        h1 = ParagraphStyle('ATSH1', fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=black, alignment=1)
        sub1 = ParagraphStyle('ATSSub', fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=gray, alignment=1)
        contact = ParagraphStyle('ATSContact', fontName="Helvetica", fontSize=9, leading=12, textColor=black, alignment=1)
        sec_h = ParagraphStyle('ATSSec', fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=black, spaceBefore=8, spaceAfter=2)
        body = ParagraphStyle('ATSBody', fontName="Helvetica", fontSize=9, leading=12, textColor=black)
        item_h = ParagraphStyle('ATSItem', fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=black)

        story = [
            Paragraph(xml_escape(full_name.upper()), h1)
        ]
        if pro_title:
            story.append(Paragraph(xml_escape(pro_title), sub1))
        
        contacts = [xml_escape(c) for c in [cv.personal.email, cv.personal.phone, cv.personal.location, cv.personal.linkedin, cv.personal.github, cv.personal.website] if c]
        story.append(Paragraph(" | ".join(contacts), contact))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1, color=black, spaceAfter=8))

        if cv.summary:
            story.append(Paragraph("PROFESSIONAL SUMMARY", sec_h))
            story.append(Paragraph(xml_multiline(cv.summary), body))
            story.append(Spacer(1, 6))

        if cv.skills:
            story.append(Paragraph("CORE SKILLS", sec_h))
            skills_text = ", ".join([xml_escape(s.name) for s in cv.skills])
            story.append(Paragraph(skills_text, body))
            story.append(Spacer(1, 6))

        if cv.experience:
            story.append(Paragraph("WORK EXPERIENCE", sec_h))
            for exp in cv.experience:
                date_str = f"{xml_escape(exp.start_date)} - {xml_escape(exp.end_date) or ('Present' if exp.is_current else '')}"
                story.append(Paragraph(f"{xml_escape(exp.job_title)} | {xml_escape(exp.company)} | {xml_escape(exp.location)} | {date_str}", item_h))
                if exp.responsibilities:
                    story.append(Paragraph(xml_multiline(exp.responsibilities), body))
                if exp.achievements:
                    story.append(Paragraph(f"Key Achievements: {xml_escape(exp.achievements)}", body))
                story.append(Spacer(1, 5))

        if cv.education:
            story.append(Paragraph("EDUCATION", sec_h))
            for edu in cv.education:
                date_str = f"{xml_escape(edu.start_date)} - {xml_escape(edu.end_date)}" if edu.start_date or edu.end_date else ""
                story.append(Paragraph(f"{xml_escape(edu.degree)}, {xml_escape(edu.field_of_study)} - {xml_escape(edu.institution)} ({date_str}) {xml_escape(edu.grade)}", item_h))
                if edu.description:
                    story.append(Paragraph(xml_multiline(edu.description), body))
                story.append(Spacer(1, 4))

        if cv.certifications:
            story.append(Paragraph("CERTIFICATIONS", sec_h))
            for cert in cv.certifications:
                story.append(Paragraph(f"{xml_escape(cert.name)} - {xml_escape(cert.issuer)} ({xml_escape(cert.issue_date)})", body))
            story.append(Spacer(1, 4))

        if cv.custom_sections:
            for csec in cv.custom_sections:
                if csec.title:
                    story.append(Paragraph(xml_escape(csec.title.upper()), sec_h))
                    for itm in csec.items:
                        story.append(Paragraph(f"{xml_escape(itm.title)} {f'- {xml_escape(itm.subtitle)}' if itm.subtitle else ''}", item_h))
                        if itm.description:
                            story.append(Paragraph(xml_multiline(itm.description), body))
                        story.append(Spacer(1, 3))

        doc.build(story, canvasmaker=NumberedCanvas)

    # =========================================================================
    # TEMPLATE 6: CREATIVE DESIGNER (Bold color block accents & creative pills)
    # =========================================================================
    @classmethod
    def _build_creative(cls, buffer: io.BytesIO, cv: CVDocument):
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=32, rightMargin=32, topMargin=28, bottomMargin=28)
        pal = cls.get_palette_colors(cv.customization.accent_palette)
        f_reg, f_bold, f_italic = get_font_names(cv.customization.font_family)
        content_w = A4[0] - 64

        full_name = (cv.personal.full_name or "Your Name").strip() or "Your Name"
        pro_title = (cv.personal.professional_title or "Creative Specialist").strip()

        h1 = ParagraphStyle('CrtH1', fontName=f_bold, fontSize=24, leading=28, textColor=pal["primary"])
        sub1 = ParagraphStyle('CrtSub', fontName=f_reg, fontSize=11, leading=14, textColor=pal["accent"])
        sec_h = ParagraphStyle('CrtSec', fontName=f_bold, fontSize=11, leading=14, textColor=pal["primary"], spaceAfter=4)
        body = ParagraphStyle('CrtBody', fontName=f_reg, fontSize=8.5, leading=12, textColor=colors.HexColor("#1F2937"))

        story = [
            Paragraph(xml_escape(full_name), h1),
            Paragraph(xml_escape(pro_title), sub1),
            Spacer(1, 4),
            Paragraph(" • ".join([xml_escape(c) for c in [cv.personal.email, cv.personal.phone, cv.personal.location, cv.personal.portfolio, cv.personal.linkedin] if c]), body),
            Spacer(1, 8),
            HRFlowable(width="100%", thickness=3, color=pal["accent"], spaceAfter=10)
        ]

        if cv.summary:
            story.append(Paragraph("CREATIVE PROFILE", sec_h))
            story.append(Paragraph(xml_multiline(cv.summary), body))
            story.append(Spacer(1, 8))

        if cv.projects:
            story.append(Paragraph("SELECTED PORTFOLIO & PROJECTS", sec_h))
            for p in cv.projects:
                story.append(Paragraph(f"<b>{xml_escape(p.name)}</b> — {xml_escape(p.technologies)}", ParagraphStyle('PjT', fontName=f_bold, fontSize=9.5, leading=12, textColor=pal["primary"])))
                if p.description:
                    story.append(Paragraph(xml_multiline(p.description), body))
                story.append(Spacer(1, 5))

        if cv.experience:
            story.append(Paragraph("PROFESSIONAL JOURNEY", sec_h))
            for exp in cv.experience:
                story.append(Paragraph(f"<b>{xml_escape(exp.job_title)}</b> @ {xml_escape(exp.company)}", ParagraphStyle('EpT', fontName=f_bold, fontSize=9.5, leading=12, textColor=colors.HexColor("#111827"))))
                if exp.responsibilities:
                    story.append(Paragraph(xml_multiline(exp.responsibilities), body))
                story.append(Spacer(1, 5))

        if cv.skills:
            story.append(Paragraph("CREATIVE TOOLKIT & SKILLS", sec_h))
            story.append(Paragraph(" • ".join([f"<b>{xml_escape(s.name)}</b>" for s in cv.skills]), body))
            story.append(Spacer(1, 8))

        if cv.education:
            story.append(Paragraph("EDUCATION", sec_h))
            for edu in cv.education:
                story.append(Paragraph(f"<b>{xml_escape(edu.degree)}</b> — {xml_escape(edu.institution)}", body))

        doc.build(story, canvasmaker=NumberedCanvas)

    # =========================================================================
    # TEMPLATE 7: ACADEMIC & RESEARCH (Strict single column, detailed hierarchy)
    # =========================================================================
    @classmethod
    def _build_academic(cls, buffer: io.BytesIO, cv: CVDocument):
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        content_w = A4[0] - 72

        full_name = (cv.personal.full_name or "Your Name").strip() or "Your Name"
        pro_title = (cv.personal.professional_title or "Researcher / Scholar").strip()

        h1 = ParagraphStyle('AcdH1', fontName="Times-Bold", fontSize=20, leading=24, textColor=colors.black, alignment=1)
        sub1 = ParagraphStyle('AcdSub', fontName="Times-Roman", fontSize=11, leading=14, textColor=colors.HexColor("#333333"), alignment=1)
        sec_h = ParagraphStyle('AcdSec', fontName="Times-Bold", fontSize=11, leading=14, textColor=colors.black, spaceBefore=8, spaceAfter=3)
        body = ParagraphStyle('AcdBody', fontName="Times-Roman", fontSize=9, leading=13, textColor=colors.black)

        story = [
            Paragraph(xml_escape(full_name), h1),
            Paragraph(xml_escape(pro_title), sub1),
            Spacer(1, 3),
            Paragraph(" • ".join([xml_escape(c) for c in [cv.personal.email, cv.personal.phone, cv.personal.location, cv.personal.website] if c]), sub1),
            Spacer(1, 6),
            HRFlowable(width="100%", thickness=0.8, color=colors.black, spaceAfter=8)
        ]

        if cv.education:
            story.append(Paragraph("EDUCATION", sec_h))
            for edu in cv.education:
                date_str = f"{xml_escape(edu.start_date)} – {xml_escape(edu.end_date)}" if edu.start_date or edu.end_date else ""
                story.append(Paragraph(f"<b>{xml_escape(edu.degree)}</b>, {xml_escape(edu.field_of_study)}, {xml_escape(edu.institution)} ({date_str})", body))
                if edu.grade or edu.description:
                    story.append(Paragraph(f"{xml_escape(edu.grade)} • {xml_multiline(edu.description)}", body))
                story.append(Spacer(1, 4))

        if cv.experience:
            story.append(Paragraph("ACADEMIC & RESEARCH APPOINTMENTS", sec_h))
            for exp in cv.experience:
                story.append(Paragraph(f"<b>{xml_escape(exp.job_title)}</b>, {xml_escape(exp.company)} ({xml_escape(exp.start_date)} – {xml_escape(exp.end_date)})", body))
                if exp.responsibilities:
                    story.append(Paragraph(xml_multiline(exp.responsibilities), body))
                story.append(Spacer(1, 4))

        if cv.achievements:
            story.append(Paragraph("HONORS & AWARDS", sec_h))
            for ach in cv.achievements:
                story.append(Paragraph(f"<b>{xml_escape(ach.title)}</b> ({xml_escape(ach.date)}): {xml_escape(ach.description)}", body))
                story.append(Spacer(1, 3))

        if cv.skills:
            story.append(Paragraph("RESEARCH METHODOLOGIES & SKILLS", sec_h))
            story.append(Paragraph(", ".join([xml_escape(s.name) for s in cv.skills]), body))

        doc.build(story, canvasmaker=NumberedCanvas)

    # =========================================================================
    # TEMPLATE 8: CORPORATE PROFESSIONAL (Clean structured corporate 2-column)
    # =========================================================================
    @classmethod
    def _build_professional(cls, buffer: io.BytesIO, cv: CVDocument):
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=32,
            bottomMargin=32
        )
        pal = cls.get_palette_colors(cv.customization.accent_palette)
        f_reg, f_bold, f_italic = get_font_names(cv.customization.font_family)
        content_w = A4[0] - 72

        full_name = (cv.personal.full_name or "Your Name").strip() or "Your Name"
        pro_title = (cv.personal.professional_title or "Corporate Professional").strip()

        h1 = ParagraphStyle('CorpName', fontName=f_bold, fontSize=22, leading=26, textColor=pal["primary"])
        sub = ParagraphStyle('CorpTitle', fontName=f_bold, fontSize=11, leading=14, textColor=pal["gray"])
        contact_s = ParagraphStyle('CorpContact', fontName=f_reg, fontSize=8.5, leading=12, textColor=pal["dark"])
        sec_h = ParagraphStyle('CorpSec', fontName=f_bold, fontSize=11, leading=14, textColor=pal["primary"], spaceBefore=8, spaceAfter=4)
        body = ParagraphStyle('CorpBody', fontName=f_reg, fontSize=8.5, leading=12, textColor=colors.HexColor("#1F2937"))
        item_title = ParagraphStyle('CorpItemT', fontName=f_bold, fontSize=9.5, leading=12, textColor=colors.HexColor("#111827"))
        item_meta = ParagraphStyle('CorpItemM', fontName=f_reg, fontSize=8, leading=10, textColor=pal["gray"])

        story = []

        # Corporate Header
        contacts = [xml_escape(c) for c in [cv.personal.email, cv.personal.phone, cv.personal.location, cv.personal.linkedin, cv.personal.website] if c]
        contact_p = Paragraph(" | ".join(contacts), contact_s)

        name_cell = [
            Paragraph(xml_escape(full_name.upper()), h1),
            Spacer(1, 2),
            Paragraph(xml_escape(pro_title), sub),
            Spacer(1, 4),
            contact_p
        ]

        photo_buf = None
        if cv.customization.show_photo and cv.customization.photo_style != "none":
            photo_buf = cls.prepare_photo(cv.personal.profile_photo_path, cv.customization.photo_style, size=90)

        if photo_buf:
            rl_img = RLImage(photo_buf, width=65, height=65)
            h_table = Table([[name_cell, rl_img]], colWidths=[content_w - 75, 75])
            h_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (1,0), (1,0), 'RIGHT'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(h_table)
        else:
            story.extend(name_cell)

        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=2, color=pal["primary"], spaceAfter=10))

        # Full width summary if present
        if cv.summary:
            story.append(Paragraph("EXECUTIVE PROFILE", sec_h))
            story.append(Paragraph(xml_multiline(cv.summary), body))
            story.append(Spacer(1, 8))

        # Split 2-column: Left 62% (Experience & Projects) | Right 38% (Skills, Education, Certs)
        left_w = content_w * 0.62
        right_w = content_w * 0.38 - 12
        left_story = []
        right_story = []

        # Left: Experience & Projects & Volunteer
        if cv.experience:
            left_story.append(Paragraph("PROFESSIONAL EXPERIENCE", sec_h))
            for exp in cv.experience:
                date_str = f"{xml_escape(exp.start_date)} – {xml_escape(exp.end_date) or ('Present' if exp.is_current else '')}"
                left_story.append(Paragraph(f"<b>{xml_escape(exp.job_title)}</b>", item_title))
                left_story.append(Paragraph(f"<b>{xml_escape(exp.company)}</b> | {xml_escape(exp.location)} | {date_str}", item_meta))
                if exp.responsibilities:
                    left_story.append(Paragraph(xml_multiline(exp.responsibilities), body))
                if exp.achievements:
                    left_story.append(Paragraph(f"<b>Key Impact:</b> {xml_escape(exp.achievements)}", body))
                left_story.append(Spacer(1, 6))

        if cv.projects:
            left_story.append(Paragraph("NOTABLE PROJECTS", sec_h))
            for p in cv.projects:
                left_story.append(Paragraph(f"<b>{xml_escape(p.name)}</b> — <i>{xml_escape(p.technologies)}</i>", item_title))
                if p.description:
                    left_story.append(Paragraph(xml_multiline(p.description), body))
                left_story.append(Spacer(1, 4))

        if cv.volunteer:
            left_story.append(Paragraph("VOLUNTEER INITIATIVES", sec_h))
            for v in cv.volunteer:
                left_story.append(Paragraph(f"<b>{xml_escape(v.role)}</b> — {xml_escape(v.organization)}", item_title))
                if v.description:
                    left_story.append(Paragraph(xml_multiline(v.description), body))
                left_story.append(Spacer(1, 4))

        # Right: Skills, Education, Certifications, Languages, Custom Sections
        if cv.skills:
            right_story.append(Paragraph("CORE EXPERTISE", sec_h))
            skills_by_cat = {}
            for s in cv.skills:
                skills_by_cat.setdefault(s.category, []).append(xml_escape(s.name))
            for cat, s_names in skills_by_cat.items():
                right_story.append(Paragraph(f"<b>{xml_escape(cat)}:</b>", item_meta))
                right_story.append(Paragraph(" • ".join(s_names), body))
                right_story.append(Spacer(1, 3))
            right_story.append(Spacer(1, 6))

        if cv.education:
            right_story.append(Paragraph("EDUCATION", sec_h))
            for edu in cv.education:
                right_story.append(Paragraph(f"<b>{xml_escape(edu.degree)}</b>", item_title))
                right_story.append(Paragraph(f"{xml_escape(edu.institution)}", item_meta))
                date_str = f"{xml_escape(edu.start_date)} – {xml_escape(edu.end_date)}" if edu.start_date or edu.end_date else ""
                if date_str or edu.grade:
                    right_story.append(Paragraph(f"{date_str} {xml_escape(edu.grade)}", item_meta))
                right_story.append(Spacer(1, 4))

        if cv.certifications:
            right_story.append(Paragraph("CERTIFICATIONS", sec_h))
            for cert in cv.certifications:
                right_story.append(Paragraph(f"<b>{xml_escape(cert.name)}</b>", item_title))
                right_story.append(Paragraph(f"{xml_escape(cert.issuer)} ({xml_escape(cert.issue_date)})", item_meta))
                right_story.append(Spacer(1, 3))

        if cv.languages:
            right_story.append(Paragraph("LANGUAGES", sec_h))
            for l in cv.languages:
                right_story.append(Paragraph(f"• <b>{xml_escape(l.name)}</b>: {xml_escape(l.proficiency)}", body))
            right_story.append(Spacer(1, 4))

        if cv.custom_sections:
            for csec in cv.custom_sections:
                if csec.title:
                    right_story.append(Paragraph(xml_escape(csec.title.upper()), sec_h))
                    for itm in csec.items:
                        right_story.append(Paragraph(f"<b>{xml_escape(itm.title)}</b>", item_title))
                        if itm.description:
                            right_story.append(Paragraph(xml_multiline(itm.description), body))
                        right_story.append(Spacer(1, 3))

        if left_story and right_story:
            split_table = Table([[left_story, right_story]], colWidths=[left_w, right_w])
            split_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (0,0), 0),
                ('RIGHTPADDING', (0,0), (0,0), 10),
                ('LEFTPADDING', (1,0), (1,0), 10),
                ('RIGHTPADDING', (1,0), (1,0), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('LINEAFTER', (0,0), (0,0), 0.5, pal["border"]),
            ]))
            story.append(split_table)
        elif left_story:
            story.extend(left_story)
        elif right_story:
            story.extend(right_story)

        doc.build(story, canvasmaker=NumberedCanvas)
