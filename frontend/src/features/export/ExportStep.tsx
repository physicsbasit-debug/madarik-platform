import { Download, FileText, Loader2 } from 'lucide-react';
import { useState } from 'react';
import type { GlossaryTerm, ProjectMetadata, QuestionItem } from '../../types/project';
import { MetricCard } from '../../components/MetricCard';

interface ExportStepProps {
  metadata: ProjectMetadata;
  questions: QuestionItem[];
  glossary: GlossaryTerm[];
  canExportDocx: boolean;
  canExportPdf: boolean;
  onExportDocx: () => Promise<void>;
  onExportPdf: () => Promise<void>;
}

export function ExportStep({
  metadata,
  questions,
  glossary,
  canExportDocx,
  canExportPdf,
  onExportDocx,
  onExportPdf,
}: ExportStepProps) {
  const [isExportingDocx, setIsExportingDocx] = useState(false);
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [exportMessage, setExportMessage] = useState('تصدير DOCX وPDF فعلي متاح الآن، مع دعم شعار المدرسة ومرفقات الأسئلة اليدوية في Phase 1-H1. راجع الملفين قبل الاستخدام، فالآلة مفيدة لكنها ليست لجنة مراجعة.');

  const approvedQuestions = questions
    .filter((question) => question.status !== 'deleted')
    .sort((a, b) => a.orderIndex - b.orderIndex);
  const totalMarks = approvedQuestions.reduce((sum, question) => sum + (question.marks ?? 0), 0);
  const glossaryNeedsReview = glossary.filter((term) => term.status === 'needs_review').length;

  async function handleExportDocx() {
    setIsExportingDocx(true);
    setExportMessage('جاري إنشاء ملف Word...');
    try {
      await onExportDocx();
      setExportMessage('تم إنشاء ملف Word وتحميله. راجع الملف قبل استخدامه مع الطلبة، فالآلة مفيدة لكنها ليست معلمًا أول.');
    } catch (error) {
      console.error(error);
      setExportMessage('تعذر إنشاء ملف Word. تأكد من وجود أسئلة نشطة واتصال Backend.');
    } finally {
      setIsExportingDocx(false);
    }
  }

  async function handleExportPdf() {
    setIsExportingPdf(true);
    setExportMessage('جاري إنشاء ملف PDF...');
    try {
      await onExportPdf();
      setExportMessage('تم إنشاء ملف PDF وتحميله. راجع المحاذاة العربية قبل الطباعة، فالـPDF معروف بعناده الجميل.');
    } catch (error) {
      console.error(error);
      setExportMessage('تعذر إنشاء ملف PDF. تأكد من وجود أسئلة نشطة واتصال Backend.');
    } finally {
      setIsExportingPdf(false);
    }
  }

  return (
    <div className="step-grid">
      <section className="form-card wide-card">
        <div className="section-heading">
          <p className="eyebrow">تصدير فعلي</p>
          <h3>جاهزية الورقة النهائية</h3>
          <p>تستطيع الآن إنشاء ملف Word وملف PDF بتنسيق RTL أولي، مع إدراج شعار المدرسة ومرفقات الصور/الجداول المرتبطة بالأسئلة يدويًا.</p>
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
          <div><dt>الصيغ</dt><dd>DOCX + PDF</dd></div>
        </dl>
      </section>

      <section className="form-card">
        <div className="section-heading">
          <p className="eyebrow">ملفات التصدير</p>
          <h3>إنشاء Word وPDF بتنسيق RTL</h3>
        </div>
        <div className="export-buttons-stack">
          <button
            type="button"
            className="primary-button full-width"
            onClick={() => void handleExportDocx()}
            disabled={!canExportDocx || isExportingDocx || isExportingPdf || approvedQuestions.length === 0}
          >
            {isExportingDocx ? <Loader2 size={18} className="spin-icon" /> : <Download size={18} />}
            {isExportingDocx ? 'جاري إنشاء Word...' : 'تحميل ملف Word'}
          </button>
          <button
            type="button"
            className="secondary-button full-width"
            onClick={() => void handleExportPdf()}
            disabled={!canExportPdf || isExportingDocx || isExportingPdf || approvedQuestions.length === 0}
          >
            {isExportingPdf ? <Loader2 size={18} className="spin-icon" /> : <Download size={18} />}
            {isExportingPdf ? 'جاري إنشاء PDF...' : 'تحميل ملف PDF'}
          </button>
        </div>
        <div className="notice-card">
          <FileText size={22} />
          <span>{exportMessage}</span>
        </div>
      </section>
    </div>
  );
}
