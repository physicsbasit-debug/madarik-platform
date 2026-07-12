from app.models.project import PdfLayoutAssetInfo
from app.services.session_store import project_store


def _create_project_with_question():
    project = project_store.create()
    project = project_store.load_demo_content(project.id)
    assert project is not None
    assert project.questions
    return project, project.questions[0].id


def _layout_asset(page_number: int) -> PdfLayoutAssetInfo:
    return PdfLayoutAssetInfo(
        name=f"page-{page_number}.png",
        size=10,
        type="image/png",
        data_base64="dGVzdA==",
        page_number=page_number,
    )


def test_link_layout_asset_to_question() -> None:
    project, question_id = _create_project_with_question()
    asset = _layout_asset(1)

    project_store.set_layout_assets(project.id, [asset])
    updated = project_store.link_layout_asset_to_question(
        project.id,
        question_id,
        asset.id,
    )

    assert updated is not None
    question = next(item for item in updated.questions if item.id == question_id)
    assert question.linked_layout_asset_ids == [asset.id]


def test_duplicate_link_is_not_added_twice() -> None:
    project, question_id = _create_project_with_question()
    asset = _layout_asset(1)

    project_store.set_layout_assets(project.id, [asset])
    project_store.link_layout_asset_to_question(project.id, question_id, asset.id)
    updated = project_store.link_layout_asset_to_question(
        project.id,
        question_id,
        asset.id,
    )

    assert updated is not None
    question = next(item for item in updated.questions if item.id == question_id)
    assert question.linked_layout_asset_ids == [asset.id]


def test_unknown_layout_asset_cannot_be_linked() -> None:
    project, question_id = _create_project_with_question()

    updated = project_store.link_layout_asset_to_question(
        project.id,
        question_id,
        "missing-asset",
    )

    assert updated is None


def test_unlink_layout_asset_from_question() -> None:
    project, question_id = _create_project_with_question()
    asset = _layout_asset(1)

    project_store.set_layout_assets(project.id, [asset])
    project_store.link_layout_asset_to_question(project.id, question_id, asset.id)

    updated = project_store.unlink_layout_asset_from_question(
        project.id,
        question_id,
        asset.id,
    )

    assert updated is not None
    question = next(item for item in updated.questions if item.id == question_id)
    assert question.linked_layout_asset_ids == []


def test_removing_layout_asset_cleans_question_links() -> None:
    project, question_id = _create_project_with_question()
    asset = _layout_asset(1)

    project_store.set_layout_assets(project.id, [asset])
    project_store.link_layout_asset_to_question(project.id, question_id, asset.id)

    updated = project_store.remove_layout_asset(project.id, asset.id)

    assert updated is not None
    assert updated.layout_assets == []

    question = next(item for item in updated.questions if item.id == question_id)
    assert question.linked_layout_asset_ids == []


def test_replacing_layout_assets_removes_stale_links() -> None:
    project, question_id = _create_project_with_question()
    first_asset = _layout_asset(1)
    second_asset = _layout_asset(2)
    replacement_asset = _layout_asset(3)

    project_store.set_layout_assets(
        project.id,
        [first_asset, second_asset],
    )
    project_store.link_layout_asset_to_question(
        project.id,
        question_id,
        first_asset.id,
    )
    project_store.link_layout_asset_to_question(
        project.id,
        question_id,
        second_asset.id,
    )

    updated = project_store.set_layout_assets(
        project.id,
        [second_asset, replacement_asset],
    )

    assert updated is not None
    question = next(item for item in updated.questions if item.id == question_id)
    assert question.linked_layout_asset_ids == [second_asset.id]
