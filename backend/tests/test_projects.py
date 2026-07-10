from fastapi.testclient import TestClient

from app.main import app


def test_create_update_load_demo_and_delete_project() -> None:
    client = TestClient(app)
    create_response = client.post("/api/projects", json={"school_name": "مدرسة تجريبية"})
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]

    read_response = client.get(f"/api/projects/{project_id}")
    assert read_response.status_code == 200
    assert read_response.json()["metadata"]["school_name"] == "مدرسة تجريبية"

    metadata_response = client.patch(
        f"/api/projects/{project_id}/metadata",
        json={
            "school_name": "مدرسة الباسط",
            "directorate": "جنوب الباطنة",
            "subject": "الفيزياء",
            "grade": "العاشر",
            "semester": "الفصل الدراسي الأول",
            "paper_title": "ورقة تدريبية",
            "duration": "45 دقيقة",
            "total_marks": "8",
            "teacher_name": "أ. وليد الهنائي",
            "date": "2026-07-10",
            "output_mode": "bilingual",
            "export_formats": ["docx", "pdf"],
        },
    )
    assert metadata_response.status_code == 200
    assert metadata_response.json()["metadata"]["output_mode"] == "bilingual"

    upload_response = client.put(
        f"/api/projects/{project_id}/upload-info",
        json={"name": "sample.pdf", "size": 2048, "type": "application/pdf"},
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["uploaded_file"]["name"] == "sample.pdf"

    demo_response = client.post(f"/api/projects/{project_id}/demo-content")
    assert demo_response.status_code == 200
    body = demo_response.json()
    assert len(body["questions"]) == 4
    assert len(body["glossary"]) == 4

    first_question_id = body["questions"][0]["id"]
    question_response = client.patch(
        f"/api/projects/{project_id}/questions/{first_question_id}",
        json={"translated_text": "ترجمة معدّلة", "marks": 2, "status": "needs_review"},
    )
    assert question_response.status_code == 200
    assert question_response.json()["questions"][0]["translated_text"] == "ترجمة معدّلة"

    ordered_ids = [question["id"] for question in reversed(question_response.json()["questions"])]
    reorder_response = client.post(
        f"/api/projects/{project_id}/questions/reorder",
        json={"ordered_question_ids": ordered_ids},
    )
    assert reorder_response.status_code == 200
    reordered = sorted(reorder_response.json()["questions"], key=lambda item: item["order_index"])
    assert [question["id"] for question in reordered] == ordered_ids

    term_id = reorder_response.json()["glossary"][0]["id"]
    glossary_response = client.patch(
        f"/api/projects/{project_id}/glossary/{term_id}",
        json={"arabic_term": "مصطلح معدّل", "status": "needs_review"},
    )
    assert glossary_response.status_code == 200
    assert glossary_response.json()["glossary"][0]["arabic_term"] == "مصطلح معدّل"

    delete_response = client.delete(f"/api/projects/{project_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True


def test_invalid_reorder_is_rejected() -> None:
    client = TestClient(app)
    project_id = client.post("/api/projects", json={}).json()["id"]
    client.post(f"/api/projects/{project_id}/demo-content")

    response = client.post(
        f"/api/projects/{project_id}/questions/reorder",
        json={"ordered_question_ids": ["q-1", "missing"]},
    )
    assert response.status_code == 400
