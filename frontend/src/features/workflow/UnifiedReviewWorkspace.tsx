import { BookOpenCheck, Image, ListChecks, Settings2 } from 'lucide-react';
import type {
  ExtractedTextInfo,
  FullExamIntakeReport,
  FullExamTranslationReport,
  GlossaryTerm,
  PdfLayoutAssetInfo,
  QuestionItem,
  QuestionStatus,
  TranslationBatchSummary,
  TranslationProviderStatus,
  VisualCropRequest,
} from '../../types/project';
import { ExtractionStep } from '../extraction/ExtractionStep';
import { GlossaryStep } from '../glossary/GlossaryStep';
import { ReviewStep } from '../review/ReviewStep';

interface UnifiedReviewWorkspaceProps {
  questions: QuestionItem[];
  glossary: GlossaryTerm[];
  layoutAssets: PdfLayoutAssetInfo[];
  extractedText: ExtractedTextInfo | null;
  translationProviderStatus: TranslationProviderStatus | null;
  translationBatchSummary: TranslationBatchSummary | null;
  fullExamIntakeReport: FullExamIntakeReport | null;
  fullExamTranslationReport: FullExamTranslationReport | null;
  isBusy: boolean;
  onUpdateQuestion: (questionId: string, updates: Partial<QuestionItem>) => void;
  onMoveQuestion: (questionId: string, direction: 'up' | 'down') => void;
  onTranslateQuestions: () => void;
  onRetryQuestionTranslation: (questionId: string) => void;
  onBulkUpdateStatus: (status: QuestionStatus, includeDeleted?: boolean) => void;
  onUploadQuestionAsset: (questionId: string, file: File) => void;
  onDeleteQuestionAsset: (questionId: string, assetId: string) => void;
  onLinkLayoutAsset: (questionId: string, assetId: string) => void;
  onUnlinkLayoutAsset: (questionId: string, assetId: string) => void;
  onCropLayoutAsset: (
    questionId: string,
    assetId: string,
    crop: VisualCropRequest,
  ) => Promise<void>;
  onUpdateGlossaryTerm: (termId: string, updates: Partial<GlossaryTerm>) => void;
  onGenerateGlossary: () => void;
  onApproveAllGlossary: () => void;
  onDeleteLayoutAsset: (assetId: string) => void;
  onReloadDemo: () => void;
  onParseQuestions: () => void;
}

export function UnifiedReviewWorkspace({
  questions,
  glossary,
  layoutAssets,
  extractedText,
  translationProviderStatus,
  translationBatchSummary,
  fullExamIntakeReport,
  fullExamTranslationReport,
  isBusy,
  onUpdateQuestion,
  onMoveQuestion,
  onTranslateQuestions,
  onRetryQuestionTranslation,
  onBulkUpdateStatus,
  onUploadQuestionAsset,
  onDeleteQuestionAsset,
  onLinkLayoutAsset,
  onUnlinkLayoutAsset,
  onCropLayoutAsset,
  onUpdateGlossaryTerm,
  onGenerateGlossary,
  onApproveAllGlossary,
  onDeleteLayoutAsset,
  onReloadDemo,
  onParseQuestions,
}: UnifiedReviewWorkspaceProps) {
  const activeQuestions = questions.filter((question) => question.status !== 'deleted');
  const needsReview = activeQuestions.filter(
    (question) => question.status === 'needs_review',
  ).length;
  const glossaryNeedsReview = glossary.filter(
    (term) => term.status === 'needs_review',
  ).length;

  return (
    <div className="workflow-panel-stack">
      <section className="review-summary-card">
        <div>
          <p className="eyebrow">مراجعة موحدة</p>
          <h3>راجع التنبيهات بدل مراجعة كل شيء من الصفر</h3>
          <p>
            الأسئلة والترجمة واللقطات في شاشة واحدة. أدوات الاستخراج والقاموس
            التفصيلية مطوية أسفل الصفحة لمن يحتاجها فقط.
          </p>
        </div>
        <div className="review-summary-grid">
          <span><ListChecks size={20} /><strong>{activeQuestions.length}</strong> سؤال نشط</span>
          <span><BookOpenCheck size={20} /><strong>{needsReview}</strong> يحتاج مراجعة</span>
          <span><BookOpenCheck size={20} /><strong>{glossaryNeedsReview}</strong> مصطلح غير معتمد</span>
          <span><Image size={20} /><strong>{layoutAssets.length}</strong> لقطة</span>
        </div>
      </section>

      <ReviewStep
        questions={questions}
        layoutAssets={layoutAssets}
        onUpdateQuestion={onUpdateQuestion}
        onMoveQuestion={onMoveQuestion}
        onTranslateQuestions={onTranslateQuestions}
        onRetryQuestionTranslation={onRetryQuestionTranslation}
        onBulkUpdateStatus={onBulkUpdateStatus}
        onUploadQuestionAsset={onUploadQuestionAsset}
        onDeleteQuestionAsset={onDeleteQuestionAsset}
        onLinkLayoutAsset={onLinkLayoutAsset}
        onUnlinkLayoutAsset={onUnlinkLayoutAsset}
        onCropLayoutAsset={onCropLayoutAsset}
        translationProviderStatus={translationProviderStatus}
        translationBatchSummary={translationBatchSummary}
        fullExamIntakeReport={fullExamIntakeReport}
        fullExamTranslationReport={fullExamTranslationReport}
        simplified
        isBusy={isBusy}
      />

      <details className="advanced-tools-card">
        <summary className="advanced-tools-summary">
          <Settings2 size={20} />
          <span>
            <strong>أدوات متقدمة</strong>
            <small>الاستخراج التفصيلي، القاموس، واللقطات الخام</small>
          </span>
        </summary>
        <div className="advanced-tools-content">
          <GlossaryStep
            glossary={glossary}
            onUpdateTerm={onUpdateGlossaryTerm}
            onGenerateGlossary={onGenerateGlossary}
            onApproveAll={onApproveAllGlossary}
            isBusy={isBusy}
          />
          <ExtractionStep
            questions={questions}
            extractedText={extractedText}
            layoutAssets={layoutAssets}
            onDeleteLayoutAsset={onDeleteLayoutAsset}
            onReloadDemo={onReloadDemo}
            onParseQuestions={onParseQuestions}
          />
        </div>
      </details>
    </div>
  );
}
