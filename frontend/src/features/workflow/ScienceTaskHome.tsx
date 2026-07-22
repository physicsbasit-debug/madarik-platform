import {
  Archive,
  BookOpenCheck,
  BrainCircuit,
  Cloud,
  FlaskConical,
  Layers3,
  LibraryBig,
  Sparkles,
  WandSparkles,
} from "lucide-react";

type ScienceTaskHomeProps = {
  onQuickTranslation: () => void;
  onProfessionalTranslation: () => void;
  onOpenCurriculum: () => void;
  onOpenQuestionBank: () => void;
};

const comingSoonTasks = [
  {
    icon: LibraryBig,
    title: "مكتبة المناهج والمصادر",
    description:
      "مناهج العلوم من الصف الأول إلى الثاني عشر، والوثائق والاختبارات الأصلية المرتبطة بها.",
  },
  {
    icon: Archive,
    title: "بنك الأسئلة",
    description:
      "حفظ الأسئلة المعتمدة وتصنيفها وربطها بالصف والوحدة وناتج التعلم.",
  },
  {
    icon: Layers3,
    title: "إنشاء اختبار",
    description:
      "تكوين اختبار قصير أو ورقة تقويم وفق جدول مواصفات جاهز.",
  },
  {
    icon: BrainCircuit,
    title: "أنشطة متمايزة",
    description:
      "إنشاء أنشطة دعم وأساسية ومتقدمة وإثرائية من نفس المحتوى العلمي.",
  },
];

export default function ScienceTaskHome({
  onQuickTranslation,
  onProfessionalTranslation,
  onOpenCurriculum,
  onOpenQuestionBank,
}: ScienceTaskHomeProps) {
  return (
    <main className="science-task-home" dir="rtl">
      <section className="science-task-hero">
        <div className="science-task-hero-copy">
          <span className="science-task-kicker">
            <FlaskConical size={18} />
            منصة مدارك للعلوم
          </span>
          <h1>ماذا تريد أن تنجز اليوم؟</h1>
          <p>
            اختر المهمة المناسبة. الترجمة السريعة للإنجاز المباشر،
            والمسار الاحترافي للمراجعة الدقيقة والاعتماد والتصدير.
          </p>
        </div>

        <div className="science-task-hero-visual" aria-hidden="true">
          <Sparkles size={34} />
          <strong>علوم 1–12</strong>
          <span>مصادر، ترجمة، أسئلة، اختبارات وأنشطة</span>
        </div>
      </section>

      <section className="science-task-section">
        <div className="science-task-section-heading">
          <div>
            <span>ابدأ الآن</span>
            <h2>المهام المتاحة</h2>
          </div>
          <small>المساران يستخدمان نواة مدارك الحالية الموثوقة.</small>
        </div>

        <div className="science-task-primary-grid">
          <button
            type="button"
            className="science-task-card science-task-card-primary"
            onClick={onQuickTranslation}
          >
            <div className="science-task-card-icon">
              <WandSparkles size={28} />
            </div>
            <div className="science-task-card-copy">
              <span className="science-task-status is-ready">متاح الآن</span>
              <h3>ترجمة سريعة</h3>
              <p>
                ارفع الورقة وابدأ المعالجة من رحلة مبسطة، مع إمكانية
                فتح المراجعة التفصيلية عند الحاجة.
              </p>
              <strong>بدء الترجمة السريعة</strong>
            </div>
          </button>

          <button
            type="button"
            className="science-task-card science-task-card-secondary"
            onClick={onProfessionalTranslation}
          >
            <div className="science-task-card-icon">
              <BookOpenCheck size={28} />
            </div>
            <div className="science-task-card-copy">
              <span className="science-task-status is-ready">متاح الآن</span>
              <h3>ترجمة احترافية</h3>
              <p>
                راجع كل سؤال، صحح الترجمة، اربط الرسوم، راجع الدرجات،
                ثم اعتمد النسخة النهائية.
              </p>
              <strong>فتح المسار الاحترافي</strong>
            </div>
          </button>
        </div>
      </section>

      <section className="science-task-section">
        <div className="science-task-section-heading">
          <div>
            <span>خارطة الطريق</span>
            <h2>أدوات مدارك القادمة</h2>
          </div>
          <small>بطاقات تعريفية فقط، ولا تنفذ وظائف غير مبنية.</small>
        </div>

        <div className="science-task-coming-grid">
          {comingSoonTasks.map((task) => {
            const Icon = task.icon;
            const isCurriculum = task.title === "مكتبة المناهج والمصادر";
            const isQuestionBank = task.title === "بنك الأسئلة";

            if (isCurriculum || isQuestionBank) {
              return (
                <button
                  type="button"
                  className="science-task-coming-card is-available"
                  key={task.title}
                  onClick={
                    isQuestionBank
                      ? onOpenQuestionBank
                      : onOpenCurriculum
                  }
                >
                  <div className="science-task-coming-icon">
                    <Icon size={24} />
                  </div>
                  <span className="science-task-status is-ready">متاح الآن</span>
                  <h3>{task.title}</h3>
                  <p>{task.description}</p>
                  <strong>
                    {isQuestionBank
                      ? "فتح بنك الأسئلة"
                      : "فتح مكتبة المناهج"}
                  </strong>
                </button>
              );
            }

            return (
              <article className="science-task-coming-card" key={task.title}>
                <div className="science-task-coming-icon">
                  <Icon size={24} />
                </div>
                <span className="science-task-status">قريبًا</span>
                <h3>{task.title}</h3>
                <p>{task.description}</p>
              </article>
            );
          })}
        </div>
      </section>

      <section className="science-task-source-note">
        <div>
          <Cloud size={22} />
          <strong>المصادر السحابية</strong>
        </div>
        <p>
          سيتم ربط Google Drive أولًا بمكتبة المناهج والاختبارات الأصلية،
          ثم OneDrive في مرحلة لاحقة.
        </p>
      </section>
    </main>
  );
}
