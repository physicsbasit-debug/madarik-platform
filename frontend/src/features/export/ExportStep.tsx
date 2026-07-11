import { AlertTriangle, BarChart3, CheckCircle2, Download, FileText, GitBranch, KeyRound, Loader2, Radar, ShieldCheck, Trash2 } from 'lucide-react';
import { useState } from 'react';
import type { AnswerKeyItem, EducationalAnalysisReport, EducationalQualityToolsReport, GlossaryTerm, ProjectMetadata, ProjectReadinessReport, QuestionItem } from '../../types/project';
import { MetricCard } from '../../components/MetricCard';

interface ExportStepProps {
  metadata: ProjectMetadata;
  questions: QuestionItem[];
  glossary: GlossaryTerm[];
  answerKey: AnswerKeyItem[];
  educationalAnalysis: EducationalAnalysisReport | null;
  qualityTools: EducationalQualityToolsReport | null;
  readiness: ProjectReadinessReport | null;
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

export function ExportStep({
  metadata,
  questions,
  glossary,
  answerKey,
  educationalAnalysis,
  qualityTools,
  readiness,
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
  const [isGeneratingAnswerKey, setIsGeneratingAnswerKey] = useState(false);
  const [isGeneratingAnalysis, setIsGeneratingAnalysis] = useState(false);
  const [isGeneratingQualityTools, setIsGeneratingQualityTools] = useState(false);
  const [exportMessage, setExportMessage] = useState('تصدير DOCX وPDF متاح مع فحص جاهزية قبل التصدير، ودعم الشعار والمرفقات ونسخ العمل JSON ومسودة نموذج إجابة وتحليل تربوي وأدوات جودة تأسيسية للمعلم.');

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
          <MetricCard label="التحليل التربوي" value={educationalAnalysis ? 1 : 0} hint="تأسيسي" />
          <MetricCard label="أدوات الجودة" value={qualityTools ? 1 : 0} hint="Pareto/Radar/Fishbone" />
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
