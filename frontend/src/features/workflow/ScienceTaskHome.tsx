import {
  ArrowLeft,
  BookOpenText,
  BrainCircuit,
  CheckCircle2,
  Cloud,
  FileStack,
  LibraryBig,
  Network,
  Upload,
  WandSparkles,
  X,
} from "lucide-react";
import { useState } from "react";
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

function providerLabel(status: TranslationProviderStatus | null) {
  if (!status?.configured) return "الترجمة غير مهيأة";
  if (status.ready === false) return "الترجمة تحتاج مراجعة";
  return "الترجمة جاهزة";
}

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
  const [sourceChooserOpen, setSourceChooserOpen] = useState(false);
  const reviewCount = needsReviewCount + glossaryNeedsReview;
  const readinessText = projectReadiness
    ? projectReadiness.ready
      ? "جاهز للتصدير"
      : `${projectReadiness.issues.length} ملاحظة تحتاج مراجعة`
    : reviewCount > 0
      ? `${reviewCount} ملاحظة تحتاج مراجعة`
      : "جاهز للمتابعة";

  return (
    <div className="mdk-simple-home">
      <section className="mdk-simple-home-hero">
        <div>
          <span className="mdk-simple-eyebrow">ابدأ من المهمة، لا من إعدادات النظام</span>
          <h1>ماذا تريد أن تنجز اليوم؟</h1>
          <p>
            اختر المهمة، ودع مدارك تتولى الخطوات التقنية تلقائيًا. نعم، البرنامج
            يستطيع العمل من دون أن يطلب من المعلم شهادة في هندسة المفاعلات.
          </p>
        </div>
        <div className="mdk-simple-home-status">
          <CheckCircle2 size={22} />
          <div>
            <strong>{providerLabel(translationProviderStatus)}</strong>
            <small>{apiStatus === "offline" ? "وضع محلي" : "الحفظ التلقائي يعمل"}</small>
          </div>
        </div>
      </section>

      <section className="mdk-simple-primary-tasks" aria-label="المهام الرئيسية">
        <button
          type="button"
          className="mdk-simple-task-card is-primary"
          onClick={() => setSourceChooserOpen(true)}
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

      <section className="mdk-simple-resume-card">
        <div className="mdk-simple-resume-card__main">
          <span className="mdk-simple-eyebrow">أكمل من حيث توقفت</span>
          <h2>{metadata.paperTitle || "العمل الحالي"}</h2>
          <p>
            {uploadedFile?.name
              ? `الملف الحالي: ${uploadedFile.name}`
              : "لا يوجد ملف مرفوع بعد. يمكنك بدء معالجة ورقة أو فتح عمل محفوظ."}
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
            <button
              type="button"
              className="mdk-simple-secondary-button"
              onClick={onOpenQuestionBank}
            >
              فتح بنك الأسئلة
            </button>
          </div>
        </div>

        <div className="mdk-simple-resume-metrics">
          <div>
            <strong>{projectCount}</strong>
            <span>أعمال محفوظة</span>
          </div>
          <div>
            <strong>{activeQuestionCount}</strong>
            <span>سؤالًا في العمل</span>
          </div>
          <div className={reviewCount > 0 ? "needs-attention" : undefined}>
            <strong>{reviewCount}</strong>
            <span>تحتاج مراجعة</span>
          </div>
          <div>
            <strong>{approvedCount}</strong>
            <span>معتمدة</span>
          </div>
        </div>

        <div className="mdk-simple-readiness">
          <CheckCircle2 size={20} />
          <span>{readinessText}</span>
        </div>
      </section>

      <section className="mdk-simple-secondary-section">
        <div className="mdk-simple-section-heading">
          <div>
            <span className="mdk-simple-eyebrow">أدوات مساندة</span>
            <h2>افتحها عند الحاجة فقط</h2>
          </div>
        </div>

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
      </section>

      {sourceChooserOpen ? (
        <div className="mdk-simple-modal-layer" role="dialog" aria-modal="true">
          <button
            type="button"
            className="mdk-simple-mobile-backdrop"
            onClick={() => setSourceChooserOpen(false)}
            aria-label="إغلاق"
          />
          <section className="mdk-simple-source-dialog">
            <header>
              <div>
                <span className="mdk-simple-eyebrow">معالجة ورقة جاهزة</span>
                <h2>من أين تريد اختيار الملف؟</h2>
              </div>
              <button
                type="button"
                className="mdk-simple-icon-button"
                onClick={() => setSourceChooserOpen(false)}
                aria-label="إغلاق"
              >
                <X size={20} />
              </button>
            </header>

            <div className="mdk-simple-source-options">
              <button
                type="button"
                onClick={() => {
                  setSourceChooserOpen(false);
                  onQuickTranslation();
                }}
              >
                <Upload size={25} />
                <span>
                  <strong>من الجهاز</strong>
                  <small>PDF أو صورة</small>
                </span>
                <ArrowLeft size={19} />
              </button>
              <button
                type="button"
                onClick={() => {
                  setSourceChooserOpen(false);
                  onOpenCloudSources();
                }}
              >
                <Cloud size={25} />
                <span>
                  <strong>Google Drive</strong>
                  <small>اختر ملفًا من حسابك</small>
                </span>
                <ArrowLeft size={19} />
              </button>
              <button
                type="button"
                onClick={() => {
                  setSourceChooserOpen(false);
                  onOpenCloudSources();
                }}
              >
                <Cloud size={25} />
                <span>
                  <strong>OneDrive</strong>
                  <small>اختر ملفًا من Microsoft</small>
                </span>
                <ArrowLeft size={19} />
              </button>
            </div>
          </section>
        </div>
      ) : null}
    </div>
  );
}
