import {
  AlertTriangle,
  BarChart3,
  BookOpenCheck,
  CheckCircle2,
  Download,
  Eye,
  FileCheck2,
  FileText,
  GitBranch,
  Image as ImageIcon,
  KeyRound,
  Loader2,
  Radar,
  Settings2,
  ShieldCheck,
  Trash2,
} from 'lucide-react';
import { useState } from 'react';
import type {
  AnswerKeyItem,
  EducationalAnalysisReport,
  EducationalQualityToolsReport,
  FullExamEndToEndReport,
  FullExamExportReport,
  FullExamTranslationReport,
  GlossaryTerm,
  ProjectMetadata,
  ProjectReadinessReport,
  QuestionItem,
  SchoolLogoInfo,
} from '../../types/project';
import { MetricCard } from '../../components/MetricCard';

interface ExportStepProps {
  metadata: ProjectMetadata;
  schoolLogo: SchoolLogoInfo | null;
  questions: QuestionItem[];
  glossary: GlossaryTerm[];
  answerKey: AnswerKeyItem[];
  educationalAnalysis: EducationalAnalysisReport | null;
  qualityTools: EducationalQualityToolsReport | null;
  readiness: ProjectReadinessReport | null;
  fullExamExportReport: FullExamExportReport | null;
  fullExamTranslationReport: FullExamTranslationReport | null;
  fullExamEndToEndReport: FullExamEndToEndReport | null;
  onRunFullExamAcceptance: () => Promise<void>;
  onMetadataChange: (metadata: ProjectMetadata) => void;
  canExportDocx: boolean;
  canExportPdf: boolean;
  onExportDocx: () => Promise<void>;
  onExportPdf: () => Promise<void>;
  onRefreshReadiness: () => Promise<void>;
  onGenerateAnswerKey: () => Promise<void>;
  onClearAnswerKey: () => Promise<void>;
  onGenerateEducationalAnalysis: () => Promise<void>;
  onClearEducationalAnalysis: () => Promise<void>;
  onGenerateQualityTools: () => Promise<void>;
  onClearQualityTools: () => Promise<void>;
}

function exportAcceptanceLabel(status: FullExamExportReport['status']) {
  switch (status) {
    case 'accepted':
      return 'مقبول';
    case 'needs_review':
      return 'يحتاج مراجعة';
    case 'incomplete':
      return 'غير مكتمل';
    case 'failed':
      return 'فشل';
  }
}

function formatLabel(format: 'docx' | 'pdf') {
  return format.toUpperCase();
}


function endToEndAcceptanceLabel(
  status: FullExamEndToEndReport['status'],
) {
  switch (status) {
    case 'accepted':
      return 'مقبول';
    case 'needs_review':
      return 'يحتاج مراجعة';
    case 'rejected':
      return 'مرفوض';
  }
}

function endToEndStageLabel(
  stage: FullExamEndToEndReport['stages'][number]['stage'],
) {
  const labels = {
    intake: 'إدخال الورقة',
    layout_assets: 'لقطات الصفحات',
    glossary: 'القاموس',
    translation: 'الترجمة',
    readiness: 'الجاهزية',
    docx_export: 'تصدير Word',
    pdf_export: 'تصدير PDF',
    final_consistency: 'الاتساق النهائي',
  };
  return labels[stage];
}

function endToEndStageStatusLabel(
  status: FullExamEndToEndReport['stages'][number]['status'],
) {
  const labels = {
    accepted: 'مقبول',
    needs_review: 'يحتاج مراجعة',
    pending: 'غير مكتمل',
    failed: 'فشل',
    skipped: 'متجاوز',
  };
  return labels[status];
}


