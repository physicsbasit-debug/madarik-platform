import { FolderOpen, Loader2, RefreshCw, Trash2 } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import type { ProjectSession } from '../../types/project';

interface ProjectLibraryPanelProps {
  projects: ProjectSession[];
  currentProjectId: string | null;
  isLoading: boolean;
  onRefresh: () => void;
  onOpenProject: (projectId: string) => void;
  onDeleteProject: (projectId: string) => void;
  onDeleteProjects: (projectIds: string[]) => void;
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
  const activeQuestions = project.questions.filter(
    (question) => question.status !== 'deleted',
  ).length;
  const glossaryTerms = project.glossary.length;
  return `${activeQuestions} سؤال نشط · ${glossaryTerms} مصطلح`;
}

function ownerLabel(project: ProjectSession, currentProjectId: string | null) {
  if (!project.ownerAccountId) return 'مشروع غير مربوط بحساب';
  if (project.id === currentProjectId)
    return 'مربوط بالحساب الحالي أو متاح للمالك';
  return 'مشروع مملوك لحساب';
}

export function ProjectLibraryPanel({
  projects,
  currentProjectId,
  isLoading,
  onRefresh,
  onOpenProject,
  onDeleteProject,
  onDeleteProjects,
}: ProjectLibraryPanelProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const projectIds = useMemo(
    () => new Set(projects.map((project) => project.id)),
    [projects],
  );

  useEffect(() => {
    setSelectedIds((current) => {
      const next = new Set(
        [...current].filter((projectId) => projectIds.has(projectId)),
      );
      return next.size === current.size ? current : next;
    });
  }, [projectIds]);

  const allSelected =
    projects.length > 0 && selectedIds.size === projects.length;

  function toggleProject(projectId: string) {
    setSelectedIds((current) => {
      const next = new Set(current);
      if (next.has(projectId)) next.delete(projectId);
      else next.add(projectId);
      return next;
    });
  }

  function toggleAll() {
    setSelectedIds(
      allSelected ? new Set() : new Set(projects.map((project) => project.id)),
    );
  }

  function deleteSelected() {
    const selected = [...selectedIds];
    if (selected.length === 0) return;
    onDeleteProjects(selected);
  }

  return (
    <section className="project-library-panel">
      <div className="library-header">
        <div>
          <p className="eyebrow">المشاريع</p>
          <h3>مكتبة المشاريع المحفوظة</h3>
          <p>
            افتح مشروعًا سابقًا، أو حدّد عدة مشاريع لإدارتها دفعة واحدة.
          </p>
        </div>
        <div className="library-toolbar">
          <label className="library-select-all">
            <input
              type="checkbox"
              checked={allSelected}
              onChange={toggleAll}
              disabled={projects.length === 0 || isLoading}
            />
            تحديد الكل
          </label>
          <button
            type="button"
            className="danger-button compact"
            onClick={deleteSelected}
            disabled={selectedIds.size === 0 || isLoading}
          >
            <Trash2 size={16} />
            حذف المحدد ({selectedIds.size})
          </button>
          <button
            type="button"
            className="secondary-button compact"
            onClick={onRefresh}
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 size={16} className="spin-icon" />
            ) : (
              <RefreshCw size={16} />
            )}
            تحديث
          </button>
        </div>
      </div>

      {projects.length === 0 ? (
        <div className="empty-state library-empty library-empty-compact">
          <FolderOpen size={22} />
          <div>
            <strong>لا توجد مشاريع محفوظة</strong>
            <span>ابدأ مشروعًا جديدًا من الشريط العلوي أو ارفع أول ورقة.</span>
          </div>
        </div>
      ) : (
        <div className="library-list">
          {projects.map((project) => (
            <article
              key={project.id}
              className={`library-item ${
                project.id === currentProjectId ? 'current-project' : ''
              }`}
            >
              <label className="library-item-selection" aria-label="تحديد المشروع">
                <input
                  type="checkbox"
                  checked={selectedIds.has(project.id)}
                  onChange={() => toggleProject(project.id)}
                />
              </label>
              <div className="library-item-main">
                <strong>{project.metadata.paperTitle || 'مشروع بلا عنوان'}</strong>
                <span>
                  {project.metadata.subject || 'مادة غير محددة'} ·{' '}
                  {project.metadata.grade || 'صف غير محدد'}
                </span>
                <small>
                  {projectStats(project)} · آخر تحديث: {formatDate(project.updatedAt)}
                </small>
                <em>{ownerLabel(project, currentProjectId)}</em>
                {project.id === currentProjectId ? (
                  <em>المشروع المفتوح حاليًا</em>
                ) : null}
              </div>
              <div className="library-actions">
                <button
                  type="button"
                  className="primary-button compact"
                  onClick={() => onOpenProject(project.id)}
                  disabled={project.id === currentProjectId}
                >
                  <FolderOpen size={16} />
                  فتح
                </button>
                <button
                  type="button"
                  className="danger-button compact"
                  onClick={() => onDeleteProject(project.id)}
                >
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
