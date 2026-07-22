
from pathlib import Path
from app.models.assessment import AssessmentBlueprint, AssessmentDraft
from app.models.project import CognitiveCategory, QuestionItem
from app.models.question_bank import QuestionBankItem
from app.services.assessment_builder import auto_select_questions_for_assessment, validate_assessment_blueprint
from app.services.question_bank_repository import QuestionBankRepository

ROOT=Path(__file__).resolve().parents[2]

def item(i,cat,marks=1):
    return QuestionBankItem(id=i,source_project_id='p',source_question_id='q'+i,content_fingerprint=i,question_snapshot=QuestionItem(id='q'+i,original_number=i,original_text=i,translated_text=i,marks=marks,order_index=1,cognitive_category=cat,curriculum_grade=10,curriculum_science_domain='physics',curriculum_unit_id='waves'))

def draft():
    return AssessmentDraft(blueprint=AssessmentBlueprint(grade=10,science_domain='physics',unit_id='waves',total_marks=4,target_question_count=4,knowledge_percent=25,application_percent=50,reasoning_percent=25))

def test_auto_selection_matches_targets(tmp_path):
    repo=QuestionBankRepository(tmp_path/'b.db'); items=[item('k',CognitiveCategory.knowledge),item('a1',CognitiveCategory.application),item('a2',CognitiveCategory.application),item('r',CognitiveCategory.reasoning)]
    for x in items: repo.save_from_project_question(__import__('app.models.project',fromlist=['ProjectSession']).ProjectSession(id=x.source_project_id,questions=[x.question_snapshot]),x.question_snapshot)
    stored=repo.search()
    result=auto_select_questions_for_assessment(draft(),stored,repo)
    assert result.validation.ready is True
    assert len(result.selected_item_ids)==4

def test_shortage_reported(tmp_path):
    repo=QuestionBankRepository(tmp_path/'b.db'); items=[item('k',CognitiveCategory.knowledge)]
    result=auto_select_questions_for_assessment(draft(),items,repo)
    assert result.shortages and result.validation.ready is False

def test_unclassified_blocks(tmp_path):
    repo=QuestionBankRepository(tmp_path/'b.db'); x=item('u',CognitiveCategory.unclassified); pr=__import__('app.models.project',fromlist=['ProjectSession']).ProjectSession(id='p',questions=[x.question_snapshot]); saved=repo.save_from_project_question(pr,x.question_snapshot); d=draft(); d.question_bank_item_ids=[saved.id]
    v=validate_assessment_blueprint(d,repo); assert v.unclassified_selected==1 and not v.ready

def test_routes_exist():
    c=(ROOT/'backend/app/api/projects.py').read_text(); assert 'auto_select_assessment_questions' in c and 'validate_assessment_draft' in c

def test_frontend_controls():
    c=(ROOT/'frontend/src/features/assessment/AssessmentBuilder.tsx').read_text(); assert 'اختيار آلي' in c and 'تحقق من الجاهزية' in c

def test_readme():
    assert 'Phase 6-B' in (ROOT/'README.md').read_text()
