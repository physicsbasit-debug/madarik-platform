import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "backend/app/contracts/v2_scope.json"


def load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_v2_scope_contract_exists() -> None:
    assert CONTRACT_PATH.exists()


def test_v2_is_science_only_for_grades_1_to_12() -> None:
    contract = load_contract()

    assert contract["grades"] == list(range(1, 13))
    assert set(contract["science_domains"]) == {
        "general_science",
        "physics",
        "chemistry",
        "biology",
        "environmental_science",
    }
    assert "non_science_subjects" in contract["out_of_scope"]


def test_google_drive_is_first_and_onedrive_is_deferred() -> None:
    contract = load_contract()

    assert contract["cloud_providers"]["phase_1"] == ["google_drive"]
    assert contract["cloud_providers"]["deferred"] == ["onedrive"]


def test_cognitive_categories_are_locked() -> None:
    contract = load_contract()

    assert contract["cognitive_categories"] == [
        "knowledge",
        "application",
        "reasoning",
        "unclassified",
    ]


def test_core_workflows_are_declared() -> None:
    contract = load_contract()

    assert contract["core_workflows"] == [
        "quick_translation",
        "professional_translation",
        "curriculum_library",
        "question_bank",
        "assessment_builder",
        "differentiated_activities",
        "science_diagrams",
    ]


def test_phase0_documents_exist() -> None:
    expected = [
        "docs/PHASE_0_A_V2_SCOPE_LOCK.md",
        "docs/PHASE_0_A_V2_ARCHITECTURE.md",
        "docs/PHASE_0_A_V2_DATA_CONTRACTS.md",
        "docs/PHASE_0_A_V2_ARCHITECTURE_DECISIONS.md",
        "docs/PHASE_0_A_V2_ROADMAP.md",
        "docs/PHASE_0_A_V2_UI_SIMPLIFICATION_PLAN.md",
    ]

    for rel in expected:
        assert (ROOT / rel).exists(), rel


def test_deferred_product_areas_remain_out_of_scope() -> None:
    contract = load_contract()

    assert {
        "student_lms",
        "attendance",
        "student_gradebook",
        "virtual_classrooms",
        "marketplace",
        "mobile_app",
        "automatic_student_answer_grading",
    }.issubset(set(contract["out_of_scope"]))
