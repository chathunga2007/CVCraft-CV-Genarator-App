"""
CVCraft Job Match & ATS Tailoring View
Analyzes CV against target job postings, inspects ATS formatting compliance,
and suggests keyword integration.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QComboBox, QScrollArea, QFrame, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, Dict, Any

from models.cv_model import CVDocument, SkillItem
from repositories.cv_repository import CVRepository
from services.ats_service import ATSService

class JobMatchView(QWidget):
    cv_updated = pyqtSignal(str) # passes cv_id when keywords are added

    def __init__(self, cv_repo: CVRepository, parent=None):
        super().__init__(parent)
        self.repo = cv_repo
        self.current_cv: Optional[CVDocument] = None
        self.last_analysis_result: Dict[str, Any] = {}
        self.setProperty("class", "MainContent")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Header
        hdr_box = QVBoxLayout()
        title = QLabel("Tailor My CV & ATS Match Engine")
        title.setProperty("class", "HeaderTitle")
        sub = QLabel("Paste any job description to calculate keyword coverage, ATS compatibility, and tailoring insights.")
        sub.setProperty("class", "HeaderSubtitle")
        hdr_box.addWidget(title)
        hdr_box.addWidget(sub)
        layout.addLayout(hdr_box)

        # CV Selection Row
        sel_row = QHBoxLayout()
        sel_row.addWidget(QLabel("Select Target CV:"))
        self.cv_selector = QComboBox()
        self.cv_selector.setMinimumWidth(300)
        self.cv_selector.currentIndexChanged.connect(self._on_cv_selected)
        sel_row.addWidget(self.cv_selector)
        sel_row.addStretch()
        layout.addLayout(sel_row)

        # Scrollable analysis area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(20)

        # Job Description Input Card
        jd_card = QFrame()
        jd_card.setProperty("class", "Card")
        jd_card.setContentsMargins(16, 16, 16, 16)
        jd_layout = QVBoxLayout(jd_card)
        jd_lbl = QLabel("Paste Target Job Description (Requirements, Tech Stack, Responsibilities):")
        jd_lbl.setProperty("class", "FieldLabel")
        jd_layout.addWidget(jd_lbl)

        self.jd_input = QTextEdit()
        self.jd_input.setPlaceholderText("Paste the job posting requirements here...")
        self.jd_input.setFixedHeight(140)
        jd_layout.addWidget(self.jd_input)

        run_btn = QPushButton("🚀 Analyze & Match Keywords")
        run_btn.setFixedHeight(40)
        run_btn.setProperty("class", "PrimaryBtn")
        run_btn.clicked.connect(self._run_analysis)
        jd_layout.addWidget(run_btn)
        c_layout.addWidget(jd_card)

        # Results Container (Hidden until analyzed)
        self.results_card = QFrame()
        self.results_card.setProperty("class", "Card")
        self.results_card.setContentsMargins(20, 20, 20, 20)
        self.res_layout = QVBoxLayout(self.results_card)
        self.res_layout.setSpacing(16)

        # Score Row
        score_box = QHBoxLayout()
        s_info = QVBoxLayout()
        self.score_title = QLabel("ATS Keyword Coverage Match")
        self.score_title.setProperty("class", "SectionHeader")
        self.score_sub = QLabel("Score based on technical keywords, required competencies, and job qualifications.")
        self.score_sub.setProperty("class", "HeaderSubtitle")
        s_info.addWidget(self.score_title)
        s_info.addWidget(self.score_sub)
        score_box.addLayout(s_info)
        score_box.addStretch()

        self.score_val_lbl = QLabel("0%")
        self.score_val_lbl.setStyleSheet("font-size: 32px; font-weight: 800; color: #10B981;")
        score_box.addWidget(self.score_val_lbl)
        self.res_layout.addLayout(score_box)

        self.score_bar = QProgressBar()
        self.score_bar.setFixedHeight(8)
        self.score_bar.setTextVisible(False)
        self.res_layout.addWidget(self.score_bar)

        # Matching Keywords Pill Box
        self.matching_lbl = QLabel("Matching Keywords Found in Your CV:")
        self.matching_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #10B981;")
        self.res_layout.addWidget(self.matching_lbl)
        self.matching_text = QLabel("None yet")
        self.matching_text.setWordWrap(True)
        self.matching_text.setProperty("class", "ItemCard")
        self.res_layout.addWidget(self.matching_text)

        # Missing Keywords Pill Box
        self.missing_lbl = QLabel("Missing Keywords from Job Description:")
        self.missing_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #F59E0B;")
        self.res_layout.addWidget(self.missing_lbl)
        self.missing_text = QLabel("None yet")
        self.missing_text.setWordWrap(True)
        self.missing_text.setProperty("class", "ItemCard")
        self.res_layout.addWidget(self.missing_text)

        # Add missing skills button
        self.add_missing_btn = QPushButton("+ Integrate Missing Keywords into CV Skills")
        self.add_missing_btn.setProperty("class", "PrimaryBtn")
        self.add_missing_btn.clicked.connect(self._add_missing_skills)
        self.res_layout.addWidget(self.add_missing_btn)

        # Recommendations Checklist
        rec_title = QLabel("Tailoring & ATS Recommendations:")
        rec_title.setProperty("class", "SectionHeader")
        self.res_layout.addWidget(rec_title)
        self.rec_text = QLabel("")
        self.rec_text.setWordWrap(True)
        self.rec_text.setProperty("class", "MutedText")
        self.res_layout.addWidget(self.rec_text)

        c_layout.addWidget(self.results_card)
        self.results_card.hide()

        c_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def refresh(self, preselect_cv_id: str = ""):
        self.cv_selector.blockSignals(True)
        self.cv_selector.clear()
        cvs = self.repo.list_all(sort_by="updated_at", desc=True)
        for c in cvs:
            self.cv_selector.addItem(f"{c['name']} ({c['job_target'] or 'CV'})", c['id'])
        
        if preselect_cv_id:
            idx = self.cv_selector.findData(preselect_cv_id)
            if idx >= 0:
                self.cv_selector.setCurrentIndex(idx)
        
        self.cv_selector.blockSignals(False)
        self._on_cv_selected()

    def _on_cv_selected(self):
        cv_id = self.cv_selector.currentData()
        if cv_id:
            self.current_cv = self.repo.get_by_id(cv_id)

    def _run_analysis(self):
        if not self.current_cv:
            QMessageBox.warning(self, "No CV Selected", "Please select a CV to analyze.")
            return

        jd_text = self.jd_input.toPlainText().strip()
        if not jd_text:
            QMessageBox.warning(self, "Empty Job Description", "Please paste a job description into the input box.")
            return

        result = ATSService.analyze_job_match(self.current_cv, jd_text)
        formatting = ATSService.check_ats_formatting(self.current_cv)
        self.last_analysis_result = result

        score = result["match_score"]
        self.score_val_lbl.setText(f"{score}%")
        self.score_bar.setValue(score)

        if score >= 75:
            self.score_val_lbl.setStyleSheet("font-size: 32px; font-weight: 800; color: #10B981;")
            self.score_bar.setStyleSheet("QProgressBar { background: #0F172A; } QProgressBar::chunk { background: #10B981; }")
        elif score >= 50:
            self.score_val_lbl.setStyleSheet("font-size: 32px; font-weight: 800; color: #F59E0B;")
            self.score_bar.setStyleSheet("QProgressBar { background: #0F172A; } QProgressBar::chunk { background: #F59E0B; }")
        else:
            self.score_val_lbl.setStyleSheet("font-size: 32px; font-weight: 800; color: #EF4444;")
            self.score_bar.setStyleSheet("QProgressBar { background: #0F172A; } QProgressBar::chunk { background: #EF4444; }")

        m_skills = result["matching_skills"]
        self.matching_text.setText(" • ".join(m_skills) if m_skills else "No direct technical keyword matches found.")

        miss_skills = result["missing_skills"]
        self.missing_text.setText(" • ".join(miss_skills) if miss_skills else "Great job! All key target skills are present in your CV.")

        all_recs = result["recommendations"] + [f"Format Check: {p}" for p in formatting["passes"][:2]]
        if formatting["issues"]:
            all_recs.extend([f"⚠️ {i}" for i in formatting["issues"]])

        self.rec_text.setText("\n".join([f"• {r}" for r in all_recs]))
        self.results_card.show()

    def _add_missing_skills(self):
        if not self.current_cv or not self.last_analysis_result:
            return
        missing = self.last_analysis_result.get("missing_skills", [])
        if not missing:
            QMessageBox.information(self, "No Missing Skills", "Your CV already covers all extracted keywords!")
            return

        reply = QMessageBox.question(
            self,
            "Integrate Missing Skills",
            f"Add {len(missing)} missing skills to your CV's 'Technical Skills' section?\n\n" +
            " • " + " • ".join(missing[:8]) + ("..." if len(missing) > 8 else ""),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for s_name in missing:
                if not any(s.name.lower() == s_name.lower() for s in self.current_cv.skills):
                    self.current_cv.skills.append(SkillItem(name=s_name, category="Technical Skills", proficiency="Intermediate"))
            self.repo.save(self.current_cv)
            self._run_analysis()
            self.cv_updated.emit(self.current_cv.id)
            QMessageBox.information(self, "Keywords Added", "Target keywords integrated into your CV skills!")
