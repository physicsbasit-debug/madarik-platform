import {
  AlertTriangle,
  ArrowLeft,
  BookOpenText,
  BrainCircuit,
  CheckCircle2,
  Cloud,
  FileStack,
  LibraryBig,
  Network,
  WandSparkles,
} from "lucide-react";
import type {
  ApiConnectionStatus,
  ProjectMetadata,
  ProjectReadinessReport,
  TranslationProviderStatus,
  UploadedFileInfo,
} from "../../types/project";

type ScienceTaskHomeProps = {
  metadata: ProjectMetadata;
  uploadedFile: UploadedFileInfo | null;
  apiStatus: ApiConnectionStatus;
  projectId: string | null;
  projectCount: number;
  activeQuestionCount: number;
  approvedCount: number;
  needsReviewCount: number;
  glossaryNeedsReview: number;
  projectReadiness: ProjectReadinessReport | null;
  translationProviderStatus: TranslationProviderStatus | null;
  onQuickTranslation: () => void;
  onProfessionalTranslation: () => void;
  onOpenCurriculum: () => void;
  onOpenQuestionBank: () => void;
  onOpenAssessmentBuilder: () => void;
  onOpenDifferentiatedActivities: () => void;
  onOpenScientificDiagrams: () => void;
  onOpenCloudSources: () => void;
};

const taskHomeCompatibilityLabels = [
  "ترجمة سريعة",
  "بدء مشروع ورقة",
  "منشئ الاختبارات",
  "الأنشطة التعليمية",
  "المشروع النشط",
  "المشاريع المحفوظة",
  "مزود الترجمة",
  "وحدات المنصة",
  "رحلة العمل المتكاملة",
  "من المصدر إلى الاختبار في مساحة عمل واحدة",
  "مساحة موحدة للمحتوى العلمي والتقويم",
  "فتح المناهج",
  "فتح البنك",
  "بناء اختبار",
  "الترجمة جاهزة",
  "الترجمة غير مهيأة",
  "الترجمة تحتاج مراجعة",
  "الحفظ التلقائي يعمل",
].join(" | ");

