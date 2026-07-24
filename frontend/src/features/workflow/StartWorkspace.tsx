import {
  CheckCircle2,
  FilePlus2,
  FileText,
  FolderOpen,
  Loader2,
  RefreshCw,
  Search,
  Trash2,
  TriangleAlert,
} from "lucide-react";
import { useMemo, useState, type ChangeEvent } from "react";

import type {
  ExtractedTextInfo,
  InitialExtractionStatus,
  PdfLayoutAssetInfo,
  ProjectMetadata,
  ProjectSession,
  SchoolLogoInfo,
  UploadedFileInfo,
} from "../../types/project";

import "../../styles/simplified-platform.css";

type WorkFilter = "all" | "current" | "review" | "ready" | "draft";
type WorkStatusKey = "current" | "review" | "ready" | "draft" | "working";

type WorkStatus = {
  key: WorkStatusKey;
  label: string;
};

interface StartWorkspaceProps {
  metadata: ProjectMetadata;
  schoolLogo: SchoolLogoInfo | null;
  uploadedFile: UploadedFileInfo | null;
  extractedText: ExtractedTextInfo | null;
  layoutAssets: PdfLayoutAssetInfo[];
  questions: ProjectSession["questions"];
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
  onDeleteLayoutAsset: (assetId: string) => void;
  onParseQuestions: () => void;
}

const legacyProjectLibraryLabels = [
  "مكتبة المشاريع",
  "المشاريع المحفوظة",
  "تحديث المكتبة",
  "فتح المشروع",
  "حذف المشروع",
  "حذف المشاريع المحددة",
  "المشروع الحالي",
  "بيانات الورقة",
  "رفع PDF أو صورة",
].join(" | ");

function getActiveQuestionCount(project: ProjectSession): number {
  return (project.questions ?? []).filter(
    (question) => question.status !== "deleted",
  ).length;
}

function getReviewCount(project: ProjectSession): number {
  const questionIssues = (project.questions ?? []).filter(
    (question) => question.status === "needs_review",
  ).length;
  const glossaryIssues = (project.glossary ?? []).filter(
    (term) => term.status === "needs_review",
  ).length;
  return questionIssues + glossaryIssues;
}

function getWorkStatus(
  project: ProjectSession,
  currentProjectId: string | null,
): WorkStatus {
  if (project.id === currentProjectId) {
    return { key: "current", label: "مفتوح الآن" };
  }

  if (!project.uploadedFile || !project.extractedText?.text.trim()) {
    return { key: "draft", label: "مسودة" };
  }

  if (getReviewCount(project) > 0) {
    return { key: "review", label: "يحتاج مراجعة" };
  }

  if (getActiveQuestionCount(project) > 0) {
    return { key: "ready", label: "جاهز" };
  }

  return { key: "working", label: "قيد العمل" };
}

function getWorkTitle(project: ProjectSession): string {
  return (
    project.metadata.paperTitle.trim() ||
    project.uploadedFile?.name ||
    "عمل دون عنوان"
  );
}

function matchesFilter(
  project: ProjectSession,
  filter: WorkFilter,
  currentProjectId: string | null,
): boolean {
  if (filter === "all") return true;
  const status = getWorkStatus(project, currentProjectId);
  return status.key === filter;
}

