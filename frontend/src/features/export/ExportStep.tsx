import { Download, FileText, Loader2 } from 'lucide-react';
import { useState } from 'react';
import type { GlossaryTerm, ProjectMetadata, QuestionItem } from '../../types/project';
import { MetricCard } from '../../components/MetricCard';

interface ExportStepProps {
  metadata: ProjectMetadata;
  questions: QuestionItem[];
  glossary: GlossaryTerm[];
  canExportDocx: boolean;
  onExportDocx: () => Promise<void>;
}

export function ExportStep({ metadata, questions, glossary, canExportDocx, onExportDocx }: ExportStepProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [exportMessage, setExportMessage] = useState('تصدير DOCX فعلي متاح الآن في Phase 1-F1. PDF ما زال مؤجلًا، حتى لا نوقظ وحش RTL قبل موعده.');

  const approvedQuestions = questions
    .filter((question) => question.status !== 'deleted')
    .sort((a, b) => a.orderIndex - b.orderIndex);
  const totalMarks = approvedQuestions.reduce((sum, question) => sum + (question.marks ?? 0), 0);
  const glossaryNeedsReview = glossary.filter((term) => term.status === 'needs_review').length;

  async function handleExportDocx() {
    setIsExporting(true);
    setExportMessage('جاري إنشاء ملف Word...');
    try {
      await onExportDocx();
      setExportMessage('تم إنشاء ملف Word وتحميله. راجع الملف قبل استخدامه مع الطلبة، فالآلة مفيدة لكنها ليست معلمًا أول.');
    } catch (error) {
      console.error(error);
      setExportMessage('تعذر إنشاء ملف Word. تأكد من وجود أسئلة نشطة واتصال Backend.');
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <div className="step-grid">
      <section className="form-card wide-card">
        <div className="section-heading">
          <p className="eyebrow">تصدير فعلي</p>
          <h3>جاهزية الورقة النهائية</h3>
          <p>تستطيع الآن إنشاء ملف Word حقيقي بتنسيق RTL. تصدير PDF سيأتي في مرحلة مستقلة حتى لا نخلط المعارك.</p>
        </div>

        <div className="metrics-row">
          <MetricCard label="الأسئلة المصدّرة" value={approvedQuestions.length} hint="بعد الحذف" />
          <MetricCard label="مجموع الدرجات" value={totalMarks} hint="محسوب تلقائيًا" />
          <MetricCard label="مصطلحات تحتاج مراجعة" value={glossaryNeedsReview} hint="للمعلم فقط" />
        </div>
      </section>

      <section className="form-card">
        <div className="section-heading">
          <p className="eyebrow">بيانات الورقة</p>
          <h3>{metadata.paperTitle}</h3>
        </div>
        <dl className="metadata-list">
          <div><dt>المدرسة</dt><dd>{metadata.schoolName}</dd></div>
          <div><dt>المادة</dt><dd>{metadata.subject}</dd></div>
          <div><dt>الصف</dt><dd>{metadata.grade}</dd></div>
          <div><dt>الزمن</dt><dd>{metadata.duration}</dd></div>
          <div><dt>نوع النسخة</dt><dd>{metadata.outputMode === 'bilingual' ? 'ثنائية اللغة' : 'عربية نظيفة'}</dd></div>
          <div><dt>الصيغ</dt><dd>DOCX فعلي الآن، PDF لاحقًا</dd></div>
        </dl>
      </section>

      <section className="form-card">
        <div className="section-heading">
          <p className="eyebrow">ملف Word</p>
          <h3>إنشاء DOCX بتنسيق RTL</h3>
        </div>
        <button
          type="button"
          className="primary-button full-width"
          onClick={() => void handleExportDocx()}
          disabled={!canExportDocx || isExporting || approvedQuestions.length === 0}
        >
          {isExporting ? <Loader2 size={18} className="spin-icon" /> : <Download size={18} />}
          {isExporting ? 'جاري إنشاء Word...' : 'تحميل ملف Word'}
        </button>
        <div className="notice-card">
          <FileText size={22} />
          <span>{exportMessage}</span>
        </div>
      </section>
    </div>
  );
}