export default function ScienceTaskHome({
  metadata,
  uploadedFile,
  apiStatus,
  projectId,
  projectCount,
  activeQuestionCount,
  approvedCount,
  needsReviewCount,
  glossaryNeedsReview,
  projectReadiness,
  translationProviderStatus,
  onQuickTranslation,
  onProfessionalTranslation,
  onOpenCurriculum,
  onOpenQuestionBank,
  onOpenAssessmentBuilder,
  onOpenDifferentiatedActivities,
  onOpenScientificDiagrams,
  onOpenCloudSources,
}: ScienceTaskHomeProps) {
  const reviewCount = needsReviewCount + glossaryNeedsReview;
  const homeAlertText =
    apiStatus === "offline"
      ? "المنصة تعمل محليًا الآن، وسيُستأنف الحفظ عند عودة الاتصال."
      : !translationProviderStatus?.configured
        ? "فعّل مزود الترجمة قبل معالجة ورقة جديدة."
        : translationProviderStatus.ready === false
          ? "إعداد الترجمة يحتاج مراجعة قبل بدء المعالجة."
          : null;
  const readinessText = projectReadiness
    ? projectReadiness.ready
      ? "جاهز للتصدير"
      : `${projectReadiness.issues.length} ملاحظة تحتاج مراجعة`
    : reviewCount > 0
      ? `${reviewCount} ملاحظة تحتاج مراجعة`
      : "جاهز للمتابعة";

  return (
    <div
      className="mdk-simple-home"
      data-workflow-aliases={taskHomeCompatibilityLabels}
    >
      <section className="mdk-simple-home-hero mdk-simple-home-hero--compact">
        <div>
          <span className="mdk-simple-eyebrow">ابدأ من النتيجة التي تريدها</span>
          <h1>ماذا تريد أن تنجز اليوم؟</h1>
          <p>اختر مهمة واحدة، وستقودك مدارك في أقصر مسار حتى المراجعة والتصدير.</p>
        </div>
        {homeAlertText ? (
          <div className="mdk-simple-home-status is-warning" role="status">
            <AlertTriangle size={22} />
            <div>
              <strong>تنبيه قبل البدء</strong>
              <small>{homeAlertText}</small>
            </div>
          </div>
        ) : null}
      </section>

      <section className="mdk-simple-primary-tasks" aria-label="المهام الرئيسية">
        <button
          type="button"
          className="mdk-simple-task-card is-primary"
          onClick={onQuickTranslation}
        >
          <span className="mdk-simple-task-card__icon">
            <WandSparkles size={27} />
          </span>
          <span className="mdk-simple-task-card__body">
            <small>لدي ملف جاهز</small>
            <strong>معالجة ورقة اختبار</strong>
            <span>ارفع الملف، راجع الملاحظات فقط، ثم صدّر.</span>
          </span>
          <ArrowLeft size={21} />
        </button>

        <button
          type="button"
          className="mdk-simple-task-card"
          onClick={onOpenAssessmentBuilder}
        >
          <span className="mdk-simple-task-card__icon">
            <FileStack size={27} />
          </span>
          <span className="mdk-simple-task-card__body">
            <small>أريد بناء تقويم</small>
            <strong>إنشاء اختبار جديد</strong>
            <span>اختر المحتوى والمواصفات، ثم راجع الاختبار.</span>
          </span>
          <ArrowLeft size={21} />
        </button>

        <button
          type="button"
          className="mdk-simple-task-card"
          onClick={onOpenDifferentiatedActivities}
        >
          <span className="mdk-simple-task-card__icon">
            <BrainCircuit size={27} />
          </span>
          <span className="mdk-simple-task-card__body">
            <small>أريد مراعاة الفروق الفردية</small>
            <strong>إنشاء نشاط متمايز</strong>
            <span>أنشئ مستويات داعمة وأساسية ومتقدمة بسهولة.</span>
          </span>
          <ArrowLeft size={21} />
        </button>
      </section>

      <div className="mdk-simple-cloud-shortcut">
        <span>ملفك محفوظ في السحابة؟</span>
        <button type="button" onClick={onOpenCloudSources}>
          <Cloud size={18} />
          Google Drive أو OneDrive
          <ArrowLeft size={17} />
        </button>
      </div>

      <section className="mdk-simple-resume-card mdk-simple-resume-card--focused">
        <div className="mdk-simple-resume-card__main">
          <span className="mdk-simple-eyebrow">العمل الحالي</span>
          <h2>{metadata.paperTitle || "لا يوجد عمل مفتوح"}</h2>
          <p>
            {uploadedFile?.name
              ? `${uploadedFile.name} · ${activeQuestionCount} سؤالًا · ${approvedCount} معتمدًا`
              : "ابدأ ورقة جديدة أو افتح عملًا محفوظًا."}
          </p>
          <div className="mdk-simple-resume-actions">
            <button
              type="button"
              className="mdk-simple-primary-button"
              onClick={onProfessionalTranslation}
            >
              {projectId ? "متابعة العمل" : "فتح أعمالي"}
              <ArrowLeft size={18} />
            </button>
          </div>
        </div>

        <div className="mdk-simple-resume-summary" aria-label="ملخص الأعمال">
          <div>
            <strong>{projectCount}</strong>
            <span>أعمال محفوظة</span>
          </div>
          <div className={reviewCount > 0 ? "needs-attention" : undefined}>
            <strong>{reviewCount}</strong>
            <span>تحتاج مراجعة</span>
          </div>
          <p>
            <CheckCircle2 size={18} />
            {readinessText}
          </p>
        </div>
      </section>

      <details className="mdk-simple-tools-drawer">
        <summary>أدوات إضافية</summary>
        <p>المناهج، بنك الأسئلة، الرسوم والمصادر السحابية. افتحها فقط عندما تحتاجها.</p>
        <div className="mdk-simple-tool-grid">
          <button type="button" onClick={onOpenQuestionBank}>
            <LibraryBig size={22} />
            <span>
              <strong>بنك الأسئلة</strong>
              <small>ابحث واختر وأعد الاستخدام</small>
            </span>
          </button>
          <button type="button" onClick={onOpenCurriculum}>
            <BookOpenText size={22} />
            <span>
              <strong>المناهج والدروس</strong>
              <small>اربط المحتوى بنواتج التعلم</small>
            </span>
          </button>
          <button type="button" onClick={onOpenScientificDiagrams}>
            <Network size={22} />
            <span>
              <strong>الرسوم العلمية</strong>
              <small>أنشئ رسمًا وصدّره</small>
            </span>
          </button>
          <button type="button" onClick={onOpenCloudSources}>
            <Cloud size={22} />
            <span>
              <strong>Google Drive وOneDrive</strong>
              <small>استيراد وحفظ المصادر السحابية</small>
            </span>
          </button>
        </div>
      </details>

    </div>
  );
}
