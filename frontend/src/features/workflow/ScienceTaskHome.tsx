import {
  ArrowLeft,
  BadgeCheck,
  BookOpenText,
  BrainCircuit,
  CheckCircle2,
  Cloud,
  FileStack,
  FlaskConical,
  Gauge,
  LibraryBig,
  Network,
  Sparkles,
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

type ModuleCard = {
  title: string;
  description: string;
  eyebrow: string;
  actionLabel: string;
  icon: typeof Gauge;
  onOpen: () => void;
  tone: string;
};

function providerLabel(status: TranslationProviderStatus | null) {
  if (!status?.configured) return "غير مهيأ";
  if (status.ready === false) return "يحتاج مراجعة";
  return status.provider === "gemini" ? "Gemini جاهز" : "مزود خارجي جاهز";
}

function connectionLabel(status: ApiConnectionStatus) {
  if (status === "connected") return "متصل بالخلفية";
  if (status === "syncing") return "جارٍ حفظ التغييرات";
  if (status === "connecting") return "جارٍ تهيئة الجلسة";
  return "وضع محلي مؤقت";
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
  const moduleCards: ModuleCard[] = [
    {
      title: "المصادر السحابية",
      description:
        "اربط Google Drive وOneDrive، راجع سجل النسخ، وأدخل المصدر المعتمد مباشرة إلى المشروع.",
      eyebrow: "المحتوى",
      actionLabel: "فتح المصادر",
      icon: Cloud,
      onOpen: onOpenCloudSources,
      tone: "cloud",
    },
    {
      title: "المناهج والدروس",
      description:
        "تصفح الصفوف والفصول والوحدات والدروس واربط الأسئلة بنواتج التعلم المناسبة.",
      eyebrow: "التنظيم",
      actionLabel: "فتح المناهج",
      icon: BookOpenText,
      onOpen: onOpenCurriculum,
      tone: "curriculum",
    },
    {
      title: "بنك الأسئلة",
      description:
        "استرجع الأسئلة المعتمدة، صفّها حسب المنهج والتصنيف المعرفي، وأعد استخدامها بثقة.",
      eyebrow: "إعادة الاستخدام",
      actionLabel: "فتح البنك",
      icon: LibraryBig,
      onOpen: onOpenQuestionBank,
      tone: "bank",
    },
    {
      title: "منشئ الاختبارات",
      description:
        "ابنِ اختبارًا منظمًا، راجع جدول المواصفات، ثم أنشئ نسخة طالب قابلة للطباعة.",
      eyebrow: "التقويم",
      actionLabel: "بناء اختبار",
      icon: FileStack,
      onOpen: onOpenAssessmentBuilder,
      tone: "assessment",
    },
    {
      title: "الأنشطة التعليمية",
      description:
        "أنشئ أنشطة دعم وأساسية ومتقدمة وإثرائية من نفس المحتوى العلمي.",
      eyebrow: "التمايز",
      actionLabel: "إنشاء نشاط",
      icon: BrainCircuit,
      onOpen: onOpenDifferentiatedActivities,
      tone: "activities",
    },
    {
      title: "الرسوم العلمية",
      description:
        "صمّم مخططات ورسومًا علمية منظمة ثم صدّرها بصيغ SVG وPNG وPDF.",
      eyebrow: "التمثيل البصري",
      actionLabel: "فتح الاستوديو",
      icon: Network,
      onOpen: onOpenScientificDiagrams,
      tone: "diagrams",
    },
  ];

  const activeProjectTitle = metadata.paperTitle || "مشروع ورقة جديد";
  const readinessLabel = projectReadiness
    ? projectReadiness.ready
      ? "جاهز للتصدير"
      : `${projectReadiness.issues.length} ملاحظة قبل التصدير`
    : "لم يُفحص بعد";

  return (
    <div className="platform-dashboard">
      <section className="platform-dashboard-hero">
        <div className="platform-dashboard-hero-copy">
          <span className="platform-dashboard-kicker">
            <FlaskConical size={18} />
            منصة موحدة لبناء المحتوى العلمي
          </span>
          <h1>من المصدر إلى الاختبار، كل العمل في مساحة واحدة.</h1>
          <p>
            اجمع المحتوى، عالج أوراق الاختبارات، راجع الترجمة، اربط الأسئلة
            بالمنهج، ثم حوّلها إلى اختبارات وأنشطة ورسوم قابلة للاستخدام.
          </p>
          <div className="platform-dashboard-hero-actions">
            <button
              type="button"
              className="platform-dashboard-primary-action"
              onClick={onProfessionalTranslation}
            >
              <FileStack size={19} />
              {projectId ? "فتح المشروع الحالي" : "بدء مشروع ورقة"}
              <ArrowLeft size={17} />
            </button>
            <button
              type="button"
              className="platform-dashboard-secondary-action"
              onClick={onQuickTranslation}
            >
              <WandSparkles size={19} />
              ترجمة سريعة
            </button>
          </div>
        </div>

        <div className="platform-active-project-card">
          <div className="platform-active-project-heading">
            <span>
              <Sparkles size={18} />
              المشروع النشط
            </span>
            <strong className={projectId ? "is-live" : ""}>
              {projectId ? "جلسة محفوظة" : "جلسة جديدة"}
            </strong>
          </div>
          <h2>{activeProjectTitle}</h2>
          <p>
            {metadata.subject || "العلوم"} · {metadata.grade || "الصف غير محدد"}
            {metadata.semester ? ` · ${metadata.semester}` : ""}
          </p>
          <dl className="platform-active-project-details">
            <div>
              <dt>الملف</dt>
              <dd>{uploadedFile?.name ?? "لم يُرفع ملف بعد"}</dd>
            </div>
            <div>
              <dt>الأسئلة النشطة</dt>
              <dd>{activeQuestionCount}</dd>
            </div>
            <div>
              <dt>حالة التصدير</dt>
              <dd>{readinessLabel}</dd>
            </div>
          </dl>
          <button type="button" onClick={onProfessionalTranslation}>
            متابعة العمل
            <ArrowLeft size={17} />
          </button>
        </div>
      </section>

      <section className="platform-dashboard-metrics" aria-label="مؤشرات المنصة">
        <article>
          <span className="is-projects"><FolderMetricIcon /></span>
          <div>
            <small>المشاريع المحفوظة</small>
            <strong>{projectCount}</strong>
            <p>المشاريع المتاحة في مكتبتك الحالية</p>
          </div>
        </article>
        <article>
          <span className="is-approved"><BadgeCheck size={22} /></span>
          <div>
            <small>الأسئلة المعتمدة</small>
            <strong>{approvedCount}</strong>
            <p>جاهزة للبنك أو التصدير</p>
          </div>
        </article>
        <article>
          <span className="is-review"><Gauge size={22} /></span>
          <div>
            <small>تحتاج مراجعة</small>
            <strong>{needsReviewCount + glossaryNeedsReview}</strong>
            <p>أسئلة ومصطلحات تنتظر قرارًا</p>
          </div>
        </article>
        <article>
          <span className="is-provider"><CheckCircle2 size={22} /></span>
          <div>
            <small>مزود الترجمة</small>
            <strong className="is-text">{providerLabel(translationProviderStatus)}</strong>
            <p>{connectionLabel(apiStatus)}</p>
          </div>
        </article>
      </section>

      <section className="platform-dashboard-section">
        <div className="platform-dashboard-section-heading">
          <div>
            <span>وحدات المنصة</span>
            <h2>انتقل مباشرة إلى الأداة التي تحتاجها</h2>
          </div>
          <p>
            كل وحدة تعمل على نفس بيانات المشروع، بدل نسخ الملفات بين أدوات
            منفصلة ثم محاولة تذكر أين اختفت النسخة الصحيحة.
          </p>
        </div>

        <div className="platform-module-grid">
          {moduleCards.map((module) => {
            const Icon = module.icon;
            return (
              <button
                type="button"
                className={`platform-module-card is-${module.tone}`}
                key={module.title}
                onClick={module.onOpen}
              >
                <span className="platform-module-icon">
                  <Icon size={23} />
                </span>
                <span className="platform-module-eyebrow">{module.eyebrow}</span>
                <h3>{module.title}</h3>
                <p>{module.description}</p>
                <strong>
                  {module.actionLabel}
                  <ArrowLeft size={16} />
                </strong>
              </button>
            );
          })}
        </div>
      </section>

      <section className="platform-workflow-overview">
        <div className="platform-workflow-overview-copy">
          <span>رحلة العمل المتكاملة</span>
          <h2>مسار واضح من الملف الأصلي إلى منتج تعليمي جاهز</h2>
          <p>
            لا تزال رحلة معالجة الورقة موجودة، لكنها أصبحت جزءًا من المنصة
            وليست المنصة كلها. تقدم صغير للبشرية، لكنه مهم.
          </p>
        </div>
        <ol>
          <li>
            <span>1</span>
            <div>
              <strong>اجمع المصدر</strong>
              <small>رفع مباشر أو مصدر سحابي مع سجل نسخ.</small>
            </div>
          </li>
          <li>
            <span>2</span>
            <div>
              <strong>حلّل وراجع</strong>
              <small>أسئلة وأجزاء ورسوم ودرجات ومصطلحات.</small>
            </div>
          </li>
          <li>
            <span>3</span>
            <div>
              <strong>اربط وأنتج</strong>
              <small>منهج، بنك أسئلة، اختبار، نشاط أو رسم.</small>
            </div>
          </li>
          <li>
            <span>4</span>
            <div>
              <strong>اعتمد وصدّر</strong>
              <small>DOCX وPDF مع فحوص الجاهزية والقبول.</small>
            </div>
          </li>
        </ol>
      </section>
    </div>
  );
}

function FolderMetricIcon() {
  return <FileStack size={22} />;
}
