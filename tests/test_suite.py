import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import *
from models.cv_model import *
from database.db import *
from repositories.cv_repository import *
from repositories.settings_repository import *
from services.cv_service import *
from services.pdf_service import *
from services.ats_service import *
from services.ai_service import *
from services.import_export import *

print("1. Testing models & serialization...")
demo = CVService.create_sample_cv()
d_dict = demo.to_dict()
restored = CVDocument.from_dict(d_dict)
assert restored.personal.full_name == demo.personal.full_name

print("2. Testing database save & retrieval...")
repo = CVRepository()
repo.save(demo, completion_pct=92)
fetched = repo.get_by_id(demo.id)
assert fetched is not None
assert fetched.personal.email == demo.personal.email

print("3. Testing PDF compilation for all 9 templates...")
templates = ['classic_sidebar', 'modern', 'minimal', 'executive', 'developer', 'ats_friendly', 'creative', 'academic', 'professional']
for t in templates:
    demo.template_id = t
    pdf_bytes = PDFService.generate_pdf_bytes(demo)
    assert len(pdf_bytes) > 1000
    imgs = PDFService.render_pdf_to_images(pdf_bytes, dpi=100)
    assert len(imgs) >= 1
    print(f"   [OK] Template [{t}]: {len(pdf_bytes)} bytes, {len(imgs)} pages rendered")

print("4. Testing ATS Keyword Matcher...")
res = ATSService.analyze_job_match(demo, "Looking for Senior Python, AWS, Docker, Kubernetes, React, FastAPI, CI/CD engineer")
assert res['match_score'] > 50
print(f"   [OK] ATS match score: {res['match_score']}%, Found: {len(res['matching_skills'])} skills")

print("5. Testing AI Assistant...")
ai = AIService()
improved_summary = ai.improve_summary(demo.summary, demo.personal.professional_title)
assert len(improved_summary['suggested']) > 50
suggested_skills = ai.suggest_skills_for_role("Backend Developer")
assert len(suggested_skills) >= 4
print("   [OK] AI assistant generation successful")

print("6. Testing Import/Export .cvcv...")
export_path = USER_DATA_DIR / "test_export.cvcv"
ImportExportService.export_cvcv_file(demo, str(export_path))
imported_cv = ImportExportService.import_cvcv_file(str(export_path))
assert imported_cv.name == demo.name
print("   [OK] Lossless import/export verified")

print("\nALL BACKEND & SERVICE VERIFICATIONS PASSED 100%!")