export function ExportStep({
  metadata,
  schoolLogo,
  questions,
  glossary,
  answerKey,
  educationalAnalysis,
  qualityTools,
  readiness,
  fullExamExportReport,
  fullExamTranslationReport,
  fullExamEndToEndReport,
  onRunFullExamAcceptance,
  onMetadataChange,
  canExportDocx,
  canExportPdf,
  onExportDocx,
  onExportPdf,
  onRefreshReadiness,
  onGenerateAnswerKey,
  onClearAnswerKey,
  onGenerateEducationalAnalysis,
  onClearEducationalAnalysis,
  onGenerateQualityTools,
  onClearQualityTools,
}: ExportStepProps) {
  const [isExportingDocx, setIsExportingDocx] = useState(false);
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [isCheckingReadiness, setIsCheckingReadiness] = useState(false);
  const [isRunningEndToEnd, setIsRunningEndToEnd] = useState(false);
  const [isGeneratingAnswerKey, setIsGeneratingAnswerKey] = useState(false);
  const [isGeneratingAnalysis, setIsGeneratingAnalysis] = useState(false);
  const [isGeneratingQualityTools, setIsGeneratingQualityTools] = useState(false);
  const [exportMessage, setExportMessage] = useState('تصدير DOCX وPDF متاح مع فحص جاهزية قبل التصدير، ودعم الشعار والمرفقات ونسخ العمل JSON ومسودة نموذج إجابة وتحليل تربوي وأدوات جودة تأسيسية للمعلم.');

  const approvedQuestions = questions
    .filter((question) => question.status !== 'deleted')
    .sort((a, b) => a.orderIndex - b.orderIndex);
  const totalMarks = readiness?.totalMarks ?? approvedQuestions.reduce((sum, question) => sum + (question.marks ?? 0), 0);
  const glossaryNeedsReview = glossary.filter((term) => term.status === 'needs_review').length;
  const declaredMarks = Number.parseInt(metadata.totalMarks.trim(), 10);
  const hasDeclaredMarks = Number.isFinite(declaredMarks);
  const hasMarksMismatch = hasDeclaredMarks && declaredMarks !== totalMarks;
  const marksPolicy = metadata.marksPolicy ?? 'unresolved';
  const translationAccepted = fullExamTranslationReport?.status === 'accepted';
  const studentVersionLabel = metadata.outputMode === 'bilingual'
    ? 'ثنائية اللغة'
    : translationAccepted
      ? 'عربية معتمدة'
      : 'مسودة ترجمة تحتاج مراجعة';
  const readinessBlocksExport = readiness ? !readiness.ready : approvedQuestions.length === 0;
  const readinessHasWarnings = readiness?.issues.some((issue) => issue.severity === 'warning') ?? false;
  const approvedCount = approvedQuestions.filter(
    (question) => question.status === 'approved',
  ).length;
  const reviewCount = approvedQuestions.filter(
    (question) => question.status === 'needs_review',
  ).length;
  const linkedAssetsCount = approvedQuestions.filter(
    (question) =>
      (question.linkedLayoutAssetIds?.length ?? 0) > 0 ||
      question.attachments.length > 0,
  ).length;
  const selectedFormats = metadata.exportFormats ?? [];
  const logoPreview = schoolLogo
    ? `data:${schoolLogo.type};base64,${schoolLogo.dataBase64}`
    : null;
  const exportIsRunning = isExportingDocx || isExportingPdf;
  const canRunSelectedExport =
    selectedFormats.length > 0 &&
    !readinessBlocksExport &&
    !exportIsRunning &&
    selectedFormats.every((format) =>
      format === 'docx' ? canExportDocx : canExportPdf,
    );

  function toggleExportFormat(format: 'docx' | 'pdf') {
    const nextFormats = selectedFormats.includes(format)
      ? selectedFormats.filter((item) => item !== format)
      : [...selectedFormats, format];

    onMetadataChange({
      ...metadata,
      exportFormats: nextFormats,
    });
  }

  async function handleExportSelected() {
    if (selectedFormats.includes('docx')) {
      await handleExportDocx();
    }
    if (selectedFormats.includes('pdf')) {
      await handleExportPdf();
    }
  }


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




  async function handleRunEndToEndAcceptance() {
    setIsRunningEndToEnd(true);
    setExportMessage(
      'جاري فحص الإدخال واللقطات والقاموس والترجمة والجاهزية وإنشاء Word وPDF في الذاكرة...',
    );
    try {
      await onRunFullExamAcceptance();
      setExportMessage('اكتمل تشغيل بوابة القبول الشامل.');
    } catch (error) {
      console.error(error);
      setExportMessage('تعذر تشغيل بوابة القبول الشامل.');
    } finally {
      setIsRunningEndToEnd(false);
    }
  }


  async function handleGenerateQualityTools() {
    setIsGeneratingQualityTools(true);
    setExportMessage('جاري توليد أدوات الجودة...');
    try {
      await onGenerateQualityTools();
      setExportMessage('تم توليد Pareto وRadar وFishbone. أدوات مفيدة، وليست عصا سحرية، للأسف.');
    } catch (error) {
      console.error(error);
      setExportMessage('تعذر توليد أدوات الجودة.');
    } finally {
      setIsGeneratingQualityTools(false);
    }
  }

  async function handleClearQualityTools() {
    setIsGeneratingQualityTools(true);
    setExportMessage('جاري حذف أدوات الجودة...');
    try {
      await onClearQualityTools();
      setExportMessage('تم حذف أدوات الجودة.');
    } catch (error) {
      console.error(error);
      setExportMessage('تعذر حذف أدوات الجودة.');
    } finally {
      setIsGeneratingQualityTools(false);
    }
  }

  async function handleGenerateEducationalAnalysis() {
    setIsGeneratingAnalysis(true);
    setExportMessage('جاري توليد التحليل التربوي التأسيسي...');
    try {
      await onGenerateEducationalAnalysis();
      setExportMessage('تم توليد التحليل التربوي التأسيسي. راجعه كدليل مراجعة، لا كصك غفران للاختبار.');
    } catch (error) {
      console.error(error);
      setExportMessage('تعذر توليد التحليل التربوي.');
    } finally {
      setIsGeneratingAnalysis(false);
    }
  }

  async function handleClearEducationalAnalysis() {
    setIsGeneratingAnalysis(true);
    setExportMessage('جاري حذف التحليل التربوي...');
    try {
      await onClearEducationalAnalysis();
      setExportMessage('تم حذف التحليل التربوي.');
    } catch (error) {
      console.error(error);
      setExportMessage('تعذر حذف التحليل التربوي.');
    } finally {
      setIsGeneratingAnalysis(false);
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
      <section className="export-workspace export-workspace-redesign">
        <div className="export-control-bar export-control-bar-redesign">
          <div className="export-control-copy">
            <strong>مركز الجاهزية والتصدير</strong>
            <p>راجع الموانع، احسم الدرجة، اختر النسخة والصيغ، ثم نزّل الملفات.</p>
          </div>
          <div className="export-control-actions">
            <button
              type="button"
              className="secondary-button export-readiness-button"
              onClick={() => void handleRefreshReadiness()}
              disabled={isCheckingReadiness}
            >
              {isCheckingReadiness ? (
                <Loader2 size={18} className="spin-icon" />
              ) : (
                <ShieldCheck size={18} />
              )}
              تحديث الجاهزية
            </button>
            <span className="export-advanced-label">الفحوص والتقارير المتقدمة أسفل الصفحة</span>
          </div>
        </div>

        <div className="export-readiness-summary">
          <article className="export-readiness-main">
            <div
              className={`export-readiness-icon ${
                readiness?.ready ? 'is-ready' : 'needs-attention'
              }`}
            >
              {readiness?.ready ? (
                <CheckCircle2 size={30} />
              ) : (
                <AlertTriangle size={30} />
              )}
            </div>
            <div>
              <span>حالة المشروع</span>
              <strong>
                {readiness?.ready
                  ? readinessHasWarnings
                    ? 'جاهز مع تنبيهات'
                    : 'جاهز للتصدير'
                  : 'يحتاج تدخلك قبل التصدير'}
              </strong>
              <p>
                {readiness
                  ? `${readiness.exportableQuestionCount} سؤالًا قابلة للتصدير، و${readiness.deletedQuestionCount} محذوفة.`
                  : 'شغّل فحص الجاهزية لرؤية النتيجة النهائية.'}
              </p>
            </div>
          </article>

          <div className="export-readiness-metrics">
            <article>
              <FileCheck2 size={21} />
              <span>الأسئلة</span>
              <strong>{approvedQuestions.length}</strong>
              <small>{approvedCount} معتمد</small>
            </article>
            <article>
              <BookOpenCheck size={21} />
              <span>المراجعة اليدوية</span>
              <strong>{reviewCount}</strong>
              <small>{reviewCount ? 'تحتاج انتباهًا' : 'مكتملة'}</small>
            </article>
            <article>
              <ImageIcon size={21} />
              <span>الرسوم المرتبطة</span>
              <strong>{linkedAssetsCount}</strong>
              <small>من الأسئلة النشطة</small>
            </article>
            <article>
              <FileText size={21} />
              <span>المصطلحات</span>
              <strong>{glossary.length - glossaryNeedsReview}</strong>
              <small>{glossaryNeedsReview} غير معتمد</small>
            </article>
            <article>
              <ShieldCheck size={21} />
              <span>مجموع الدرجات</span>
              <strong>{totalMarks}</strong>
              <small>{hasMarksMismatch ? 'يوجد اختلاف' : 'متسق'}</small>
            </article>
          </div>
        </div>

        {hasMarksMismatch ? (
          <div
            className={`marks-decision-bar ${
              marksPolicy === 'unresolved'
                ? 'marks-policy-unresolved'
                : 'marks-policy-resolved'
            }`}
          >
            <div>
              <strong>يوجد اختلاف في الدرجة</strong>
              <p>
                الدرجة المعلنة {declaredMarks}، ومجموع الأسئلة {totalMarks}. اختر القرار قبل التصدير.
              </p>
            </div>
            <div className="marks-decision-actions">
              <button
                type="button"
                className={`secondary-button ${
                  marksPolicy === 'use_question_total' ? 'is-selected' : ''
                }`}
                onClick={() =>
                  onMetadataChange({
                    ...metadata,
                    marksPolicy: 'use_question_total',
                  })
                }
              >
                <span>اعتماد مجموع الأسئلة</span>
                <strong>{totalMarks}</strong>
              </button>
              <button
                type="button"
                className={`secondary-button ${
                  marksPolicy === 'scale_to_declared' ? 'is-selected' : ''
                }`}
                onClick={() =>
                  onMetadataChange({
                    ...metadata,
                    marksPolicy: 'scale_to_declared',
                  })
                }
              >
                <span>تحويل الدرجة إلى المعلنة</span>
                <strong>{declaredMarks}</strong>
              </button>
            </div>
          </div>
        ) : null}

        {readiness?.issues.length ? (
          <div className="export-blockers-panel">
            <strong>ملاحظات الجاهزية</strong>
            <ul className="readiness-list">
              {readiness.issues.map((issue) => (
                <li
                  key={`${issue.code}-${issue.message}`}
                  className={
                    issue.severity === 'error'
                      ? 'readiness-error'
                      : 'readiness-warning'
                  }
                >
                  <span>{issue.severity === 'error' ? 'مانع' : 'تنبيه'}</span>
                  {issue.message}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        <div className="export-choice-grid">
          <section className="export-choice-card export-mode-card">
            <div className="export-choice-card-body">
            <div className="export-choice-heading">
              <FileText size={22} />
              <div>
                <span>نوع النسخة</span>
                <strong>اختر المخرج النهائي</strong>
              </div>
            </div>

            <label
              className={`export-radio-card ${
                metadata.outputMode === 'arabic' ? 'is-selected' : ''
              }`}
            >
              <input
                type="radio"
                name="output-mode"
                checked={metadata.outputMode === 'arabic'}
                onChange={() =>
                  onMetadataChange({ ...metadata, outputMode: 'arabic' })
                }
              />
              <div>
                <strong>نسخة عربية نظيفة</strong>
                <span>السؤال بالعربية فقط، جاهز للطباعة والمراجعة الصفية.</span>
              </div>
            </label>

            <label
              className={`export-radio-card ${
                metadata.outputMode === 'bilingual' ? 'is-selected' : ''
              }`}
            >
              <input
                type="radio"
                name="output-mode"
                checked={metadata.outputMode === 'bilingual'}
                onChange={() =>
                  onMetadataChange({ ...metadata, outputMode: 'bilingual' })
                }
              />
              <div>
                <strong>نسخة ثنائية اللغة</strong>
                <span>الإنجليزية ثم العربية تحت كل سؤال.</span>
              </div>
            </label>
            </div>
          </section>

          <section className="export-choice-card export-formats-card">
            <div className="export-choice-card-body">
            <div className="export-choice-heading">
              <Download size={22} />
              <div>
                <span>صيغ الملفات</span>
                <strong>اختر ما تريد تنزيله</strong>
              </div>
            </div>

            <label
              className={`export-format-option ${
                selectedFormats.includes('docx') ? 'is-selected' : ''
              }`}
            >
              <input
                type="checkbox"
                checked={selectedFormats.includes('docx')}
                onChange={() => toggleExportFormat('docx')}
              />
              <div>
                <strong>Word DOCX</strong>
                <span>ملف قابل للتعديل والمراجعة.</span>
              </div>
            </label>

            <label
              className={`export-format-option ${
                selectedFormats.includes('pdf') ? 'is-selected' : ''
              }`}
            >
              <input
                type="checkbox"
                checked={selectedFormats.includes('pdf')}
                onChange={() => toggleExportFormat('pdf')}
              />
              <div>
                <strong>PDF للطباعة</strong>
                <span>نسخة ثابتة جاهزة للطباعة والمشاركة.</span>
              </div>
            </label>
            </div>
          </section>

        </div>

        <div className="export-preview-grid">
          <section className="export-preview-card">
            <div className="export-choice-heading">
              <Eye size={22} />
              <div>
                <span>معاينة قبل التصدير</span>
                <strong>{metadata.paperTitle || 'ورقة بلا عنوان'}</strong>
              </div>
            </div>
            <div className="export-paper-preview">
              <div className="export-paper-thumbnail" aria-hidden="true">
                <div className="export-paper-brand">
                  {logoPreview ? (
                    <img src={logoPreview} alt="" />
                  ) : (
                    <ImageIcon size={20} />
                  )}
                  <span>{metadata.schoolName || 'اسم المدرسة'}</span>
                </div>
                <strong>{metadata.paperTitle || 'عنوان الورقة'}</strong>
                <small>
                  {metadata.subject || 'المادة'} · {metadata.grade || 'الصف'}
                </small>
                <div className="export-paper-line is-wide" />
                <div className="export-paper-line" />
                <div className="export-paper-line is-short" />
                <div className="export-paper-question">1</div>
                <div className="export-paper-line is-wide" />
                <div className="export-paper-line" />
              </div>
              <dl className="export-preview-meta">
                <div><dt>المادة</dt><dd>{metadata.subject || '—'}</dd></div>
                <div><dt>الصف</dt><dd>{metadata.grade || '—'}</dd></div>
                <div><dt>نوع النسخة</dt><dd>{studentVersionLabel}</dd></div>
                <div><dt>الأسئلة</dt><dd>{approvedQuestions.length}</dd></div>
                <div><dt>الدرجات</dt><dd>{totalMarks}</dd></div>
                <div>
                  <dt>الصيغ</dt>
                  <dd>
                    {selectedFormats.length
                      ? selectedFormats.map(formatLabel).join(' + ')
                      : 'لم تُحدد'}
                  </dd>
                </div>
              </dl>
            </div>
          </section>

          <section
            className={`export-ready-card ${
              readiness?.ready ? 'is-ready' : 'needs-attention'
            }`}
          >
            {readiness?.ready ? (
              <CheckCircle2 size={38} />
            ) : (
              <AlertTriangle size={38} />
            )}
            <strong>
              {readiness?.ready
                ? 'المشروع جاهز للتصدير'
                : 'أكمل الملاحظات قبل التصدير'}
            </strong>
            <p>
              {readiness?.ready
                ? 'اختر الصيغ واضغط زر التصدير أدناه.'
                : 'راجع قائمة الجاهزية ثم أعد الفحص.'}
            </p>
          </section>
        </div>

        <section className="export-choice-card export-identity-card export-identity-row">
          <div className="export-choice-heading">
            <ImageIcon size={22} />
            <div>
              <span>هوية المدرسة</span>
              <strong>الشعار ورأس الورقة</strong>
            </div>
          </div>

          <div className="export-identity-row-content">
            <div className="export-logo-preview">
              {logoPreview ? (
                <img src={logoPreview} alt="شعار المدرسة" />
              ) : (
                <ImageIcon size={34} />
              )}
            </div>
            <div className="export-identity-copy">
              <strong>{metadata.schoolName || 'لم يُحدد اسم المدرسة'}</strong>
              <span>
                {schoolLogo
                  ? `الشعار: ${schoolLogo.name}`
                  : 'أضف الشعار من مرحلة البدء والرفع.'}
              </span>
            </div>
          </div>
        </section>

        <div className="export-primary-action">
          <div className="notice-card export-primary-message">
            <FileText size={22} />
            <span>{exportMessage}</span>
          </div>
          <button
            type="button"
            className="primary-button export-main-button"
            onClick={() => void handleExportSelected()}
            disabled={!canRunSelectedExport}
          >
            {exportIsRunning ? (
              <Loader2 size={20} className="spin-icon" />
            ) : (
              <Download size={20} />
            )}
            {exportIsRunning
              ? 'جاري تجهيز الملفات...'
              : selectedFormats.length > 1
                ? 'تصدير Word وPDF'
                : selectedFormats[0] === 'pdf'
                  ? 'تصدير PDF'
                  : 'تصدير Word'}
          </button>
        </div>
      </section>

      <details className="export-advanced-tools">
        <summary>
          <Settings2 size={20} />
          <span>الفحوص والتقارير المتقدمة</span>
          <small>بوابات القبول، التحليل التربوي، أدوات الجودة، ونموذج الإجابة</small>
        </summary>
        <div className="export-advanced-content">
      <section className="form-card wide-card end-to-end-acceptance-panel">
        <div className="section-heading">
          <p className="eyebrow">Phase 4-A6d</p>
          <h3>بوابة قبول الرحلة الكاملة</h3>
          <p>
            تعيد البوابة بناء تقارير الإدخال والترجمة والجاهزية، ثم تنشئ Word وPDF
            في الذاكرة وتفحصهما دون استدعاء مزود ذكاء اصطناعي أو استبدال النصوص
            التي راجعها المعلم.
          </p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={() => void handleRunEndToEndAcceptance()}
          disabled={isRunningEndToEnd}
        >
          {isRunningEndToEnd ? <Loader2 size={18} className="spin-icon" /> : <ShieldCheck size={18} />}
          تشغيل بوابة القبول الشامل
        </button>

        {fullExamEndToEndReport ? (
          <>
            <div className={`end-to-end-status end-to-end-${fullExamEndToEndReport.status}`}>
              {fullExamEndToEndReport.status === 'accepted' ? <CheckCircle2 size={24} /> : <AlertTriangle size={24} />}
              <div>
                <strong>{endToEndAcceptanceLabel(fullExamEndToEndReport.status)}</strong>
                <p>
                  استغرق الفحص {Math.max(1, Math.round(fullExamEndToEndReport.totalDurationMs))} ms،
                  واكتملت الترجمة بنسبة {Math.round(fullExamEndToEndReport.translationCompletionPercent)}%.
                </p>
              </div>
            </div>

            <div className="metrics-row">
              <MetricCard label="الصفحات" value={fullExamEndToEndReport.pageCount} hint="حدود PDF المحفوظة" />
              <MetricCard label="الأسئلة" value={fullExamEndToEndReport.activeQuestionCount} hint="الأسئلة النشطة" />
              <MetricCard label="الدرجات" value={fullExamEndToEndReport.totalMarks} hint="مجموع الجاهزية" />
              <MetricCard label="الصيغ المقبولة" value={fullExamEndToEndReport.acceptedFormats.length} hint={fullExamEndToEndReport.acceptedFormats.map(formatLabel).join('، ') || 'لا توجد'} />
            </div>

            <div className="end-to-end-stage-grid">
              {fullExamEndToEndReport.stages.map((stage) => (
                <article
                  key={stage.stage}
                  className={`end-to-end-stage-card end-to-end-stage-${stage.status}`}
                >
                  <div className="end-to-end-stage-header">
                    <strong>{endToEndStageLabel(stage.stage)}</strong>
                    <span>{endToEndStageStatusLabel(stage.status)}</span>
                  </div>
                  <p>{stage.message}</p>
                  <small>{Math.max(0, Math.round(stage.durationMs))} ms</small>
                  {stage.errors.length ? (
                    <ul className="end-to-end-error-list">
                      {stage.errors.map((error) => <li key={error}>{error}</li>)}
                    </ul>
                  ) : null}
                  {stage.warnings.length ? (
                    <ul className="end-to-end-warning-list">
                      {stage.warnings.map((warning) => <li key={warning}>{warning}</li>)}
                    </ul>
                  ) : null}
                </article>
              ))}
            </div>

            {fullExamEndToEndReport.errors.length ? (
              <div className="analysis-note readiness-error">
                <strong>أخطاء المسار</strong>
                <ul>
                  {fullExamEndToEndReport.errors.map((error) => <li key={error}>{error}</li>)}
                </ul>
              </div>
            ) : fullExamEndToEndReport.warnings.length ? (
              <div className="analysis-note warning-card">
                <strong>ملاحظات المسار</strong>
                <ul>
                  {fullExamEndToEndReport.warnings.map((warning) => <li key={warning}>{warning}</li>)}
                </ul>
              </div>
            ) : (
              <div className="notice-card success-card">
                <ShieldCheck size={22} />
                <span>اجتازت جميع المراحل المطلوبة دون تحذيرات.</span>
              </div>
            )}
          </>
        ) : (
          <div className="empty-state">
            لم تُشغّل بوابة القبول الشامل بعد. الزر أعلاه يختبر المسار الحالي
            دون إعادة الترجمة أو تنزيل ملفات تلقائيًا.
          </div>
        )}
      </section>


      <section className="form-card wide-card export-acceptance-panel">
        <div className="section-heading">
          <p className="eyebrow">Phase 4-A6c</p>
          <h3>قبول تصدير الامتحان الكامل</h3>
          <p>
            يفحص هذا التقرير ملفات Word وPDF الناتجة فعليًا، بما يشمل بصمة البنية،
            ترتيب الأسئلة، مجموع الدرجات، الأجزاء، والمرفقات المدرجة مرة واحدة.
          </p>
        </div>

        {fullExamExportReport ? (
          <>
            <div className={`export-acceptance-status export-acceptance-${fullExamExportReport.status}`}>
              {fullExamExportReport.status === 'accepted' ? <CheckCircle2 size={24} /> : <AlertTriangle size={24} />}
              <div>
                <strong>{exportAcceptanceLabel(fullExamExportReport.status)}</strong>
                <p>
                  الصيغ المنشأة: {fullExamExportReport.generatedFormats.map(formatLabel).join('، ') || 'لا توجد'}
                  {' '}من أصل {fullExamExportReport.requestedFormats.map(formatLabel).join('، ')}.
                </p>
              </div>
            </div>

            <div className="metrics-row">
              <MetricCard label="الأسئلة" value={fullExamExportReport.activeQuestionCount} hint="الأسئلة النشطة" />
              <MetricCard label="مجموع الدرجات" value={fullExamExportReport.expectedTotalMarks} hint="دون تكرار درجات الأجزاء" />
              <MetricCard label="الأجزاء" value={fullExamExportReport.expectedPartCount} hint="البنية المتعددة" />
              <MetricCard label="المرفقات" value={fullExamExportReport.expectedAttachmentCount} hint="صور السؤال المقصوصة" />
              <MetricCard label="أسئلة مرتبطة بصفحات" value={fullExamExportReport.sourcePageLinkedQuestions} hint="من ورقة المصدر" />
              <MetricCard label="أسئلة متعددة الصفحات" value={fullExamExportReport.multiPageQuestions} hint="استمرارية المصدر" />
            </div>

            <div className="export-format-grid">
              {fullExamExportReport.formats.map((format) => (
                <article key={format.format} className={`export-format-card export-format-${format.status}`}>
                  <div className="export-format-card-header">
                    <strong>{formatLabel(format.format)}</strong>
                    <span>{format.status === 'accepted' ? 'مقبول' : format.status === 'needs_review' ? 'يحتاج مراجعة' : 'فشل'}</span>
                  </div>
                  <dl>
                    <div><dt>الحجم</dt><dd>{Math.max(1, Math.round(format.byteSize / 1024))} KB</dd></div>
                    <div><dt>الصفحات</dt><dd>{format.pageCount ?? 'غير محسوب'}</dd></div>
                    <div><dt>الأسئلة</dt><dd>{format.exportedQuestionCount}</dd></div>
                    <div><dt>الأجزاء</dt><dd>{format.exportedPartCount}</dd></div>
                    <div><dt>المرفقات</dt><dd>{format.exportedAttachmentCount}</dd></div>
                    <div><dt>الدرجات</dt><dd>{format.detectedTotalMarks}</dd></div>
                  </dl>
                  <ul className="export-check-list">
                    {format.checks.map((check) => (
                      <li key={`${format.format}-${check.code}`} className={check.passed ? 'check-pass' : 'check-fail'}>
                        {check.passed ? '✓' : '!'} {check.message}
                      </li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>

            {fullExamExportReport.warnings.length ? (
              <div className="analysis-note warning-card">
                <strong>تنبيهات قبول التصدير</strong>
                <ul>
                  {fullExamExportReport.warnings.map((warning) => <li key={warning}>{warning}</li>)}
                </ul>
              </div>
            ) : (
              <div className="notice-card success-card">
                <ShieldCheck size={22} />
                <span>لم تُسجّل تحذيرات في آخر ملفات التصدير المنشأة.</span>
              </div>
            )}
          </>
        ) : (
          <div className="empty-state">
            لم يُنشأ تقرير قبول التصدير بعد. حمّل Word أو PDF ليُفحص الملف الناتج فعليًا.
          </div>
        )}
      </section>


      <section className="form-card wide-card">
        <div className="section-heading">
          <p className="eyebrow">Phase 2-F2</p>
          <h3>أدوات الجودة التربوية</h3>
          <p>
            تولّد المنصة قراءة تأسيسية باستخدام Pareto لأولويات المراجعة، وRadar لمحاور الجاهزية، وFishbone لأسباب الضعف المحتملة. لا تزال أدوات مساعدة، لا لجنة اعتماد سماوية.
          </p>
        </div>

        <div className="inline-actions">
          <button type="button" className="primary-button" onClick={() => void handleGenerateQualityTools()} disabled={isGeneratingQualityTools || approvedQuestions.length === 0}>
            {isGeneratingQualityTools ? <Loader2 size={18} className="spin-icon" /> : <Radar size={18} />}
            توليد أدوات الجودة
          </button>
          <button type="button" className="danger-button" onClick={() => void handleClearQualityTools()} disabled={isGeneratingQualityTools || !qualityTools}>
            <Trash2 size={18} />
            حذف أدوات الجودة
          </button>
        </div>

        {qualityTools ? (
          <div className="quality-tools-panel">
            <div className="analysis-summary-card">
              <strong>الخلاصة</strong>
              <p>{qualityTools.qualitySummary}</p>
            </div>

            <div className="quality-columns">
              <div className="quality-card">
                <h4><BarChart3 size={18} /> Pareto أولويات المراجعة</h4>
                {qualityTools.paretoItems.length ? (
                  <ul className="analysis-list">
                    {qualityTools.paretoItems.map((item) => (
                      <li key={item.label}>
                        <span>{item.label}</span>
                        <strong>{item.count} · {item.cumulativePercent}%</strong>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="empty-state">لا توجد بيانات Pareto كافية.</p>
                )}
              </div>

              <div className="quality-card">
                <h4><Radar size={18} /> Radar محاور الجاهزية</h4>
                <ul className="analysis-list">
                  {Object.entries(qualityTools.radarAxes).map(([label, value]) => (
                    <li key={label}>
                      <span>{label}</span>
                      <strong>{value}%</strong>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="quality-card">
              <h4><GitBranch size={18} /> Fishbone أسباب الضعف المحتملة</h4>
              <div className="fishbone-grid">
                {Object.entries(qualityTools.fishboneCauses).map(([category, causes]) => (
                  <article key={category} className="fishbone-card">
                    <strong>{category}</strong>
                    <ul>
                      {causes.map((cause) => <li key={cause}>{cause}</li>)}
                    </ul>
                  </article>
                ))}
              </div>
            </div>

            {qualityTools.warnings.length ? (
              <div className="analysis-note warning-card">
                <strong>تنبيهات</strong>
                <ul>
                  {qualityTools.warnings.map((warning) => <li key={warning}>{warning}</li>)}
                </ul>
              </div>
            ) : null}

            <div className="analysis-note success-card">
              <strong>إجراءات ذات أولوية</strong>
              <ul>
                {qualityTools.priorityActions.map((action) => <li key={action}>{action}</li>)}
              </ul>
            </div>
          </div>
        ) : (
          <div className="empty-state">لم تُولّد أدوات الجودة بعد.</div>
        )}
      </section>

      <section className="form-card wide-card">
        <div className="section-heading">
          <p className="eyebrow">Phase 2-F1</p>
          <h3>التحليل التربوي التأسيسي</h3>
          <p>
            يقرأ هذا التحليل اتزان الورقة من حيث عدد الأسئلة، الدرجات، أوامر السؤال، عبء المراجعة، ووجود مسودة الإجابة ولقطات التخطيط. ليس تحليلًا نفسيًا قياسيًا ولا باريتو عظيمًا بعد، فقط أساس محترم بدل الفوضى.
          </p>
        </div>

        <div className="inline-actions">
          <button type="button" className="primary-button" onClick={() => void handleGenerateEducationalAnalysis()} disabled={isGeneratingAnalysis || approvedQuestions.length === 0}>
            {isGeneratingAnalysis ? <Loader2 size={18} className="spin-icon" /> : <BarChart3 size={18} />}
            توليد التحليل التربوي
          </button>
          <button type="button" className="danger-button" onClick={() => void handleClearEducationalAnalysis()} disabled={isGeneratingAnalysis || !educationalAnalysis}>
            <Trash2 size={18} />
            حذف التحليل
          </button>
        </div>

        {educationalAnalysis ? (
          <div className="educational-analysis-panel">
            <div className="analysis-summary-card">
              <strong>الخلاصة</strong>
              <p>{educationalAnalysis.educationalSummary}</p>
            </div>

            <div className="analysis-grid">
              <MetricCard label="الأسئلة النشطة" value={educationalAnalysis.questionCount} hint="بعد الحذف" />
              <MetricCard label="مجموع الدرجات" value={educationalAnalysis.totalMarks} hint="من البطاقات" />
              <MetricCard label="متوسط الدرجة" value={educationalAnalysis.averageMarks} hint="لكل سؤال" />
              <MetricCard label="عبء المراجعة" value={educationalAnalysis.reviewLoad} hint="مؤشر تأسيسي" />
            </div>

            <div className="analysis-columns">
              <div>
                <h4>توزيع أوامر السؤال</h4>
                {Object.entries(educationalAnalysis.commandDistribution).length ? (
                  <ul className="analysis-list">
                    {Object.entries(educationalAnalysis.commandDistribution).map(([label, value]) => (
                      <li key={label}><span>{label}</span><strong>{value}</strong></li>
                    ))}
                  </ul>
                ) : (
                  <p className="empty-state">لا يوجد توزيع متاح.</p>
                )}
              </div>

              <div>
                <h4>توزيع الدرجات</h4>
                {Object.entries(educationalAnalysis.marksDistribution).length ? (
                  <ul className="analysis-list">
                    {Object.entries(educationalAnalysis.marksDistribution).map(([label, value]) => (
                      <li key={label}><span>{label}</span><strong>{value}</strong></li>
                    ))}
                  </ul>
                ) : (
                  <p className="empty-state">لا يوجد توزيع متاح.</p>
                )}
              </div>
            </div>

            {educationalAnalysis.warnings.length ? (
              <div className="analysis-note warning-card">
                <strong>تنبيهات</strong>
                <ul>
                  {educationalAnalysis.warnings.map((warning) => <li key={warning}>{warning}</li>)}
                </ul>
              </div>
            ) : null}

            <div className="analysis-note success-card">
              <strong>توصيات</strong>
              <ul>
                {educationalAnalysis.recommendations.map((recommendation) => <li key={recommendation}>{recommendation}</li>)}
              </ul>
            </div>
          </div>
        ) : (
          <div className="empty-state">لم يُولّد التحليل التربوي بعد.</div>
        )}
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

        </div>
      </details>

      <section className="form-card export-legacy-hidden" aria-hidden="true">
        <div className="section-heading">
          <p className="eyebrow">بيانات الورقة</p>
          <h3>{metadata.paperTitle}</h3>
        </div>
        <dl className="metadata-list">
          <div><dt>المدرسة</dt><dd>{metadata.schoolName}</dd></div>
          <div><dt>المادة</dt><dd>{metadata.subject}</dd></div>
          <div><dt>الصف</dt><dd>{metadata.grade}</dd></div>
          <div><dt>الزمن</dt><dd>{metadata.duration}</dd></div>
          <div><dt>نوع النسخة</dt><dd>{studentVersionLabel}</dd></div>
          <div><dt>الصيغ</dt><dd>DOCX + PDF</dd></div>
        </dl>
      </section>

      <section className="form-card export-legacy-hidden" aria-hidden="true">
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
