import { ArrowLeft, ArrowRight, DatabaseZap, Download, FileText, RefreshCcw, Upload, Wifi, WifiOff } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { StepNavigation } from '../components/StepNavigation';
import { steps } from '../constants/steps';
import { defaultMetadata, sampleGlossary, sampleQuestions } from '../data/mockProject';
import { ExtractionStep } from '../features/extraction/ExtractionStep';
import { ExportStep } from '../features/export/ExportStep';
import { FileUploadStep } from '../features/file-upload/FileUploadStep';
import { GlossaryStep } from '../features/glossary/GlossaryStep';
import { ProjectSetupStep } from '../features/project-setup/ProjectSetupStep';
import { ReviewStep } from '../features/review/ReviewStep';
import {
  bulkUpdateQuestionStatus,
  createProject,
  exportProjectDocx,
  exportProjectPdf,
  exportProjectSnapshot,
  generateGlossaryFromQuestions,
  deleteProject,
  deleteQuestionAsset,
  deleteSchoolLogo,
  loadDemoContent,
  parseExtractedQuestions,
  reorderQuestions,
  setUploadedFileInfo,
  translateProjectQuestions,
  uploadQuestionAsset,
  uploadPdfAndExtractText,
  uploadPdfOcrAndExtractText,
  uploadImageAndExtractText,
  uploadSchoolLogo,
  updateGlossaryTerm as updateGlossaryTermOnServer,
  updateProjectMetadata,
  updateProjectStep,
  updateQuestion as updateQuestionOnServer,
  getTranslationProviderStatus,
  getProjectReadiness,
  importProjectSnapshot,
} from '../services/api';
import type {
  ApiConnectionStatus,
  ExtractedTextInfo,
  GlossaryTerm,
  ProjectMetadata,
  ProjectReadinessReport,
  ProjectSession,
  QuestionItem,
  QuestionStatus,
  SchoolLogoInfo,
  StepKey,
  UploadedFileInfo,
  TranslationProviderStatus,
} from '../types/project';

function sortQuestions(questions: QuestionItem[]) {
  return [...questions].sort((a, b) => a.orderIndex - b.orderIndex);
}

function statusLabel(status: ApiConnectionStatus) {
  switch (status) {
    case 'connecting':
      return 'الاتصال بالخلفية...';
    case 'connected':
      return 'متصل بـ FastAPI';
    case 'syncing':
      return 'مزامنة مؤقتة...';
    case 'offline':
      return 'وضع واجهة محلي';
  }
}

function applyProjectSession(
  project: ProjectSession,
  setters: {
    setProjectId: (projectId: string) => void;
    setMetadata: (metadata: ProjectMetadata) => void;
    setUploadedFile: (fileInfo: UploadedFileInfo | null) => void;
    setSchoolLogo: (schoolLogo: SchoolLogoInfo | null) => void;
    setExtractedText: (extractedText: ExtractedTextInfo | null) => void;
    setQuestions: (questions: QuestionItem[]) => void;
    setGlossary: (glossary: GlossaryTerm[]) => void;
  },
) {
  setters.setProjectId(project.id);
  setters.setMetadata(project.metadata);
  setters.setUploadedFile(project.uploadedFile);
  setters.setSchoolLogo(project.schoolLogo);
  setters.setExtractedText(project.extractedText);
  setters.setQuestions(project.questions);
  setters.setGlossary(project.glossary);
}

