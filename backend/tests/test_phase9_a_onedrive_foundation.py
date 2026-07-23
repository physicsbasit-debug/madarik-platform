from pathlib import Path
import pytest
from app.models.cloud_source import CloudSourceProvider, CloudSourceType
from app.services.cloud_source_repository import CloudSourceRepository
from app.services.onedrive_source_parser import parse_onedrive_source_url
ROOT = Path(__file__).resolve().parents[2]

def test_parser_accepts_onedrive_url():
    payload=parse_onedrive_source_url(web_url='https://onedrive.live.com/?id=ABC123',display_name='ملف العلوم')
    assert payload.provider is CloudSourceProvider.onedrive
    assert payload.external_id.startswith('u!')
    assert payload.metadata['addressing_mode'] == 'share'
    assert payload.metadata['share_token'] == payload.external_id

def test_parser_accepts_sharepoint_url():
    payload=parse_onedrive_source_url(web_url='https://school.sharepoint.com/sites/science/document.pdf',display_name='وثيقة',source_type=CloudSourceType.file)
    assert payload.metadata['host']=='school.sharepoint.com'
    assert payload.external_id

def test_parser_rejects_unknown_host():
    with pytest.raises(ValueError): parse_onedrive_source_url(web_url='https://example.com/file.pdf',display_name='غير صالح')

def test_repository_persists_source(tmp_path):
    repository=CloudSourceRepository(tmp_path/'db.sqlite')
    payload=parse_onedrive_source_url(web_url='https://1drv.ms/u/s!example',display_name='مصدر')
    created=repository.create(payload); items=repository.list(provider='onedrive')
    assert len(items)==1 and items[0].id==created.id

def test_api_routes_exist():
    content=(ROOT/'backend/app/api/projects.py').read_text(encoding='utf-8')
    assert 'list_cloud_sources' in content and 'create_onedrive_source_from_url' in content and 'delete_cloud_source' in content

def test_frontend_workspace_exists():
    content=(ROOT/'frontend/src/features/cloud/CloudSources.tsx').read_text(encoding='utf-8')
    assert 'إضافة مصدر OneDrive' in content and 'SharePoint' in content and 'حفظ المصدر' in content

def test_readme_tracks_phase_9a():
    content=(ROOT/'README.md').read_text(encoding='utf-8')
    assert 'Phase 9-A' in content and 'Cloud Source Expansion and OneDrive Foundation' in content