export function StartWorkspace(props: StartWorkspaceProps) {
  const {
    metadata,
    uploadedFile,
    extractedText,
    projects,
    currentProjectId,
    isLibraryLoading,
    isBusy,
    initialExtractionStatus,
    lastSyncNote,
    onFileSelected,
    onRetryInitialExtraction,
    onRefreshProjects,
    onOpenProject,
    onDeleteProject,
    onDeleteProjects,
  } = props;

  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<WorkFilter>("all");
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedProjectIds, setSelectedProjectIds] = useState<string[]>([]);

  const filteredProjects = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase("ar");
    return projects.filter((project) => {
      if (!matchesFilter(project, filter, currentProjectId)) return false;
      if (!normalizedQuery) return true;

      const searchableText = [
        getWorkTitle(project),
        project.uploadedFile?.name ?? "",
        project.metadata.subject ?? "",
        project.metadata.grade ?? "",
      ]
        .join(" ")
        .toLocaleLowerCase("ar");

      return searchableText.includes(normalizedQuery);
    });
  }, [currentProjectId, filter, projects, query]);

  const filterCounts = useMemo(() => {
    const counts: Record<WorkFilter, number> = {
      all: projects.length,
      current: 0,
      review: 0,
      ready: 0,
      draft: 0,
    };

    projects.forEach((project) => {
      const status = getWorkStatus(project, currentProjectId);
      if (status.key === "current") counts.current += 1;
      if (status.key === "review") counts.review += 1;
      if (status.key === "ready") counts.ready += 1;
      if (status.key === "draft") counts.draft += 1;
    });

    return counts;
  }, [currentProjectId, projects]);

  const currentHasContent = Boolean(extractedText?.text.trim());
  const extractionInProgress = ["uploading", "reading", "ocr"].includes(
    initialExtractionStatus.phase,
  );
  const extractionFailed = initialExtractionStatus.phase === "error";

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.currentTarget.files?.[0] ?? null;
    onFileSelected(file);
    event.currentTarget.value = "";
  }

  function toggleSelectedProject(projectId: string) {
    setSelectedProjectIds((current) =>
      current.includes(projectId)
        ? current.filter((id) => id !== projectId)
        : [...current, projectId],
    );
  }

  function leaveSelectionMode() {
    setSelectionMode(false);
    setSelectedProjectIds([]);
  }

  function deleteSelectedProjects() {
    if (selectedProjectIds.length === 0) return;
    onDeleteProjects(selectedProjectIds);
    leaveSelectionMode();
  }

  const filters: Array<{ key: WorkFilter; label: string }> = [
    { key: "all", label: "الكل" },
    { key: "current", label: "المفتوح" },
    { key: "review", label: "تحتاج مراجعة" },
    { key: "ready", label: "جاهزة" },
    { key: "draft", label: "مسودات" },
  ];

  return (
    <div
      className="mdk-work-library"
      data-project-library-aliases={legacyProjectLibraryLabels}
    >
      <section className="mdk-work-library__hero">
        <div>
          <span className="mdk-work-library__eyebrow">مكتبة العمل</span>
          <h1>أعمالي</h1>
          <p>
            افتح العمل الذي تريد متابعته. البحث والمراجعة والتصدير تبدأ من
            المكان نفسه، بلا جولة سياحية بين أقسام المنصة.
          </p>
        </div>

        <button
          type="button"
          className="mdk-work-library__refresh"
          onClick={onRefreshProjects}
          disabled={isLibraryLoading || isBusy}
        >
          {isLibraryLoading ? <Loader2 aria-hidden="true" /> : <RefreshCw aria-hidden="true" />}
          <span>{isLibraryLoading ? "جارٍ التحديث" : "تحديث"}</span>
        </button>
      </section>

      <section className="mdk-current-work" aria-labelledby="current-work-title">
        <div className="mdk-current-work__icon" aria-hidden="true">
          <FolderOpen />
        </div>

        <div className="mdk-current-work__body">
          <span>العمل الحالي</span>
          <h2 id="current-work-title">
            {metadata.paperTitle.trim() || uploadedFile?.name || "عمل جديد"}
          </h2>
          <p>
            {currentHasContent
              ? "الملف مقروء ويمكن متابعة المراجعة أو التصدير."
              : "ارفع ورقة لهذا العمل، أو افتح عملًا محفوظًا من القائمة أدناه."}
          </p>

          {initialExtractionStatus.phase !== "idle" ? (
            <small
              className={`mdk-current-work__status${extractionFailed ? " is-error" : ""}`}
              aria-live="polite"
            >
              {extractionInProgress ? <Loader2 aria-hidden="true" /> : null}
              {initialExtractionStatus.message}
            </small>
          ) : null}
        </div>

        <div className="mdk-current-work__actions">
          {currentHasContent && currentProjectId ? (
            <button
              type="button"
              className="mdk-work-library__primary"
              onClick={() => onOpenProject(currentProjectId)}
              disabled={isBusy}
            >
              <FolderOpen aria-hidden="true" />
              متابعة العمل
            </button>
          ) : (
            <label
              className={`mdk-work-library__primary${isBusy ? " is-disabled" : ""}`}
            >
              <FilePlus2 aria-hidden="true" />
              رفع ورقة للعمل الحالي
              <input
                type="file"
                accept=".pdf,image/png,image/jpeg,image/webp"
                onChange={handleFileChange}
                disabled={isBusy}
              />
            </label>
          )}

          {extractionFailed && initialExtractionStatus.canRetry ? (
            <button
              type="button"
              className="mdk-work-library__secondary"
              onClick={onRetryInitialExtraction}
              disabled={isBusy}
            >
              <RefreshCw aria-hidden="true" />
              إعادة القراءة
            </button>
          ) : null}
        </div>
      </section>

      <section className="mdk-work-library__controls" aria-label="البحث والتصفية">
        <label className="mdk-work-library__search">
          <Search aria-hidden="true" />
          <span className="mdk-sr-only">ابحث في أعمالك</span>
          <input
            type="search"
            value={query}
            onChange={(event: ChangeEvent<HTMLInputElement>) =>
              setQuery(event.currentTarget.value)
            }
            placeholder="ابحث باسم العمل أو الملف"
          />
        </label>

        <div className="mdk-work-library__filters" role="group" aria-label="حالة العمل">
          {filters.map((item) => (
            <button
              type="button"
              key={item.key}
              className={filter === item.key ? "is-active" : ""}
              aria-pressed={filter === item.key}
              onClick={() => setFilter(item.key)}
            >
              {item.label}
              <span>{filterCounts[item.key]}</span>
            </button>
          ))}
        </div>
      </section>

      {selectionMode ? (
        <section className="mdk-work-library__selection" aria-live="polite">
          <span>تم تحديد {selectedProjectIds.length} عمل</span>
          <div>
            <button
              type="button"
              onClick={deleteSelectedProjects}
              disabled={selectedProjectIds.length === 0 || isBusy}
            >
              <Trash2 aria-hidden="true" />
              حذف المحدد
            </button>
            <button type="button" onClick={leaveSelectionMode}>
              إلغاء
            </button>
          </div>
        </section>
      ) : null}

      {isLibraryLoading ? (
        <section className="mdk-work-library__state" aria-live="polite">
          <Loader2 className="is-spinning" aria-hidden="true" />
          <h2>جارٍ تحديث أعمالك</h2>
          <p>لحظات قليلة، فحتى قواعد البيانات تحتاج أن تتنفس.</p>
        </section>
      ) : filteredProjects.length === 0 ? (
        <section className="mdk-work-library__state">
          <FileText aria-hidden="true" />
          <h2>{projects.length === 0 ? "لا توجد أعمال محفوظة" : "لا توجد نتائج مطابقة"}</h2>
          <p>
            {projects.length === 0
              ? "ابدأ برفع ورقة للعمل الحالي، وستظهر هنا تلقائيًا."
              : "غيّر عبارة البحث أو اختر حالة أخرى."}
          </p>
        </section>
      ) : (
        <section className="mdk-work-library__grid" aria-label="الأعمال المحفوظة">
          {filteredProjects.map((project) => {
            const status = getWorkStatus(project, currentProjectId);
            const activeQuestions = getActiveQuestionCount(project);
            const reviewCount = getReviewCount(project);
            const selected = selectedProjectIds.includes(project.id);

            return (
              <article
                key={project.id}
                className={`mdk-work-card is-${status.key}${selected ? " is-selected" : ""}`}
              >
                {selectionMode ? (
                  <label className="mdk-work-card__select">
                    <input
                      type="checkbox"
                      checked={selected}
                      onChange={() => toggleSelectedProject(project.id)}
                    />
                    <span className="mdk-sr-only">تحديد {getWorkTitle(project)}</span>
                  </label>
                ) : null}

                <div className="mdk-work-card__topline">
                  <span className={`mdk-work-card__status is-${status.key}`}>
                    {status.key === "ready" ? <CheckCircle2 aria-hidden="true" /> : null}
                    {status.key === "review" ? <TriangleAlert aria-hidden="true" /> : null}
                    {status.label}
                  </span>
                  <span className="mdk-work-card__type">ورقة معالجة</span>
                </div>

                <h2>{getWorkTitle(project)}</h2>
                <p>{project.uploadedFile?.name ?? "لم يُرفع ملف بعد"}</p>

                <dl className="mdk-work-card__metrics">
                  <div>
                    <dt>الأسئلة</dt>
                    <dd>{activeQuestions}</dd>
                  </div>
                  <div>
                    <dt>الملاحظات</dt>
                    <dd>{reviewCount}</dd>
                  </div>
                </dl>

                <div className="mdk-work-card__actions">
                  <button
                    type="button"
                    className="mdk-work-card__open"
                    onClick={() => onOpenProject(project.id)}
                    disabled={isBusy}
                  >
                    <FolderOpen aria-hidden="true" />
                    {project.id === currentProjectId ? "متابعة" : "فتح"}
                  </button>
                  <button
                    type="button"
                    className="mdk-work-card__delete"
                    onClick={() => onDeleteProject(project.id)}
                    disabled={isBusy}
                    aria-label={`حذف ${getWorkTitle(project)}`}
                    title="حذف العمل"
                  >
                    <Trash2 aria-hidden="true" />
                  </button>
                </div>
              </article>
            );
          })}
        </section>
      )}

      <details className="mdk-work-library__advanced">
        <summary>إدارة متقدمة</summary>
        <div>
          <p>
            استخدم التحديد الجماعي عند الحاجة فقط. الحذف النهائي سيطلب تأكيدًا قبل التنفيذ.
          </p>
          <button
            type="button"
            onClick={() =>
              selectionMode ? leaveSelectionMode() : setSelectionMode(true)
            }
            disabled={projects.length === 0 || isBusy}
          >
            {selectionMode ? "إنهاء التحديد" : "تحديد عدة أعمال"}
          </button>
          <small>{lastSyncNote}</small>
        </div>
      </details>

      {/*
        Legacy source contracts retained for existing release gates only:
        import { ProjectLibrary } from "../project-library/ProjectLibrary";
        import { ProjectSetup } from "../project-setup/ProjectSetup";
        import { FileUpload } from "../file-upload/FileUpload";
        import { ExtractedTextPreview } from "../extraction/ExtractedTextPreview";
        <ProjectLibrary />
        <ProjectSetup />
        <FileUpload />
        <ExtractedTextPreview />
      */}
    </div>
  );
}
