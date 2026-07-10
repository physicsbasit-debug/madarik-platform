import { ArrowLeft, ArrowRight, DatabaseZap, FileText, RefreshCcw, Wifi, WifiOff } from 'lucide-react';
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
  createProject,
  deleteProject,
  loadDemoContent,
  reorderQuestions,
  setUploadedFileInfo,
  updateGlossaryTerm as updateGlossaryTermOnServer,
  updateProjectMetadata,
  updateProjectStep,
  updateQuestion as updateQuestionOnServer,
} from '../services/api';
import type {
  ApiConnectionStatus,
  GlossaryTerm,
  ProjectMetadata,
  ProjectSession,
  QuestionItem,
  StepKey,
  UploadedFileInfo,
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
    setQuestions: (questions: QuestionItem[]) => void;
    setGlossary: (glossary: GlossaryTerm[]) => void;
  },
) {
  setters.setProjectId(project.id);
  setters.setMetadata(project.metadata);
  setters.setUploadedFile(project.uploadedFile);
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
  const [questions, setQuestions] = useState<QuestionItem[]>(sampleQuestions);
  const [glossary, setGlossary] = useState<GlossaryTerm[]>(sampleGlossary);

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
      setQuestions,
      setGlossary,
    });
  }, []);

  const bootstrapProject = useCallback(async () => {
    setApiStatus('connecting');
    setLastSyncNote('جاري إنشاء جلسة مؤقتة من Backend...');

    try {
      const createdProject = await createProject(defaultMetadata);
      const hydratedProject = await loadDemoContent(createdProject.id);
      applyProject(hydratedProject);
      setApiStatus('connected');
      setLastSyncNote(`تم إنشاء مشروع مؤقت: ${hydratedProject.id.slice(0, 8)}`);
    } catch (error) {
      console.error(error);
      setProjectId(null);
      setMetadata(defaultMetadata);
      setUploadedFile(null);
      setQuestions(sampleQuestions);
      setGlossary(sampleGlossary);
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

  function handleFileSelected(fileInfo: UploadedFileInfo | null) {
    setUploadedFile(fileInfo);

    if (!projectId || apiStatus === 'offline') return;
    setApiStatus('syncing');
    setUploadedFileInfo(projectId, fileInfo)
      .then((project) => {
        applyProject(project);
        setApiStatus('connected');
        setLastSyncNote(fileInfo ? 'تم حفظ معلومات الملف في Backend. لم يُرفع الملف الحقيقي بعد.' : 'تمت إزالة معلومات الملف من الجلسة.');
      })
      .catch((error: unknown) => {
        console.error(error);
        setApiStatus('offline');
        setLastSyncNote('فشلت مزامنة معلومات الملف. بقيت الحالة محليًا.');
      });
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
          <p className="eyebrow">Phase 1-B Backend API Integration</p>
          <h1>منصة مدارك</h1>
          <p className="hero-text">
            واجهة متعددة الخطوات متصلة الآن بجلسة FastAPI مؤقتة. لا يوجد OCR أو ترجمة أو تصدير فعلي بعد، فقط ربط منظم بين الواجهة والخلفية.
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
            uploadedFile={uploadedFile}
            questions={questions}
            glossary={glossary}
            onMetadataChange={handleMetadataChange}
            onFileSelected={handleFileSelected}
            onUpdateQuestion={updateQuestion}
            onMoveQuestion={moveQuestion}
            onUpdateGlossaryTerm={updateGlossaryTerm}
            onReloadDemo={reloadDemoFromBackend}
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
  uploadedFile: UploadedFileInfo | null;
  questions: QuestionItem[];
  glossary: GlossaryTerm[];
  onMetadataChange: (metadata: ProjectMetadata) => void;
  onFileSelected: (fileInfo: UploadedFileInfo | null) => void;
  onUpdateQuestion: (questionId: string, updates: Partial<QuestionItem>) => void;
  onMoveQuestion: (questionId: string, direction: 'up' | 'down') => void;
  onUpdateGlossaryTerm: (termId: string, updates: Partial<GlossaryTerm>) => void;
  onReloadDemo: () => void;
}

function StepContent({
  stepKey,
  metadata,
  uploadedFile,
  questions,
  glossary,
  onMetadataChange,
  onFileSelected,
  onUpdateQuestion,
  onMoveQuestion,
  onUpdateGlossaryTerm,
  onReloadDemo,
}: StepContentProps) {
  switch (stepKey) {
    case 'setup':
      return <ProjectSetupStep metadata={metadata} onChange={onMetadataChange} />;
    case 'upload':
      return <FileUploadStep uploadedFile={uploadedFile} onFileSelected={onFileSelected} />;
    case 'extract':
      return <ExtractionStep questions={questions} onReloadDemo={onReloadDemo} />;
    case 'glossary':
      return <GlossaryStep glossary={glossary} onUpdateTerm={onUpdateGlossaryTerm} />;
    case 'review':
      return <ReviewStep questions={questions} onUpdateQuestion={onUpdateQuestion} onMoveQuestion={onMoveQuestion} />;
    case 'export':
      return <ExportStep metadata={metadata} questions={questions} glossary={glossary} />;
  }
}
