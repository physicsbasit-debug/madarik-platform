import { BookOpen, CheckCircle2, FileSearch, FolderOpen, Loader2, ShieldCheck, UploadCloud, Wifi } from 'lucide-react';
import type {
  ExtractedTextInfo,
  InitialExtractionStatus,
  PdfLayoutAssetInfo,
  ProjectMetadata,
  ProjectSession,
  QuestionItem,
  SchoolLogoInfo,
  UploadedFileInfo,
} from '../../types/project';
import { FileUploadStep } from '../file-upload/FileUploadStep';
import { ProjectLibraryPanel } from '../project-library/ProjectLibraryPanel';
import { ProjectSetupStep } from '../project-setup/ProjectSetupStep';

interface StartWorkspaceProps {
  metadata: ProjectMetadata;
  schoolLogo: SchoolLogoInfo | null;
  uploadedFile: UploadedFileInfo | null;
  extractedText: ExtractedTextInfo | null;
  layoutAssets: PdfLayoutAssetInfo[];
  questions: QuestionItem[];
  projects: ProjectSession[];
  currentProjectId: string | null;
  isLibraryLoading: boolean;
  isBusy: boolean;
  initialExtractionStatus: InitialExtractionStatus;
  lastSyncNote: string;
  onMetadataChange: (metadata: ProjectMetadata) => void;
  onLogoSelected: (file: File | null) => void;
  onLogoRemove: () => void;
  onFileSelected: (file: File | null) => void;
  onRetryInitialExtraction: () => void;
  onRefreshProjects: () => void;
  onOpenProject: (projectId: string) => void;
  onDeleteProject: (projectId: string) => void;
  onDeleteProjects: (projectIds: string[]) => void;
  onParseQuestions: () => void;
}

function statusClass(ready: boolean) {
  return ready ? 'is-ready' : 'is-pending';
}

export function StartWorkspace({
  metadata,
  schoolLogo,
  uploadedFile,
  extractedText,
  layoutAssets,
  questions,
  projects,
  currentProjectId,
  isLibraryLoading,
  isBusy,
  initialExtractionStatus,
  lastSyncNote,
  onMetadataChange,
  onLogoSelected,
  onLogoRemove,
  onFileSelected,
  onRetryInitialExtraction,
  onRefreshProjects,
  onOpenProject,
  onDeleteProject,
  onDeleteProjects,
  onParseQuestions,
}: StartWorkspaceProps) {
  const hasExtractedText = Boolean(extractedText?.text.trim());
  const activeQuestionCount = hasExtractedText
    ? questions.filter((question) => question.status !== 'deleted').length
    : 0;
  const canParseQuestions = Boolean(extractedText?.isTextBased && !isBusy);
  const reviewNeededCount = questions.filter(
    (question) => question.status === 'needs_review',
  ).length;

  return (
    <div className="workflow-panel-stack start-workspace start-workspace-redesign">
      <section className="start-overview-strip" aria-label="ملخص مشروع البدء والرفع">
        <article className="start-overview-item is-primary">
          <FolderOpen size={22} />
          <div>
            <span>المشروع الحالي</span>
            <strong>{metadata.paperTitle || 'مشروع جديد'}</strong>
          </div>
        </article>
        <article className="start-overview-item">
          <BookOpen size={22} />
          <div>
            <span>المادة والصف</span>
            <strong>{metadata.subject || 'غير محددة'} · {metadata.grade || 'غير محدد'}</strong>
          </div>
        </article>
        <article className="start-overview-item">
          <Wifi size={22} />
          <div>
            <span>وضع الاتصال</span>
            <strong>محلي على هذا الجهاز</strong>
          </div>
        </article>
        <article className="start-overview-item">
          <FileSearch size={22} />
          <div>
            <span>الأسئلة المستخرجة</span>
            <strong>{activeQuestionCount || '—'}</strong>
          </div>
        </article>
        <article className="start-overview-item">
          <ShieldCheck size={22} />
          <div>
            <span>تحتاج مراجعة</span>
            <strong>{reviewNeededCount || '—'}</strong>
          </div>
        </article>
      </section>
      <div className="start-workspace-grid">
        <div className="start-details-column">
          <ProjectSetupStep
            metadata={metadata}
            schoolLogo={schoolLogo}
            onChange={onMetadataChange}
            onLogoSelected={onLogoSelected}
            onLogoRemove={onLogoRemove}
          />
        </div>

        <div className="start-upload-column">
          <FileUploadStep
            uploadedFile={uploadedFile}
            extractedText={extractedText}
            layoutAssets={layoutAssets}
            onFileSelected={onFileSelected}
            canParseQuestions={canParseQuestions}
            isBusy={isBusy}
            initialExtractionStatus={initialExtractionStatus}
            onRetryInitialExtraction={onRetryInitialExtraction}
            onParseQuestions={onParseQuestions}
          />
        </div>

        <div className="start-library-column">
          <ProjectLibraryPanel
            projects={projects}
            currentProjectId={currentProjectId}
            isLoading={isLibraryLoading}
            onRefresh={onRefreshProjects}
            onOpenProject={onOpenProject}
            onDeleteProject={onDeleteProject}
            onDeleteProjects={onDeleteProjects}
          />
        </div>
      </div>

      <section className="start-analysis-card">
        <div className="start-analysis-heading">
          <div>
            <p className="eyebrow">حالة المعالجة</p>
            <h3>ماذا أنجز النظام؟</h3>
            <p>{lastSyncNote}</p>
          </div>
          {isBusy ? (
            <Loader2 size={28} className="spin-icon" />
          ) : (
            <FileSearch size={28} />
          )}
        </div>

        <div className="workflow-status-grid">
          <div className={statusClass(Boolean(uploadedFile))}>
            {uploadedFile ? (
              <CheckCircle2 size={20} />
            ) : (
              <UploadCloud size={20} />
            )}
            <span>رفع الملف</span>
            <strong>{uploadedFile ? 'مكتمل' : 'بانتظار الملف'}</strong>
          </div>
          <div className={statusClass(hasExtractedText)}>
            <CheckCircle2 size={20} />
            <span>استخراج النص</span>
            <strong>{hasExtractedText ? 'مكتمل' : 'غير مكتمل'}</strong>
          </div>
          <div className={statusClass(activeQuestionCount > 0)}>
            <CheckCircle2 size={20} />
            <span>الأسئلة المستخرجة</span>
            <strong>{activeQuestionCount}</strong>
          </div>
          <div className={statusClass(layoutAssets.length > 0)}>
            <CheckCircle2 size={20} />
            <span>الرسوم والجداول</span>
            <strong>{layoutAssets.length}</strong>
          </div>
        </div>

        <div className="start-primary-action">
          <button
            type="button"
            className="primary-button start-parse-button"
            onClick={onParseQuestions}
            disabled={!canParseQuestions}
          >
            {isBusy ? (
              <Loader2 size={18} className="spin-icon" />
            ) : (
              <FileSearch size={18} />
            )}
            استخراج الأسئلة من النص
          </button>
          <span>
            يتاح الاستخراج بعد اكتمال قراءة النص. ستجد أدوات التحليل التفصيلية
            داخل شاشة المراجعة.
          </span>
        </div>
      </section>
    </div>
  );
}
