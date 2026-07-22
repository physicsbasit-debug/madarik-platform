import {
  Download,
  FolderOpen,
  MoreVertical,
  RefreshCcw,
  Save,
  Upload,
  Wifi,
  WifiOff,
} from 'lucide-react';
import type { ApiConnectionStatus, ProjectMetadata } from '../types/project';

interface WorkspaceTopBarProps {
  metadata: ProjectMetadata;
  apiStatus: ApiConnectionStatus;
  lastSyncNote: string;
  projectId: string | null;
  onOpenStart: () => void;
  onDownloadSnapshot: () => void;
  onImportSnapshot: (file: File | null) => void;
  onNewProject: () => void;
}

function connectionLabel(status: ApiConnectionStatus) {
  if (status === 'connected') return 'متصل';
  if (status === 'syncing') return 'جارٍ الحفظ';
  if (status === 'connecting') return 'جارٍ الاتصال';
  return 'وضع محلي';
}

export function WorkspaceTopBar({
  metadata,
  apiStatus,
  lastSyncNote,
  projectId,
  onOpenStart,
  onDownloadSnapshot,
  onImportSnapshot,
  onNewProject,
}: WorkspaceTopBarProps) {
  const isOffline = apiStatus === 'offline';

  return (
    <header className="workspace-topbar">
      <div className="workspace-project-summary">
        <FolderOpen size={20} aria-hidden="true" />
        <span>
          <small>المشروع الحالي</small>
          <strong>{metadata.paperTitle || 'مشروع جديد'}</strong>
        </span>
        <span className="workspace-project-context">
          {metadata.subject || 'المادة'} · {metadata.grade || 'الصف'}
        </span>
      </div>

      <div className="workspace-sync-summary" title={lastSyncNote}>
        {isOffline ? <WifiOff size={18} /> : <Wifi size={18} />}
        <span>
          <small>حالة الاتصال</small>
          <strong>{connectionLabel(apiStatus)}</strong>
        </span>
        <span className={`workspace-sync-dot workspace-sync-${apiStatus}`} />
      </div>

      <div className="workspace-topbar-actions">
        <button
          type="button"
          className="workspace-icon-button"
          onClick={onDownloadSnapshot}
          disabled={!projectId || isOffline}
        >
          <Save size={18} />
          حفظ
        </button>
        <button type="button" className="workspace-primary-action" onClick={onNewProject}>
          <RefreshCcw size={18} />
          مشروع جديد
        </button>
        <details className="workspace-more-menu">
          <summary className="workspace-icon-button" aria-label="إجراءات إضافية">
            <MoreVertical size={18} />
            المزيد
          </summary>
          <div className="workspace-more-menu-panel">
            <button type="button" onClick={onOpenStart}>
              <FolderOpen size={17} />
              إدارة المشاريع
            </button>
            <label>
              <Upload size={17} />
              استيراد نسخة JSON
              <input
                type="file"
                accept="application/json,.json"
                onChange={(event) => onImportSnapshot(event.target.files?.[0] ?? null)}
              />
            </label>
            <button
              type="button"
              onClick={onDownloadSnapshot}
              disabled={!projectId || isOffline}
            >
              <Download size={17} />
              تصدير نسخة المشروع
            </button>
          </div>
        </details>
      </div>
    </header>
  );
}
