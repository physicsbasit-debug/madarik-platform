import type {
  DifferentiatedActivityPreview,
} from "../../types/project";

interface Props {
  preview: DifferentiatedActivityPreview;
  onClose: () => void;
}

export function DifferentiatedActivityPreviewCard({
  preview,
  onClose,
}: Props) {
  return (
    <section className="differentiated-preview" dir="rtl">
      <header>
        <div>
          <span>{preview.levelLabel}</span>
          <h2>{preview.title}</h2>
        </div>
        <button
          type="button"
          className="secondary-button compact"
          onClick={onClose}
        >
          إغلاق
        </button>
      </header>

      <div className="differentiated-preview-meta">
        <span>الصف {preview.grade}</span>
        <span>{preview.estimatedMinutes} دقيقة</span>
        <span>{preview.scienceDomain}</span>
      </div>

      <section>
        <h3>الهدف</h3>
        <p>{preview.objective}</p>
      </section>

      <section>
        <h3>التعليمات</h3>
        <p>{preview.instructions}</p>
      </section>

      <section>
        <h3>معايير النجاح</h3>
        <ul>
          {preview.successCriteria.map((criterion) => (
            <li key={criterion}>{criterion}</li>
          ))}
        </ul>
      </section>

      <section>
        <h3>الأدوات والمواد</h3>
        {preview.materials.length ? (
          <ul>
            {preview.materials.map((material) => (
              <li key={material}>{material}</li>
            ))}
          </ul>
        ) : (
          <p>لا توجد أدوات محددة.</p>
        )}
      </section>

      <section className="differentiated-workspace-lines">
        <h3>مساحة عمل الطالب</h3>
        {Array.from({ length: 8 }).map((_, index) => (
          <span key={index} />
        ))}
      </section>
    </section>
  );
}
