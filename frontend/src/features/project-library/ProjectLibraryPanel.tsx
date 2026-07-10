import { FolderOpen, Loader2, RefreshCw, Trash2 } from 'lucide-react';
import type { ProjectSession } from '../../types/project';

interface ProjectLibraryPanelProps {
  projects: ProjectSession[];
  currentProjectId: string | null;
  isLoading: boolean;
  onRefresh: () => void;
  onOpenProject: (projectId: string) => void;
  onDeleteProject: (projectId: string) => void;
}

function formatDate(value: string | undefined) {
  if (!value) return 'غير معروف';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return 'غير معروف';
  return new Intl.DateTimeFormat('ar-OM', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(parsed);
}

function projectStats(project: ProjectSession) {
  const activeQuestions = project.questions.filter((question) => question.status !== 'deleted').length;
  const glossaryTerms = project.glossary.length;
  return `${activeQuestions} سؤال نشط · ${glossaryTerms} مصطلح`;
}

function ownerLabel(project: ProjectSession, currentProjectId: string | null) {
  if (!project.ownerAccountId) return 'مشروع غير مربوط بحساب';
  if (project.id === currentProjectId) return 'مربوط بالحساب الحالي أو متاح للمالك';
  return 'مشروع مملوك لحساب';
}

export function ProjectLibraryPanel({
  projects,
  currentProjectId,
  isLoading,
  onRefresh,
  onOpenProject,
  onDeleteProject,
}: ProjectLibraryPanelProps) {
  return (
    <section className="project-library-panel">
      <div className="library-header">
        <div>
          <p className="eyebrow">Phase 2-A2</p>
          <h3>مكتبة المشاريع المحفوظة</h3>
          <p>تعرض المشاريع المحفوظة في SQLite. افتح مشروعًا سابقًا أو احذف مشروعًا قديمًا. أخيرًا صار عندنا رف، لا كومة أوراق على الطاولة.</p>
        </div>
        <button type="button" className="secondary-button compact" onClick={onRefresh} disabled={isLoading}>
          {isLoading ? <Loader2 size={16} className="spin-icon" /> : <RefreshCw size={16} />}
          تحديث المكتبة
        </button>
      </div>

      {projects.length === 0 ? (
        <div className="empty-state library-empty">
          لا توجد مشاريع محفوظة بعد. أنشئ مشروعًا أو استورد نسخة JSON، وسيظهر هنا بدل أن يتبخر مثل وعود البرامج المجانية.
        </div>
      ) : (
        <div className="library-list">
          {projects.map((project) => (
            <article key={project.id} className={`library-item ${project.id === currentProjectId ? 'current-project' : ''}`}>
              <div className="library-item-main">
                <strong>{project.metadata.paperTitle || 'مشروع بلا عنوان'}</strong>
                <span>{project.metadata.subject || 'مادة غير محددة'} · {project.metadata.grade || 'صف غير محدد'}</span>
                <small>{projectStats(project)} · آخر تحديث: {formatDate(project.updatedAt)}</small>
                <em>{ownerLabel(project, currentProjectId)}</em>
                {project.id === currentProjectId ? <em>المشروع المفتوح حاليًا</em> : null}
              </div>
              <div className="library-actions">
                <button type="button" className="primary-button compact" onClick={() => onOpenProject(project.id)} disabled={project.id === currentProjectId}>
                  <FolderOpen size={16} />
                  فتح
                </button>
                <button type="button" className="danger-button compact" onClick={() => onDeleteProject(project.id)}>
                  <Trash2 size={16} />
                  حذف
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