export function App() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<ApiConnectionStatus>('connecting');
  const [lastSyncNote, setLastSyncNote] = useState('يتم إنشاء جلسة مشروع مؤقتة...');
  const [metadata, setMetadata] = useState<ProjectMetadata>(defaultMetadata);
  const [uploadedFile, setUploadedFile] = useState<UploadedFileInfo | null>(null);
  const [schoolLogo, setSchoolLogo] = useState<SchoolLogoInfo | null>(null);
  const [extractedText, setExtractedText] = useState<ExtractedTextInfo | null>(null);
  const [questions, setQuestions] = useState<QuestionItem[]>(sampleQuestions);
  const [glossary, setGlossary] = useState<GlossaryTerm[]>(sampleGlossary);
  const [translationProviderStatus, setTranslationProviderStatus] = useState<TranslationProviderStatus | null>(null);
  const [projectReadiness, setProjectReadiness] = useState<ProjectReadinessReport | null>(null);

  const activeStep = steps[activeIndex];
  const progressLabel = useMemo(() => `${activeIndex + 1} من ${steps.length}`, [activeIndex]);

  const approvedCount = questions.filter((question) => question.status === 'approved').length;
  const needsReviewCount = questions.filter((question) => question.status === 'needs_review').length;
  const deletedCount = questions.filter((question) => question.status === 'deleted').length;

  const applyProject = useCallback((project: ProjectSession) => {
    applyProjectSession(project, {
      setProjectId,
      setMetadata,
      setUploadedFile,
      setSchoolLogo,
      setExtractedText,
      setQuestions,
      setGlossary,
    });
  }, []);

  const bootstrapProject = useCallback(async () => {
    setApiStatus('connecting');
    setLastSyncNote('جاري إنشاء جلسة مؤقتة من Backend...');

    try {
      const createdProject = await createProject(defaultMetadata);
      const providerStatus = await getTranslationProviderStatus();
      setTranslationProviderStatus(providerStatus);
      const hydratedProject = await loadDemoContent(createdProject.id);
      applyProject(hydratedProject);
      setApiStatus('connected');
      setLastSyncNote(`تم إنشاء مشروع مؤقت: ${hydratedProject.id.slice(0, 8)}`);
    } catch (error) {
      console.error(error);
      setProjectId(null);
      setMetadata(defaultMetadata);
      setUploadedFile(null);
      setSchoolLogo(null);
      setExtractedText(null);
      setQuestions(sampleQuestions);
      setGlossary(sampleGlossary);
      setTranslationProviderStatus({ provider: 'mock', configured: false, model: '', fallback: 'mock' });
      setApiStatus('offline');
      setLastSyncNote('تعذر الاتصال بالخلفية. تعمل الواجهة ببيانات محلية مؤقتة. يا لها من بداية درامية، لكنها مقبولة في التطوير.');
    }
  }, [applyProject]);

  useEffect(() => {
    void bootstrapProject();
  }, [bootstrapProject]);

  useEffect(() => {
    if (!projectId || apiStatus === 'offline') return;
    void updateProjectStep(projectId, activeStep.key).catch((error: unknown) => {
      console.error(error);
      setApiStatus('offline');
      setLastSyncNote('تعذرت مزامنة الخطوة الحالية مع Backend.');
    });
  }, [activeStep.key, apiStatus, projectId]);

  function goNext() {
    setActiveIndex((current) => Math.min(current + 1, steps.length - 1));
  }

  function goPrevious() {
    setActiveIndex((current) => Math.max(current - 1, 0));
  }


  async function downloadProjectSnapshot() {
    if (!projectId || apiStatus === 'offline') {
      setLastSyncNote('لا يمكن حفظ نسخة مشروع دون اتصال Backend.');
      return;
    }

    setApiStatus('syncing');
    try {
      const snapshot = await exportProjectSnapshot(projectId);
      const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: 'application/json;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      const safeTitle = (metadata.paperTitle || 'madarik-project').replace(/[^A-Za-z0-9_\-]+/g, '_');
      link.href = url;
      link.download = `${safeTitle || 'madarik-project'}_snapshot.json`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setApiStatus('connected');
      setLastSyncNote('تم تنزيل نسخة JSON من مشروع العمل الحالي. احتفظ بها لاستكمال العمل لاحقًا.');
    } catch (error) {
      console.error(error);
      setApiStatus('connected');
      setLastSyncNote('فشل تنزيل نسخة المشروع.');
    }
  }

  async function importProjectSnapshotFile(file: File | null) {
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.json')) {
      setLastSyncNote('ملف الاستعادة يجب أن يكون JSON صادرًا من منصة مدارك، لا ملفًا مجهولًا جاء من ظلام الإنترنت.');
      return;
    }

    if (apiStatus === 'offline') {
      setLastSyncNote('لا يمكن استعادة مشروع دون اتصال Backend.');
      return;
    }

    setApiStatus('syncing');
    try {
      const rawText = await file.text();
      const snapshot = JSON.parse(rawText) as unknown;
      const project = await importProjectSnapshot(snapshot);
      setActiveIndex(0);
      applyProject(project);
      setProjectReadiness(null);
      setApiStatus('connected');
      setLastSyncNote(`تم استيراد نسخة المشروع كجلسة جديدة: ${project.id.slice(0, 8)}`);
    } catch (error) {
      console.error(error);
      setApiStatus('connected');
      setLastSyncNote('فشل استيراد نسخة المشروع. تأكد أن الملف صادر من منصة مدارك ولم يتم العبث به كما يفعل البشر عادة.');
    }
  }

  async function resetProject() {
    const confirmed = window.confirm('سيتم مسح مشروع العمل الحالي فقط. هل تريد المتابعة؟');
    if (!confirmed) return;

    if (projectId) {
      await deleteProject(projectId).catch((error: unknown) => console.error(error));
    }

    setActiveIndex(0);
    await bootstrapProject();
  }

  function handleMetadataChange(nextMetadata: ProjectMetadata) {
    setMetadata(nextMetadata);

    if (!projectId || apiStatus === 'offline') return;
    setApiStatus('syncing');
    updateProjectMetadata(projectId, nextMetadata)
      .then((project) => {
        applyProject(project);
        setApiStatus('connected');
        setLastSyncNote('تمت مزامنة بيانات الورقة مع Backend.');
      })
      .catch((error: unknown) => {
        console.error(error);
        setApiStatus('offline');
        setLastSyncNote('فشلت مزامنة بيانات الورقة. بقيت التعديلات محليًا.');
      });
  }

  async function handleLogoSelected(file: File | null) {
    if (!file) return;

    if (!projectId || apiStatus === 'offline') {
      setLastSyncNote('لا يمكن رفع الشعار دون اتصال Backend. الشعار يحتاج جلسة مؤقتة في الخلفية.');
      return;
    }

    setApiStatus('syncing');
    try {
      const project = await uploadSchoolLogo(projectId, file);
      applyProject(project);
      setApiStatus('connected');
      setLastSyncNote('تم رفع شعار المدرسة وربطه بتصدير DOCX وPDF.');
    } catch (error) {
      console.error(error);
      setApiStatus('connected');
      setLastSyncNote('فشل رفع الشعار. يدعم Phase 1-F3 ملفات PNG وJPG بحجم صغير.');
    }
  }

  async function handleLogoRemove() {
    setSchoolLogo(null);

    if (!projectId || apiStatus === 'offline') return;

    setApiStatus('syncing');
    try {
      const project = await deleteSchoolLogo(projectId);
      applyProject(project);
      setApiStatus('connected');
      setLastSyncNote('تم حذف شعار المدرسة من جلسة المشروع.');
    } catch (error) {
      console.error(error);
      setApiStatus('connected');
      setLastSyncNote('فشل حذف الشعار من Backend. بقي الحذف محليًا فقط.');
    }
  }

  function handleFileSelected(file: File | null) {
    if (!file) {
      setUploadedFile(null);
      setExtractedText(null);

      if (!projectId || apiStatus === 'offline') return;
      setApiStatus('syncing');
      setUploadedFileInfo(projectId, null)
        .then((project) => {
          applyProject(project);
          setApiStatus('connected');
          setLastSyncNote('تمت إزالة الملف ونتيجة الاستخراج من الجلسة.');
        })
        .catch((error: unknown) => {
          console.error(error);
          setApiStatus('offline');
          setLastSyncNote('فشلت إزالة معلومات الملف من Backend. بقيت الحالة محليًا.');
        });
      return;
    }

    const fileInfo: UploadedFileInfo = { name: file.name, size: file.size, type: file.type || 'غير معروف' };
    setUploadedFile(fileInfo);
    setExtractedText(null);

    if (!projectId || apiStatus === 'offline') {
      setLastSyncNote('تم اختيار الملف محليًا فقط. لا يمكن استخلاص PDF دون اتصال Backend. الكون يضحك في الخلفية.');
      return;
    }

    const isImageFile = file.type.startsWith('image/') || /\.(png|jpe?g|webp)$/i.test(file.name);
    const isPdfFile = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');

    if (!isImageFile && !isPdfFile) {
      setExtractedText({
        text: '',
        preview: '',
        pageCount: 0,
        characterCount: 0,
        isTextBased: false,
        message: 'يدعم Phase 1-I2 ملفات PDF النصية أو المصوّرة البسيطة وصور PNG/JPG/WEBP فقط.',
      });
      setLastSyncNote('نوع الملف غير مدعوم في هذه المرحلة. لا نطلب من التطبيق قراءة كل مخلوقات التخزين مرة واحدة.');
      return;
    }

    setApiStatus('syncing');
    const extractionRequest = isImageFile
      ? uploadImageAndExtractText(projectId, file)
      : uploadPdfAndExtractText(projectId, file).then((project) => {
          if (project.extractedText?.isTextBased) return project;
          return uploadPdfOcrAndExtractText(projectId, file);
        });

    extractionRequest
      .then((project) => {
        applyProject(project);
        setApiStatus('connected');
        setLastSyncNote(project.extractedText?.message ?? 'تم رفع الملف ومحاولة استخراج النص.');
      })
      .catch((error: unknown) => {
        console.error(error);
        setApiStatus('connected');
        setUploadedFile(fileInfo);
        setExtractedText({
          text: '',
          preview: '',
          pageCount: 0,
          characterCount: 0,
          isTextBased: false,
          message: isImageFile
            ? 'تعذر تشغيل OCR على الصورة. جرّب صورة أوضح أو قصّ منطقة السؤال فقط.'
            : 'تعذر استخراج النص من PDF نصيًا أو عبر OCR مبدئي. تأكد من جودة الملف أو جرّب صورة واضحة.',
        });
        setLastSyncNote(isImageFile ? 'فشل OCR المبدئي للصورة.' : 'فشل استخراج النص من PDF نصيًا وOCR. جرّب صورة واضحة أو ملفًا أعلى جودة.');
      });
  }


  async function bulkUpdateReviewStatus(status: QuestionStatus, includeDeleted = false) {
    if (!projectId || apiStatus === 'offline') {
      setLastSyncNote('لا يمكن تنفيذ إجراء جماعي دون اتصال Backend.');
      return;
    }

    setApiStatus('syncing');
    try {
      const project = await bulkUpdateQuestionStatus(projectId, status, includeDeleted);
      applyProject(project);
      setProjectReadiness(null);
      setApiStatus('connected');
      const label = status === 'approved' ? 'معتمد' : status === 'needs_review' ? 'يحتاج مراجعة' : 'محذوف';
      setLastSyncNote(`تم تحديث حالة الأسئلة جماعيًا إلى: ${label}.`);
    } catch (error) {
      console.error(error);
      setApiStatus('connected');
      setLastSyncNote('فشل تنفيذ الإجراء الجماعي على الأسئلة.');
    }
  }

  async function handleQuestionAssetUpload(questionId: string, file: File) {
    if (!projectId || apiStatus === 'offline') {
      setLastSyncNote('لا يمكن ربط مرفق بالسؤال دون اتصال Backend. المرفقات تُحفظ مؤقتًا في الخلفية.');
      return;
    }

    setApiStatus('syncing');
    try {
      const project = await uploadQuestionAsset(projectId, questionId, file);
      applyProject(project);
      setApiStatus('connected');
      setLastSyncNote('تم ربط الصورة/الجدول ببطاقة السؤال وسيظهر في DOCX وPDF.');
    } catch (error) {
      console.error(error);
      setApiStatus('connected');
      setLastSyncNote('فشل رفع مرفق السؤال. يدعم Phase 1-H1 صور PNG وJPG بحجم لا يتجاوز 2MB.');
    }
  }

  async function handleQuestionAssetDelete(questionId: string, assetId: string) {
    if (!projectId || apiStatus === 'offline') {
      setLastSyncNote('لا يمكن حذف المرفق دون اتصال Backend.');
      return;
    }

    setApiStatus('syncing');
    try {
      const project = await deleteQuestionAsset(projectId, questionId, assetId);
      applyProject(project);
      setApiStatus('connected');
      setLastSyncNote('تم حذف مرفق السؤال من الجلسة المؤقتة.');
    } catch (error) {
      console.error(error);
      setApiStatus('connected');
      setLastSyncNote('فشل حذف مرفق السؤال.');
    }
  }


  function updateQuestion(questionId: string, updates: Partial<QuestionItem>) {
    setQuestions((currentQuestions) =>
      currentQuestions.map((question) => (question.id === questionId ? { ...question, ...updates } : question)),
    );

    if (!projectId || apiStatus === 'offline') return;
    setApiStatus('syncing');
    updateQuestionOnServer(projectId, questionId, updates)
      .then((project) => {
        applyProject(project);
        setApiStatus('connected');
        setLastSyncNote('تمت مزامنة بطاقة السؤال مع Backend.');
      })
      .catch((error: unknown) => {
        console.error(error);
        setApiStatus('offline');
        setLastSyncNote('فشلت مزامنة بطاقة السؤال. بقي التعديل محليًا.');
      });
  }

  function moveQuestion(questionId: string, direction: 'up' | 'down') {
    setQuestions((currentQuestions) => {
      const movableQuestions = sortQuestions(currentQuestions).filter((question) => question.status !== 'deleted');
      const currentPosition = movableQuestions.findIndex((question) => question.id === questionId);
      const targetPosition = direction === 'up' ? currentPosition - 1 : currentPosition + 1;

      if (currentPosition < 0 || targetPosition < 0 || targetPosition >= movableQuestions.length) {
        return currentQuestions;
      }

      const currentQuestion = movableQuestions[currentPosition];
      const targetQuestion = movableQuestions[targetPosition];
      const nextQuestions = currentQuestions.map((question) => {
        if (question.id === currentQuestion.id) return { ...question, orderIndex: targetQuestion.orderIndex };
        if (question.id === targetQuestion.id) return { ...question, orderIndex: currentQuestion.orderIndex };
        return question;
      });

      if (projectId && apiStatus !== 'offline') {
        const orderedQuestionIds = sortQuestions(nextQuestions).map((question) => question.id);
        setApiStatus('syncing');
        reorderQuestions(projectId, orderedQuestionIds)
          .then((project) => {
            applyProject(project);
            setApiStatus('connected');
            setLastSyncNote('تمت مزامنة ترتيب الأسئلة مع Backend.');
          })
          .catch((error: unknown) => {
            console.error(error);
            setApiStatus('offline');
            setLastSyncNote('فشلت مزامنة ترتيب الأسئلة. بقي الترتيب محليًا.');
          });
      }

      return nextQuestions;
    });
  }

  function updateGlossaryTerm(termId: string, updates: Partial<GlossaryTerm>) {
    setGlossary((currentGlossary) => currentGlossary.map((term) => (term.id === termId ? { ...term, ...updates } : term)));

    if (!projectId || apiStatus === 'offline') return;
    setApiStatus('syncing');
    updateGlossaryTermOnServer(projectId, termId, updates)
      .then((project) => {
        applyProject(project);
        setApiStatus('connected');
        setLastSyncNote('تمت مزامنة قاموس الورقة مع Backend.');
      })
      .catch((error: unknown) => {
        console.error(error);
        setApiStatus('offline');
        setLastSyncNote('فشلت مزامنة قاموس الورقة. بقي التعديل محليًا.');
      });
  }

  async function parseQuestionsFromExtractedText() {
    if (!projectId || apiStatus === 'offline') {
      setLastSyncNote('لا يمكن تقسيم النص دون اتصال Backend. النص موجود، لكن المحلل في الخلفية وليس في الواجهة.');
      return;
    }

    if (!extractedText?.isTextBased) {
      setLastSyncNote('ارفع PDF نصيًا أولًا قبل تحويل النص إلى أسئلة. لا نحلل الهواء، رغم أن بعض الاجتماعات تفعل ذلك.');
      return;
    }

    setApiStatus('syncing');
    try {
      const project = await parseExtractedQuestions(projectId);
      applyProject(project);
      setApiStatus('connected');
      setLastSyncNote(`تم تحويل النص إلى ${project.questions.length} بطاقة سؤال تحتاج مراجعة.`);
    } catch (error) {
      console.error(error);
      setApiStatus('connected');
      setLastSyncNote('فشل تقسيم النص إلى أسئلة. قد يحتاج الملف إلى تنسيق أوضح أو OCR لاحقًا.');
    }
  }



  async function translateQuestions() {
    if (!projectId || apiStatus === 'offline') {
      setLastSyncNote('لا يمكن تشغيل ترجمة الأسئلة دون اتصال Backend. المترجم موجود في الخلفية، لا في عالم الخيال.');
      return;
    }

    if (questions.filter((question) => question.status !== 'deleted').length === 0) {
      setLastSyncNote('لا توجد أسئلة نشطة قابلة للترجمة. حذف كل شيء ثم طلب الترجمة رياضة ذهنية غريبة.');
      return;
    }

    setApiStatus('syncing');
    try {
      const project = await translateProjectQuestions(projectId);
      applyProject(project);
      setApiStatus('connected');
      setActiveIndex(4);
      setLastSyncNote('تمت ترجمة الأسئلة عبر طبقة مزود Phase 1-G1 مع fallback آمن وقابل للمراجعة.');
    } catch (error) {
      console.error(error);
      setApiStatus('connected');
      setLastSyncNote('تعذر تشغيل ترجمة الأسئلة. تحقق من وجود أسئلة محللة ثم أعد المحاولة.');
    }
  }

  async function generateGlossaryFromQuestionCards() {
    if (!projectId || apiStatus === 'offline') {
      setLastSyncNote('لا يمكن توليد قاموس حقيقي دون اتصال Backend. القاموس الحالي محلي فقط.');
      return;
    }

    if (questions.length === 0) {
      setLastSyncNote('لا توجد أسئلة يمكن استخراج مصطلحات منها. نحتاج مادة خام، لا نقرأ النوايا.');
      return;
    }

    setApiStatus('syncing');
    try {
      const project = await generateGlossaryFromQuestions(projectId);
      applyProject(project);
      setApiStatus('connected');
      setLastSyncNote(`تم توليد ${project.glossary.length} مصطلحًا من بطاقات الأسئلة.`);
    } catch (error) {
      console.error(error);
      setApiStatus('connected');
      setLastSyncNote('فشل توليد قاموس الورقة. قد لا تحتوي الأسئلة على مصطلحات ضمن القاموس الأولي.');
    }
  }


  async function refreshProjectReadiness() {
    if (!projectId || apiStatus === 'offline') {
      setProjectReadiness(null);
      setLastSyncNote('لا يمكن فحص الجاهزية دون اتصال Backend.');
      return;
    }

    setApiStatus('syncing');
    try {
      const report = await getProjectReadiness(projectId);
      setProjectReadiness(report);
      setApiStatus('connected');
      setLastSyncNote(report.ready ? 'فحص الجاهزية: الورقة قابلة للتصدير.' : 'فحص الجاهزية: توجد ملاحظات قبل التصدير.');
    } catch (error) {
      console.error(error);
      setApiStatus('connected');
      setLastSyncNote('تعذر فحص جاهزية التصدير.');
    }
  }


  async function exportDocx() {
    if (!projectId || apiStatus === 'offline') {
      setLastSyncNote('لا يمكن إنشاء DOCX دون اتصال Backend. ملف Word يحتاج محرك التصدير في الخلفية.');
      return;
    }

    const report = await getProjectReadiness(projectId);
    setProjectReadiness(report);
    if (!report.ready) {
      setLastSyncNote('فحص الجاهزية منع تصدير Word حتى معالجة الملاحظات المانعة.');
      return;
    }

    setApiStatus('syncing');
    try {
      const blob = await exportProjectDocx(projectId);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const safeTitle = (metadata.paperTitle || 'madarik-export').replace(/[^A-Za-z0-9_\-]+/g, '_');
      link.download = `${safeTitle || 'madarik-export'}.docx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setApiStatus('connected');
      setLastSyncNote('تم إنشاء ملف Word عبر Backend بنجاح.');
    } catch (error) {
      console.error(error);
      setApiStatus('connected');
      setLastSyncNote('فشل إنشاء ملف Word. تحقق من وجود أسئلة نشطة ثم أعد المحاولة.');
      throw error;
    }
  }


  async function exportPdf() {
    if (!projectId || apiStatus === 'offline') {
      setLastSyncNote('لا يمكن إنشاء PDF دون اتصال Backend. ملف PDF يحتاج محرك التصدير في الخلفية.');
      return;
    }

    const report = await getProjectReadiness(projectId);
    setProjectReadiness(report);
    if (!report.ready) {
      setLastSyncNote('فحص الجاهزية منع تصدير PDF حتى معالجة الملاحظات المانعة.');
      return;
    }

    setApiStatus('syncing');
    try {
      const blob = await exportProjectPdf(projectId);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const safeTitle = (metadata.paperTitle || 'madarik-export').replace(/[^A-Za-z0-9_\-]+/g, '_');
      link.download = `${safeTitle || 'madarik-export'}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setApiStatus('connected');
      setLastSyncNote('تم إنشاء ملف PDF عبر Backend بنجاح.');
    } catch (error) {
      console.error(error);
      setApiStatus('connected');
      setLastSyncNote('فشل إنشاء ملف PDF. تحقق من وجود أسئلة نشطة ثم أعد المحاولة.');
      throw error;
    }
  }

  async function reloadDemoFromBackend() {
    if (!projectId || apiStatus === 'offline') {
      setQuestions(sampleQuestions);
      setGlossary(sampleGlossary);
      setLastSyncNote('تمت إعادة تحميل البيانات التجريبية محليًا.');
      return;
    }

    setApiStatus('syncing');
    try {
      const project = await loadDemoContent(projectId);
      applyProject(project);
      setApiStatus('connected');
      setLastSyncNote('تم تحميل الأسئلة والقاموس التجريبيين من Backend.');
    } catch (error) {
      console.error(error);
      setApiStatus('offline');
      setLastSyncNote('فشل تحميل البيانات التجريبية من Backend.');
    }
  }

  return (
    <main className="app-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">Phase 1-H1 Question Assets</p>
          <h1>منصة مدارك</h1>
          <p className="hero-text">
            واجهة متعددة الخطوات تستطيع رفع PDF نصي، استخراج النص، تحويله إلى بطاقات أسئلة، توليد قاموس، ترجمة أولية، ربط صور/جداول يدوية بالأسئلة، ثم تصدير DOCX وPDF بتنسيق RTL. لا يوجد OCR أو استخراج صور تلقائي من PDF بعد، فالوحوش التقنية تنتظر دورها.
          </p>
        </div>
        <button className="ghost-button" type="button" onClick={() => void resetProject()}>
          <RefreshCcw size={18} />
          مشروع جديد / إعادة البدء
        </button>
      </section>

      <section className={`api-banner api-banner-${apiStatus}`} aria-label="حالة الاتصال بالخلفية">
        <div>
          {apiStatus === 'offline' ? <WifiOff size={20} /> : <Wifi size={20} />}
          <strong>{statusLabel(apiStatus)}</strong>
        </div>
        <span>{lastSyncNote}</span>
        {projectId ? <code dir="ltr">project: {projectId.slice(0, 8)}</code> : <code dir="ltr">local fallback</code>}
      </section>

      <section className="status-strip" aria-label="ملخص حالة المشروع">
        <div>
          <span>معتمد</span>
          <strong>{approvedCount}</strong>
        </div>
        <div>
          <span>يحتاج مراجعة</span>
          <strong>{needsReviewCount}</strong>
        </div>
        <div>
          <span>محذوف</span>
          <strong>{deletedCount}</strong>
        </div>
        <div>
          <span>نوع النسخة</span>
          <strong>{metadata.outputMode === 'bilingual' ? 'ثنائية' : 'عربية'}</strong>
        </div>
        <div>
          <span>مرحلة التطوير</span>
          <strong>Phase 1-RC1</strong>
        </div>
      </section>

      <section className="workspace-card">
        <StepNavigation steps={steps} activeIndex={activeIndex} onSelectStep={setActiveIndex} />

        <section className="step-content">
          <div className="step-header">
            <div>
              <p className="eyebrow">الخطوة {progressLabel}</p>
              <h2>{activeStep.label}</h2>
              <p>{activeStep.description}</p>
            </div>
            <DatabaseZap size={34} aria-hidden="true" />
          </div>

          <StepContent
            stepKey={activeStep.key}
            metadata={metadata}
            schoolLogo={schoolLogo}
            uploadedFile={uploadedFile}
            extractedText={extractedText}
            questions={questions}
            glossary={glossary}
            translationProviderStatus={translationProviderStatus}
            onMetadataChange={handleMetadataChange}
            onLogoSelected={handleLogoSelected}
            onLogoRemove={handleLogoRemove}
            onFileSelected={handleFileSelected}
            onUpdateQuestion={updateQuestion}
            onMoveQuestion={moveQuestion}
            onUpdateGlossaryTerm={updateGlossaryTerm}
            onGenerateGlossary={generateGlossaryFromQuestionCards}
            onTranslateQuestions={translateQuestions}
            onBulkUpdateStatus={bulkUpdateReviewStatus}
            onUploadQuestionAsset={handleQuestionAssetUpload}
            onDeleteQuestionAsset={handleQuestionAssetDelete}
            onReloadDemo={reloadDemoFromBackend}
            onParseQuestions={parseQuestionsFromExtractedText}
            onExportDocx={exportDocx}
            onExportPdf={exportPdf}
            onRefreshReadiness={refreshProjectReadiness}
            projectReadiness={projectReadiness}
            canExportDocx={Boolean(projectId && apiStatus !== 'offline')}
            canExportPdf={Boolean(projectId && apiStatus !== 'offline')}
          />

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

interface StepContentProps {
  stepKey: StepKey;
  metadata: ProjectMetadata;
  schoolLogo: SchoolLogoInfo | null;
  uploadedFile: UploadedFileInfo | null;
  extractedText: ExtractedTextInfo | null;
  questions: QuestionItem[];
  glossary: GlossaryTerm[];
  translationProviderStatus: TranslationProviderStatus | null;
  projectReadiness: ProjectReadinessReport | null;
  onMetadataChange: (metadata: ProjectMetadata) => void;
  onLogoSelected: (file: File | null) => void;
  onLogoRemove: () => void;
  onFileSelected: (file: File | null) => void;
  onUpdateQuestion: (questionId: string, updates: Partial<QuestionItem>) => void;
  onMoveQuestion: (questionId: string, direction: 'up' | 'down') => void;
  onUpdateGlossaryTerm: (termId: string, updates: Partial<GlossaryTerm>) => void;
  onGenerateGlossary: () => void;
  onTranslateQuestions: () => void;
  onBulkUpdateStatus: (status: QuestionStatus, includeDeleted?: boolean) => void;
  onUploadQuestionAsset: (questionId: string, file: File) => void;
  onDeleteQuestionAsset: (questionId: string, assetId: string) => void;
  onReloadDemo: () => void;
  onParseQuestions: () => void;
  onExportDocx: () => Promise<void>;
  onExportPdf: () => Promise<void>;
  onRefreshReadiness: () => Promise<void>;
  canExportDocx: boolean;
  canExportPdf: boolean;
}

function StepContent({
  stepKey,
  metadata,
  schoolLogo,
  uploadedFile,
  extractedText,
  questions,
  glossary,
  translationProviderStatus,
  projectReadiness,
  onMetadataChange,
  onLogoSelected,
  onLogoRemove,
  onFileSelected,
  onUpdateQuestion,
  onMoveQuestion,
  onUpdateGlossaryTerm,
  onGenerateGlossary,
  onTranslateQuestions,
  onBulkUpdateStatus,
  onUploadQuestionAsset,
  onDeleteQuestionAsset,
  onReloadDemo,
  onParseQuestions,
  onExportDocx,
  onExportPdf,
  onRefreshReadiness,
  canExportDocx,
  canExportPdf,
}: StepContentProps) {
  switch (stepKey) {
    case 'setup':
      return <ProjectSetupStep metadata={metadata} schoolLogo={schoolLogo} onChange={onMetadataChange} onLogoSelected={onLogoSelected} onLogoRemove={onLogoRemove} />;
    case 'upload':
      return <FileUploadStep uploadedFile={uploadedFile} extractedText={extractedText} onFileSelected={onFileSelected} />;
    case 'extract':
      return <ExtractionStep questions={questions} extractedText={extractedText} onReloadDemo={onReloadDemo} onParseQuestions={onParseQuestions} />;
    case 'glossary':
      return <GlossaryStep glossary={glossary} onUpdateTerm={onUpdateGlossaryTerm} onGenerateGlossary={onGenerateGlossary} />;
    case 'review':
      return (
        <ReviewStep
          questions={questions}
          onUpdateQuestion={onUpdateQuestion}
          onMoveQuestion={onMoveQuestion}
          onTranslateQuestions={onTranslateQuestions}
          onBulkUpdateStatus={onBulkUpdateStatus}
          onUploadQuestionAsset={onUploadQuestionAsset}
          onDeleteQuestionAsset={onDeleteQuestionAsset}
          translationProviderStatus={translationProviderStatus}
        />
      );
    case 'export':
      return (
        <ExportStep
          metadata={metadata}
          questions={questions}
          glossary={glossary}
          readiness={projectReadiness}
          canExportDocx={canExportDocx}
          onExportDocx={onExportDocx}
          onExportPdf={onExportPdf}
          canExportPdf={canExportPdf}
          onRefreshReadiness={onRefreshReadiness}
        />
      );
  }
}
