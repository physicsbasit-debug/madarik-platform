import { ArrowLeft, ArrowRight, FileText, RefreshCcw } from 'lucide-react';
import { useMemo, useState } from 'react';
import type { StepKey } from '../types/project';

const steps: Array<{ key: StepKey; label: string; description: string }> = [
  { key: 'setup', label: 'بيانات الورقة', description: 'إعداد رأس الورقة ونوع النسخة' },
  { key: 'upload', label: 'رفع الملف', description: 'استقبال ملف الاختبار' },
  { key: 'extract', label: 'استخراج الأسئلة', description: 'تحويل المحتوى إلى أسئلة مستقلة' },
  { key: 'glossary', label: 'قاموس الورقة', description: 'توحيد المصطلحات للمعلم' },
  { key: 'review', label: 'مراجعة الأسئلة', description: 'تعديل وحذف وترتيب ودرجات' },
  { key: 'export', label: 'التصدير', description: 'إخراج Word وPDF' },
];

export function App() {
  const [activeIndex, setActiveIndex] = useState(0);
  const activeStep = steps[activeIndex];

  const progressLabel = useMemo(() => `${activeIndex + 1} من ${steps.length}`, [activeIndex]);

  function goNext() {
    setActiveIndex((current) => Math.min(current + 1, steps.length - 1));
  }

  function goPrevious() {
    setActiveIndex((current) => Math.max(current - 1, 0));
  }

  function resetProject() {
    const confirmed = window.confirm('سيتم مسح مشروع العمل الحالي فقط. هل تريد المتابعة؟');
    if (confirmed) setActiveIndex(0);
  }

  return (
    <main className="app-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">Phase 0 Skeleton</p>
          <h1>منصة مدارك</h1>
          <p className="hero-text">
            هيكل تأسيسي لمنصة تعليمية ذكية لمعالجة أوراق الاختبارات الأجنبية وتحويلها إلى موارد عربية وثنائية اللغة قابلة للمراجعة والطباعة.
          </p>
        </div>
        <button className="ghost-button" type="button" onClick={resetProject}>
          <RefreshCcw size={18} />
          مشروع جديد / إعادة البدء
        </button>
      </section>

      <section className="workspace-card">
        <aside className="steps-panel" aria-label="خطوات العمل">
          {steps.map((step, index) => (
            <button
              key={step.key}
              type="button"
              className={`step-item ${index === activeIndex ? 'active' : ''} ${index < activeIndex ? 'done' : ''}`}
              onClick={() => setActiveIndex(index)}
            >
              <span className="step-number">{index + 1}</span>
              <span>
                <strong>{step.label}</strong>
                <small>{step.description}</small>
              </span>
            </button>
          ))}
        </aside>

        <section className="step-content">
          <div className="step-header">
            <div>
              <p className="eyebrow">الخطوة {progressLabel}</p>
              <h2>{activeStep.label}</h2>
              <p>{activeStep.description}</p>
            </div>
            <FileText size={34} aria-hidden="true" />
          </div>

          <StepPlaceholder stepKey={activeStep.key} />

          <div className="actions-row">
            <button className="secondary-button" type="button" onClick={goPrevious} disabled={activeIndex === 0}>
              <ArrowRight size={18} />
              السابق
            </button>
            <button className="primary-button" type="button" onClick={goNext} disabled={activeIndex === steps.length - 1}>
              التالي
              <ArrowLeft size={18} />
            </button>
          </div>
        </section>
      </section>
    </main>
  );
}

function StepPlaceholder({ stepKey }: { stepKey: StepKey }) {
  const content: Record<StepKey, { title: string; points: string[] }> = {
    setup: {
      title: 'سيتم هنا إدخال بيانات الورقة',
      points: ['اسم المدرسة', 'المادة والصف', 'عنوان الورقة', 'الزمن والدرجة', 'نوع النسخة'],
    },
    upload: {
      title: 'سيتم هنا رفع الملف',
      points: ['PDF نصي', 'PDF مصور لاحقًا', 'صور JPG / PNG / WEBP', 'فحص نوع الملف وحجمه'],
    },
    extract: {
      title: 'سيتم هنا استخراج الأسئلة',
      points: ['استخراج النص', 'تقسيم الأسئلة', 'التقاط الدرجات', 'ربط الصور قدر الإمكان'],
    },
    glossary: {
      title: 'سيتم هنا عرض قاموس الورقة',
      points: ['مصطلح إنجليزي', 'ترجمة عربية معتمدة', 'حالة المصطلح', 'تعديل الترجمة'],
    },
    review: {
      title: 'سيتم هنا مراجعة بطاقات الأسئلة',
      points: ['النص الأصلي', 'الترجمة', 'الدرجة', 'حذف وترتيب', 'حالة السؤال'],
    },
    export: {
      title: 'سيتم هنا التصدير',
      points: ['نسخة عربية', 'نسخة ثنائية اللغة', 'DOCX', 'PDF', 'RTL كامل'],
    },
  };

  const selected = content[stepKey];

  return (
    <div className="placeholder-card">
      <h3>{selected.title}</h3>
      <ul>
        {selected.points.map((point) => (
          <li key={point}>{point}</li>
        ))}
      </ul>
    </div>
  );
}
