import { ArrowLeft, ArrowRight, FileText, RefreshCcw } from 'lucide-react';
import { useMemo, useState } from 'react';
import { StepNavigation } from '../components/StepNavigation';
import { steps } from '../constants/steps';
import { defaultMetadata, sampleGlossary, sampleQuestions } from '../data/mockProject';
import { ExtractionStep } from '../features/extraction/ExtractionStep';
import { ExportStep } from '../features/export/ExportStep';
import { FileUploadStep } from '../features/file-upload/FileUploadStep';
import { GlossaryStep } from '../features/glossary/GlossaryStep';
import { ProjectSetupStep } from '../features/project-setup/ProjectSetupStep';
import { ReviewStep } from '../features/review/ReviewStep';
import type { GlossaryTerm, ProjectMetadata, QuestionItem, StepKey, UploadedFileInfo } from '../types/project';

function sortQuestions(questions: QuestionItem[]) {
  return [...questions].sort((a, b) => a.orderIndex - b.orderIndex);
}

export function App() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [metadata, setMetadata] = useState<ProjectMetadata>(defaultMetadata);
  const [uploadedFile, setUploadedFile] = useState<UploadedFileInfo | null>(null);
  const [questions, setQuestions] = useState<QuestionItem[]>(sampleQuestions);
  const [glossary, setGlossary] = useState<GlossaryTerm[]>(sampleGlossary);

  const activeStep = steps[activeIndex];
  const progressLabel = useMemo(() => `${activeIndex + 1} من ${steps.length}`, [activeIndex]);

  const approvedCount = questions.filter((question) => question.status === 'approved').length;
  const needsReviewCount = questions.filter((question) => question.status === 'needs_review').length;
  const deletedCount = questions.filter((question) => question.status === 'deleted').length;

  function goNext() {
    setActiveIndex((current) => Math.min(current + 1, steps.length - 1));
  }

  function goPrevious() {
    setActiveIndex((current) => Math.max(current - 1, 0));
  }

  function resetProject() {
    const confirmed = window.confirm('سيتم مسح مشروع العمل الحالي فقط. هل تريد المتابعة؟');
    if (!confirmed) return;

    setActiveIndex(0);
    setMetadata(defaultMetadata);
    setUploadedFile(null);
    setQuestions(sampleQuestions);
    setGlossary(sampleGlossary);
  }

  function updateQuestion(questionId: string, updates: Partial<QuestionItem>) {
    setQuestions((currentQuestions) =>
      currentQuestions.map((question) => (question.id === questionId ? { ...question, ...updates } : question)),
    );
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

      return currentQuestions.map((question) => {
        if (question.id === currentQuestion.id) return { ...question, orderIndex: targetQuestion.orderIndex };
        if (question.id === targetQuestion.id) return { ...question, orderIndex: currentQuestion.orderIndex };
        return question;
      });
    });
  }

  function updateGlossaryTerm(termId: string, updates: Partial<GlossaryTerm>) {
    setGlossary((currentGlossary) => currentGlossary.map((term) => (term.id === termId ? { ...term, ...updates } : term)));
  }

  return (
    <main className="app-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">Phase 1-A Static UI</p>
          <h1>منصة مدارك</h1>
          <p className="hero-text">
            واجهة ثابتة متعددة الخطوات لاختبار تجربة إعداد الورقة، مراجعة المصطلحات، تعديل بطاقات الأسئلة، الحذف، الترتيب، والتهيئة للتصدير.
          </p>
        </div>
        <button className="ghost-button" type="button" onClick={resetProject}>
          <RefreshCcw size={18} />
          مشروع جديد / إعادة البدء
        </button>
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
            <FileText size={34} aria-hidden="true" />
          </div>

          <StepContent
            stepKey={activeStep.key}
            metadata={metadata}
            uploadedFile={uploadedFile}
            questions={questions}
            glossary={glossary}
            onMetadataChange={setMetadata}
            onFileSelected={setUploadedFile}
            onUpdateQuestion={updateQuestion}
            onMoveQuestion={moveQuestion}
            onUpdateGlossaryTerm={updateGlossaryTerm}
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
}: StepContentProps) {
  switch (stepKey) {
    case 'setup':
      return <ProjectSetupStep metadata={metadata} onChange={onMetadataChange} />;
    case 'upload':
      return <FileUploadStep uploadedFile={uploadedFile} onFileSelected={onFileSelected} />;
    case 'extract':
      return <ExtractionStep questions={questions} />;
    case 'glossary':
      return <GlossaryStep glossary={glossary} onUpdateTerm={onUpdateGlossaryTerm} />;
    case 'review':
      return <ReviewStep questions={questions} onUpdateQuestion={onUpdateQuestion} onMoveQuestion={onMoveQuestion} />;
    case 'export':
      return <ExportStep metadata={metadata} questions={questions} glossary={glossary} />;
  }
}
