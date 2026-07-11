import { AlertTriangle, CheckCircle2, Download, FileText, KeyRound, Loader2, ShieldCheck, Trash2 } from 'lucide-react';
import { useState } from 'react';
import type { AnswerKeyItem, GlossaryTerm, ProjectMetadata, ProjectReadinessReport, QuestionItem } from '../../types/project';
import { MetricCard } from '../../components/MetricCard';

interface ExportStepProps {
  metadata: ProjectMetadata;
  questions: QuestionItem[];
  glossary: GlossaryTerm[];
  answerKey: AnswerKeyItem[];
  readiness: ProjectReadinessReport | null;
  canExportDocx: boolean;
  canExportPdf: boolean;
  onExportDocx: () => Promise<void>;
  onExportPdf: () => Promise<void>;
  onRefreshReadiness: () => Promise<void>;
  onGenerateAnswerKey: () => Promise<void>;
  onClearAnswerKey: () => Promise<void>;
}

export function ExportStep({
  metadata,
  questions,
  glossary,
  answerKey,
  readiness,
  canExportDocx,
  canExportPdf,
  onExportDocx,
  onExportPdf,
  onRefreshReadiness,
  onGenerateAnswerKey,
  onClearAnswerKey,
}: ExportStepProps) {
  const [isExportingDocx, setIsExportingDocx] = useState(false);
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [isCheckingReadiness, setIsCheckingReadiness] = useState(false);
  const [isGeneratingAnswerKey, setIsGeneratingAnswerKey] = useState(false);
  const [exportMessage, setExportMessage] = useState('تصدير DOCX وPDF متاح مع فحص جاهزية قبل التصدير، ودعم الشعار والمرفقات ونسخ العمل JSON ومسودة نموذج إجابة للمعلم.');

  const approvedQuestions = questions
    .filter((question) => question.status !== 'deleted')
    .sort((a, b) => a.orderIndex - b.orderIndex);
  const totalMarks = readiness?.totalMarks ?? approvedQuestions.reduce((sum, question) => sum + (question.marks ?? 0), 0);
  const glossaryNeedsReview = glossary.filter((term) => term.status === 'needs_review').length;
  const readinessBlocksExport = readiness ? !readiness.ready : approvedQuestions.length === 0;

  async function handleRefreshReadiness() {
    setIsCheckingReadiness(true);
    setExportMessage('جاري فحص جاهزية الورقة...');
    try {
      await onRefreshReadiness();
      setExportMessage('تم تحديث فحص الجاهزية.');
    } catch (error) {
      console.error(error);
      setExportMessage('تعذر تحديث فحص الجاهزية. تأكد من اتصال Backend.');
    } finally {
      setIsCheckingReadiness(false);
    }
  }


  async function handleGenerateAnswerKey() {
    setIsGeneratingAnswerKey(true);
    setExportMessage('جاري توليد مسودة نموذج الإجابة...');
    try {
      await onGenerateAnswerKey();
      setExportMessage('تم توليد مسودة نموذج الإجابة. راجعها قبل اعتمادها، لأن الثقة العمياء بالآلة نشاط خطير.');
    } catch (error) {
      console.error(error);
      setExportMessage('تعذر توليد مسودة نموذج الإجابة.');
    } finally {
      setIsGeneratingAnswerKey(false);
    }
  }

  async function handleClearAnswerKey() {
    setIsGeneratingAnswerKey(true);
    setExportMessage('جاري حذف مسودة نموذج الإجابة...');
    try {
      await onClearAnswerKey();
      setExportMessage('تم حذف مسودة نموذج الإجابة.');
    } catch (error) {
      console.error(error);
      setExportMessage('تعذر حذف مسودة نموذج الإجابة.');
    } finally {
      setIsGeneratingAnswerKey(false);
    }
  }

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
          <p className="eyebrow">فحص الجاهزية قبل التصدير</p>
          <h3>جاهزية الورقة النهائية</h3>
          <p>
            قبل إنشاء Word أو PDF، تفحص منصة مدارك وجود أسئلة قابلة للتصدير وترجمة ودرجات وحالات مراجعة.
          </p>
        </div>

        <div className="metrics-row">
          <MetricCard label="الأسئلة المصدّرة" value={readiness?.exportableQuestionCount ?? approvedQuestions.length} hint="بعد الحذف" />
          <MetricCard label="مجموع الدرجات" value={totalMarks} hint="محسوب تلقائيًا" />
          <MetricCard label="أسئلة مترجمة" value={readiness?.translatedQuestionCount ?? 0} hint="حسب فحص Backend" />
          <MetricCard label="مصطلحات تحتاج مراجعة" value={glossaryNeedsReview} hint="للمعلم فقط" />
          <MetricCard label="مسودة الإجابة" value={answerKey.length} hint="للمعلم فقط" />
        </div>

        <div className={`readiness-card ${readiness?.ready ? 'success-card' : 'warning-card'}`}>
          {readiness?.ready ? <CheckCircle2 size={24} /> : <AlertTriangle size={24} />}
          <div>
            <strong>{readiness?.ready ? 'الورقة جاهزة للتصدير' : 'توجد ملاحظات قبل التصدير'}</strong>
            <p>
              {readiness
                ? `الأسئلة القابلة للتصدير: ${readiness.exportableQuestionCount}، المحذوفة: ${readiness.deletedQuestionCount}.`
                : 'لم يتم تشغيل فحص الجاهزية بعد.'}
            </p>
          </div>
        </div>

        {readiness?.issues.length ? (
          <ul className="readiness-list">
            {readiness.issues.map((issue) => (
              <li key={`${issue.code}-${issue.message}`} className={issue.severity === 'error' ? 'readiness-error' : 'readiness-warning'}>
                <span>{issue.severity === 'error' ? 'مانع' : 'تنبيه'}</span>
                {issue.message}
              </li>
            ))}
          </ul>
        ) : (
          <div className="notice-card">
            <ShieldCheck size={22} />
            <span>لا توجد ملاحظات مانعة من التصدير في آخر فحص جاهزية.</span>
          </div>
        )}

        <button type="button" className="secondary-button" onClick={() => void handleRefreshReadiness()} disabled={isCheckingReadiness}>
          {isCheckingReadiness ? <Loader2 size={18} className="spin-icon" /> : <ShieldCheck size={18} />}
          تحديث فحص الجاهزية
        </button>
      </section>


      <section className="form-card wide-card">
        <div className="section-heading">
          <p className="eyebrow">Phase 2-E1</p>
          <h3>مسودة نموذج الإجابة</h3>
          <p>
            تولّد المنصة مسودة أولية للإجابات من الأسئلة النشطة. هذه أداة مساعدة للمعلم فقط، وليست نموذجًا معتمدًا ولا تظهر في ورقة الطالب.
          </p>
        </div>

        <div className="inline-actions">
          <button type="button" className="primary-button" onClick={() => void handleGenerateAnswerKey()} disabled={isGeneratingAnswerKey || approvedQuestions.length === 0}>
            {isGeneratingAnswerKey ? <Loader2 size={18} className="spin-icon" /> : <KeyRound size={18} />}
            توليد مسودة نموذج الإجابة
          </button>
          <button type="button" className="danger-button" onClick={() => void handleClearAnswerKey()} disabled={isGeneratingAnswerKey || answerKey.length === 0}>
            <Trash2 size={18} />
            حذف المسودة
          </button>
        </div>

        {answerKey.length > 0 ? (
          <div className="answer-key-list">
            {answerKey.map((item) => (
              <article key={item.id} className="answer-key-card">
                <div className="answer-key-card-header">
                  <strong>السؤال {item.questionNumber}</strong>
                  <span>{item.marks ?? '—'} درجات · الثقة: {item.confidence}</span>
                </div>
                <p>{item.draftAnswer}</p>
                <small>{item.notes}</small>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty-state">لم تُولّد مسودة نموذج إجابة بعد.</div>
        )}
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
            disabled={!canExportDocx || readinessBlocksExport || isExportingDocx || isExportingPdf}
          >
            {isExportingDocx ? <Loader2 size={18} className="spin-icon" /> : <Download size={18} />}
            {isExportingDocx ? 'جاري إنشاء Word...' : 'تحميل ملف Word'}
          </button>
          <button
            type="button"
            className="secondary-button full-width"
            onClick={() => void handleExportPdf()}
            disabled={!canExportPdf || readinessBlocksExport || isExportingDocx || isExportingPdf}
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
