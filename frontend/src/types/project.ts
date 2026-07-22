export type StepKey = 'setup' | 'upload' | 'extract' | 'glossary' | 'review' | 'export';

export type InitialExtractionPhase =
  | 'idle'
  | 'uploading'
  | 'reading'
  | 'ocr'
  | 'success'
  | 'error';

export interface InitialExtractionStatus {
  phase: InitialExtractionPhase;
  startedAt: number | null;
  message: string;
  canRetry: boolean;
}

export type QuestionStatus = 'approved' | 'needs_review' | 'deleted';

export type OutputMode = 'arabic' | 'bilingual';

export type ExportFormat = 'docx' | 'pdf';

export type MarksPolicy =
  | 'unresolved'
  | 'use_question_total'
  | 'scale_to_declared';

export interface ProjectMetadata {
  schoolName: string;
  directorate: string;
  subject: string;
  grade: string;
  semester: string;
  paperTitle: string;
  duration: string;
  totalMarks: string;
  marksPolicy?: MarksPolicy;
  teacherName: string;
  date: string;
  outputMode: OutputMode;
  exportFormats: ExportFormat[];
}

export interface UploadedFileInfo {
  name: string;
  size: number;
  type: string;
}

export interface SchoolLogoInfo {
  name: string;
  size: number;
  type: string;
  dataBase64: string;
}


export interface VisualCropRequest {
  x: number;
  y: number;
  width: number;
  height: number;
  name?: string | null;
}

export interface PdfLayoutAssetInfo {
  id: string;
  name: string;
  size: number;
  type: string;
  dataBase64: string;
  pageNumber: number;
  source: string;
  note: string;
}

export interface ExtractedPdfPageInfo {
  pageNumber: number;
  text: string;
  characterCount: number;
  isTextEmpty: boolean;
}

export interface ExtractedTextInfo {
  text: string;
  preview: string;
  pageCount: number;
  characterCount: number;
  isTextBased: boolean;
  message: string;
  pages?: ExtractedPdfPageInfo[];
}

export interface QuestionAssetInfo {
  id: string;
  name: string;
  size: number;
  type: string;
  dataBase64: string;
}

export interface QuestionOption {
  label: string;
  text: string;
}

export interface QuestionPart {
  id: string;
  label: string;
  originalText: string;
  translatedText: string;
  marks: number | null;
  parentId?: string | null;
  orderIndex: number;
}

export interface QuestionItem {
  reusedFromQuestionBankItemId?: string | null;
  reusedFromSourceProjectId?: string | null;
  reusedAt?: string | null;
  curriculumGrade?: number | null;
  curriculumScienceDomain?: ScienceDomain | null;
  curriculumSemesterId?: string | null;
  curriculumSubjectId?: string | null;
  curriculumUnitId?: string | null;
  curriculumLessonId?: string | null;
  curriculumLearningOutcomeIds?: string[];
  curriculumLinkSource?: string;
  cognitiveCategory?: CognitiveCategory;
  classificationConfidence?: number;
  classificationReason?: string | null;
  classificationSource?: string;
  id: string;
  originalNumber: string;
  originalText: string;
  rawText?: string | null;
  translatedText: string;
  marks: number | null;
  detectedMarks: number | null;
  status: QuestionStatus;
  orderIndex: number;
  attachmentNote?: string | null;
  attachments: QuestionAssetInfo[];
  linkedLayoutAssetIds?: string[];
  options?: QuestionOption[];
  parts?: QuestionPart[];
  sourcePageNumbers?: number[];
  sourcePageStart?: number | null;
  sourcePageEnd?: number | null;
  reviewNotes?: string | null;
}

export interface GlossaryTerm {
  id: string;
  englishTerm: string;
  arabicTerm: string;
  subject: string;
  status: 'approved' | 'needs_review';
  source: 'mock' | 'manual' | 'detected';
  notes?: string | null;
}

export interface AnswerKeyItem {
  id: string;
  questionId: string;
  questionNumber: string;
  draftAnswer: string;
  marks: number | null;
  confidence: string;
  source: string;
  needsReview: boolean;
  notes: string;
}

export interface EducationalAnalysisReport {
  id: string;
  questionCount: number;
  totalMarks: number;
  averageMarks: number;
  translatedQuestionCount: number;
  answerKeyItemsCount: number;
  layoutAssetsCount: number;
  commandDistribution: Record<string, number>;
  marksDistribution: Record<string, number>;
  reviewLoad: string;
  educationalSummary: string;
  recommendations: string[];
  warnings: string[];
  needsReview: boolean;
}

export interface QualityParetoItem {
  label: string;
  count: number;
  cumulativePercent: number;
}

export interface EducationalQualityToolsReport {
  id: string;
  paretoItems: QualityParetoItem[];
  radarAxes: Record<string, number>;
  fishboneCauses: Record<string, string[]>;
  qualitySummary: string;
  priorityActions: string[];
  warnings: string[];
  needsReview: boolean;
}


export type FullExamIntakeStatus =
  | 'accepted'
  | 'needs_review'
  | 'rejected';

export type PdfPageKind = 'cover' | 'question' | 'blank' | 'other';

export interface FullExamPageSummary {
  pageNumber: number;
  kind: PdfPageKind;
  characterCount: number;
  questionNumbers: string[];
  visualReferenceCount: number;
}

export interface FullExamQuestionSpan {
  questionNumber: string;
  pageNumbers: number[];
  pageStart: number;
  pageEnd: number;
  detectedTotalMarks: number | null;
  visualReferenceCount: number;
  linkedLayoutAssetCount: number;
}

export interface FullExamIntakeCheck {
  code: string;
  passed: boolean;
  message: string;
}

export interface FullExamIntakeReport {
  status: FullExamIntakeStatus;
  pageCount: number;
  contentPageCount: number;
  blankPageCount: number;
  coverPageCount: number;
  questionPageCount: number;
  detectedQuestionCount: number;
  detectedQuestionNumbers: string[];
  reportedTotalMarks: number | null;
  detectedTotalMarks: number | null;
  multiPageQuestionCount: number;
  visualReferenceCount: number;
  autoLinkedLayoutAssetCount: number;
  pages: FullExamPageSummary[];
  questionSpans: FullExamQuestionSpan[];
  checks: FullExamIntakeCheck[];
  warnings: string[];
}




export type FullExamTranslationAcceptanceStatus =
  | 'accepted'
  | 'needs_review'
  | 'incomplete'
  | 'failed';

export type FullExamTranslationQuestionStatus =
  | 'accepted'
  | 'needs_review'
  | 'untranslated'
  | 'failed'
  | 'deleted';

export interface FullExamTranslationQuestionSummary {
  questionId: string;
  questionNumber: string;
  status: FullExamTranslationQuestionStatus;
  totalItems: number;
  translatedItems: number;
  urgentReviewItems: number;
  failedItems: number;
  glossaryViolationCount: number;
  fidelityViolationCount: number;
  languageQualityViolationCount: number;
  sourcePageNumbers: number[];
  linkedLayoutAssetCount: number;
  message: string;
}

export interface FullExamTranslationCheck {
  code: string;
  passed: boolean;
  message: string;
}

export interface FullExamTranslationReport {
  status: FullExamTranslationAcceptanceStatus;
  totalQuestions: number;
  activeQuestions: number;
  deletedQuestions: number;
  translatedQuestions: number;
  acceptedQuestions: number;
  needsReviewQuestions: number;
  untranslatedQuestions: number;
  failedQuestions: number;
  completionPercent: number;
  totalItems: number;
  translatedItems: number;
  urgentReviewItems: number;
  glossaryViolationCount: number;
  fidelityViolationCount: number;
  languageQualityViolationCount: number;
  sourcePageLinkedQuestions: number;
  multiPageQuestions: number;
  questions: FullExamTranslationQuestionSummary[];
  checks: FullExamTranslationCheck[];
  warnings: string[];
}


export type FullExamExportAcceptanceStatus =
  | 'accepted'
  | 'needs_review'
  | 'incomplete'
  | 'failed';

export type FullExamExportArtifactStatus =
  | 'accepted'
  | 'needs_review'
  | 'failed';

export interface FullExamExportCheck {
  code: string;
  passed: boolean;
  message: string;
}

export interface FullExamExportFormatSummary {
  format: ExportFormat;
  status: FullExamExportArtifactStatus;
  byteSize: number;
  pageCount: number | null;
  exportedQuestionCount: number;
  exportedPartCount: number;
  exportedAttachmentCount: number;
  detectedTotalMarks: number;
  questionOrder: string[];
  checks: FullExamExportCheck[];
  warnings: string[];
}

export interface FullExamExportReport {
  status: FullExamExportAcceptanceStatus;
  requestedFormats: ExportFormat[];
  generatedFormats: ExportFormat[];
  acceptedFormats: ExportFormat[];
  needsReviewFormats: ExportFormat[];
  failedFormats: ExportFormat[];
  activeQuestionCount: number;
  expectedTotalMarks: number;
  expectedPartCount: number;
  expectedAttachmentCount: number;
  sourcePageLinkedQuestions: number;
  multiPageQuestions: number;
  formats: FullExamExportFormatSummary[];
  checks: FullExamExportCheck[];
  warnings: string[];
}


export type FullExamEndToEndAcceptanceStatus =
  | 'accepted'
  | 'needs_review'
  | 'rejected';

export type FullExamEndToEndStageStatus =
  | 'accepted'
  | 'needs_review'
  | 'pending'
  | 'failed'
  | 'skipped';

export type FullExamEndToEndStageKey =
  | 'intake'
  | 'layout_assets'
  | 'glossary'
  | 'translation'
  | 'readiness'
  | 'docx_export'
  | 'pdf_export'
  | 'final_consistency';

export interface FullExamEndToEndCheck {
  code: string;
  passed: boolean;
  message: string;
}

export interface FullExamEndToEndStageSummary {
  stage: FullExamEndToEndStageKey;
  status: FullExamEndToEndStageStatus;
  durationMs: number;
  message: string;
  checks: FullExamEndToEndCheck[];
  warnings: string[];
  errors: string[];
}

export interface FullExamEndToEndReport {
  status: FullExamEndToEndAcceptanceStatus;
  runId: string;
  generatedAt: string;
  totalDurationMs: number;
  pageCount: number;
  activeQuestionCount: number;
  totalMarks: number;
  translationCompletionPercent: number;
  requestedFormats: ExportFormat[];
  generatedFormats: ExportFormat[];
  acceptedFormats: ExportFormat[];
  stages: FullExamEndToEndStageSummary[];
  checks: FullExamEndToEndCheck[];
  warnings: string[];
  errors: string[];
}


export type TranslationOutcomeStatus =
  | 'external_success'
  | 'corrected_success'
  | 'local_fallback'
  | 'skipped'
  | 'failed_safely';

export type TranslationItemType = 'question' | 'part';

export type TranslationBatchStatus =
  | 'completed'
  | 'completed_with_fallbacks'
  | 'completed_with_failures';

export interface TranslationItemOutcome {
  questionId: string;
  questionNumber: string;
  itemType: TranslationItemType;
  partId: string | null;
  partLabel: string | null;
  status: TranslationOutcomeStatus;
  provider: string;
  usedExternalProvider: boolean;
  urgentReview: boolean;
  message: string;
}

export interface TranslationBatchSummary {
  status: TranslationBatchStatus;
  totalQuestions: number;
  activeQuestions: number;
  deletedQuestions: number;
  totalItems: number;
  externalSuccessCount: number;
  correctedSuccessCount: number;
  localFallbackCount: number;
  skippedCount: number;
  failedSafelyCount: number;
  urgentReviewCount: number;
  items: TranslationItemOutcome[];
}

export interface ProjectSession {
  id: string;
  ownerAccountId: string | null;
  createdAt: string;
  updatedAt: string;
  metadata: ProjectMetadata;
  uploadedFile: UploadedFileInfo | null;
  schoolLogo: SchoolLogoInfo | null;
  extractedText: ExtractedTextInfo | null;
  questions: QuestionItem[];
  glossary: GlossaryTerm[];
  layoutAssets: PdfLayoutAssetInfo[];
  answerKey: AnswerKeyItem[];
  educationalAnalysis: EducationalAnalysisReport | null;
  qualityTools: EducationalQualityToolsReport | null;
  translationBatchSummary?: TranslationBatchSummary | null;
  fullExamIntakeReport?: FullExamIntakeReport | null;
  fullExamTranslationReport?: FullExamTranslationReport | null;
  fullExamExportReport?: FullExamExportReport | null;
  fullExamEndToEndReport?: FullExamEndToEndReport | null;
  currentStep: StepKey;
}

export type ApiConnectionStatus = 'connecting' | 'connected' | 'syncing' | 'offline';

export interface TranslationProviderStatus {
  provider: string;
  configured: boolean;
  externalEnabled?: boolean;
  ready?: boolean;
  reason?: string;
  model: string;
  apiMode?: string;
  baseUrlConfigured?: boolean;
  timeoutSeconds?: number;
  maxInputChars?: number;
  maxOutputTokens?: number;
  temperature?: number;
  supportedProviders?: string[];
  storesResponses?: boolean;
  providerStorageControl?: string;
  acceptanceGuard?: string;
  fallbackCanBeAccepted?: boolean;
  fallback: string;
}


export type ReadinessSeverity = 'error' | 'warning';

export interface ProjectReadinessIssue {
  code: string;
  severity: ReadinessSeverity;
  message: string;
}

export interface ProjectReadinessReport {
  ready: boolean;
  exportableQuestionCount: number;
  translatedQuestionCount: number;
  deletedQuestionCount: number;
  totalMarks: number;
  issues: ProjectReadinessIssue[];
}


export type AccountRole = 'owner' | 'teacher' | 'reviewer';

export interface AuthAccountPublic {
  id: string;
  username: string;
  displayName: string;
  role: AccountRole;
  isActive: boolean;
  createdAt: string;
  lastLoginAt: string | null;
}

export interface AuthStatus {
  accountsExist: boolean;
  requiresBootstrap: boolean;
}

export interface AuthSessionInfo {
  token: string;
  account: AuthAccountPublic;
}


export interface AuthCreateAccountInput {
  username: string;
  displayName: string;
  password: string;
  role: AccountRole;
  isActive: boolean;
}

export interface AuthUpdateAccountInput {
  displayName?: string;
  role?: AccountRole;
  isActive?: boolean;
}


export type ScienceDomain =
  | "general_science"
  | "physics"
  | "chemistry"
  | "biology"
  | "environmental_science";

export type CurriculumDocumentType =
  | "student_book"
  | "teacher_guide"
  | "curriculum_document"
  | "learning_outcomes"
  | "assessment_guide"
  | "other";

export type CurriculumSemester = {
  id: string;
  grade: number;
  number: 1 | 2;
  title: string;
};

export type CurriculumSubject = {
  id: string;
  grade: number;
  scienceDomain: ScienceDomain;
  title: string;
  shortTitle: string;
};

export type CurriculumUnit = {
  id: string;
  subjectId: string;
  semesterId: string;
  title: string;
  order: number;
  description?: string;
};

export type CurriculumLesson = {
  id: string;
  unitId: string;
  title: string;
  order: number;
  learningOutcomeIds: string[];
};

export type CurriculumLearningOutcome = {
  id: string;
  grade: number;
  scienceDomain: ScienceDomain;
  unitId: string;
  lessonId: string | null;
  code: string;
  text: string;
};

export type CurriculumCatalog = {
  grades: number[];
  semesters: CurriculumSemester[];
  subjects: CurriculumSubject[];
  units: CurriculumUnit[];
  lessons: CurriculumLesson[];
  learningOutcomes: CurriculumLearningOutcome[];
};


export type GoogleDriveSourceStatus = {
  provider: "google_drive";
  mode: string;
  configured: boolean;
  ready: boolean;
  reason: string;
  folderConfigured: boolean;
  tokenConfigured: boolean;
  supportedMimeTypes: string[];
  readOnly: boolean;
};

export type GoogleDriveSourceFile = {
  id: string;
  provider: "google_drive";
  fileName: string;
  mimeType: string;
  sizeBytes: number | null;
  webUrl: string | null;
  folderId: string | null;
  modifiedAt: string | null;
  checksum: string | null;
  accessScope: "read_only";
};

export type GoogleDriveSourceList = {
  status: GoogleDriveSourceStatus;
  files: GoogleDriveSourceFile[];
};

export type GoogleDriveImportResult = {
  source: GoogleDriveSourceFile;
  downloaded: boolean;
  byteCount: number;
  message: string;
};


export type CurriculumSourceVersion = {
  id: string;
  checksum: string | null;
  sizeBytes: number | null;
  fileName: string;
  mimeType: string;
  sourceModifiedAt: string | null;
  recordedAt: string;
};

export type CurriculumSourceAttachment = {

  id: string;
  provider: string;
  sourceFileId: string;
  fileName: string;
  mimeType: string;
  sizeBytes: number | null;
  checksum: string | null;
  grade: number;
  scienceDomain: string;
  semesterId: string;
  subjectId: string;
  unitId: string | null;
  sourceDocumentType: string;
  importedAt: string;
  sourceModifiedAt: string | null;
  sourceRefreshStatus: "unknown" | "current" | "changed" | "missing" | "unverifiable";
  lastCheckedAt: string | null;
  refreshMessage: string | null;
  versionHistory: CurriculumSourceVersion[];
};

export type AttachCurriculumSourceRequest = {
  sourceFileId: string;
  grade: number;
  scienceDomain: string;
  semesterId: string;
  subjectId: string;
  unitId: string | null;
  sourceDocumentType: string;
};


export type RefreshCurriculumSourcesResult = {
  items: CurriculumSourceAttachment[];
  checkedCount: number;
  changedCount: number;
  missingCount: number;
  unverifiableCount: number;
};


export type CognitiveCategory =
  | "knowledge"
  | "application"
  | "reasoning"
  | "unclassified";


export interface QuestionBankItem {
  id: string;
  sourceProjectId: string;
  sourceQuestionId: string;
  ownerAccountId: string | null;
  contentFingerprint: string;
  questionSnapshot: QuestionItem;
  createdAt: string;
  updatedAt: string;
}

export interface QuestionBankList {
  items: QuestionBankItem[];
  total: number;
}


export interface QuestionBankSearchFilters {
  query?: string;
  grade?: number | null;
  scienceDomain?: ScienceDomain | null;
  unitId?: string | null;
  cognitiveCategory?: CognitiveCategory | null;
}

export interface QuestionBankSearchResult {
  items: QuestionBankItem[];
  total: number;
  filters: QuestionBankSearchFilters;
}


export interface QuestionBankReuseResult {
  targetProjectId: string;
  sourceBankItemId: string;
  reused: boolean;
  question: QuestionItem;
}


export interface AssessmentBlueprint {
  title: string;
  grade: number;
  scienceDomain: ScienceDomain;
  subjectId: string;
  semesterId: string | null;
  unitId: string | null;
  durationMinutes: number;
  totalMarks: number;
  targetQuestionCount: number;
  knowledgePercent: number;
  applicationPercent: number;
  reasoningPercent: number;
}

export interface AssessmentSection {
  id: string;
  title: string;
  instructions: string | null;
  orderIndex: number;
}

export interface AssessmentItemConfiguration {
  bankItemId: string;
  sectionId: string | null;
  orderIndex: number;
  marksOverride: number | null;
}


export interface AssessmentDraft {
  id: string;
  ownerAccountId: string | null;
  sourceProjectId: string | null;
  blueprint: AssessmentBlueprint;
  questionBankItemIds: string[];
  sections: AssessmentSection[];
  itemConfigurations: AssessmentItemConfiguration[];
  status: "draft" | "ready";
  createdAt: string;
  updatedAt: string;
}

export interface AssessmentQuestionSummary {
  sectionId: string | null;
  orderIndex: number;
  sourceMarks: number;
  marksOverride: number | null;
  bankItemId: string;
  questionNumber: string;
  text: string;
  marks: number;
  cognitiveCategory: CognitiveCategory;
  grade: number | null;
  unitId: string | null;
}

export interface AssessmentBalanceSummary {
  selectedQuestionCount: number;
  selectedMarks: number;
  remainingQuestionCount: number;
  remainingMarks: number;
  knowledgeCount: number;
  applicationCount: number;
  reasoningCount: number;
  unclassifiedCount: number;
  knowledgePercent: number;
  applicationPercent: number;
  reasoningPercent: number;
  questionTargetMet: boolean;
  marksTargetMet: boolean;
  cognitiveTargetsValid: boolean;
}

export interface AssessmentDraftDetail {
  draft: AssessmentDraft;
  questions: AssessmentQuestionSummary[];
  balance: AssessmentBalanceSummary;
}


export interface AssessmentBlueprintValidation {
  ready: boolean;
  totalSelectedQuestions: number;
  targetQuestions: number;
  totalSelectedMarks: number;
  targetMarks: number;
  knowledgeSelected: number;
  knowledgeTarget: number;
  applicationSelected: number;
  applicationTarget: number;
  reasoningSelected: number;
  reasoningTarget: number;
  unclassifiedSelected: number;
  issues: string[];
}

export interface AssessmentAutoSelectionResult {
  detail: AssessmentDraftDetail;
  validation: AssessmentBlueprintValidation;
  selectedItemIds: string[];
  skippedItemIds: string[];
  shortages: string[];
}


export interface AssessmentStudentPaperQuestion {
  bankItemId: string;
  number: number;
  questionNumber: string;
  text: string;
  marks: number;
  sectionId: string | null;
  sectionTitle: string | null;
}

export interface AssessmentStudentPaperSection {
  id: string;
  title: string;
  instructions: string | null;
  orderIndex: number;
  questions: AssessmentStudentPaperQuestion[];
}

export interface AssessmentStudentPaperPreview {
  draftId: string;
  title: string;
  grade: number;
  scienceDomain: string | null;
  subjectId: string | null;
  durationMinutes: number;
  totalMarks: number;
  questionCount: number;
  sections: AssessmentStudentPaperSection[];
  exportReady: boolean;
  issues: string[];
}

export interface AssessmentExportResult {
  draftId: string;
  format: "docx" | "pdf";
  filename: string;
  path: string;
  exportReady: boolean;
  issues: string[];
}


export type DifferentiationLevel = "support" | "core" | "extension";
export interface DifferentiatedActivity {
  id: string; ownerAccountId: string | null; sourceProjectId: string | null;
  title: string; grade: number; scienceDomain: ScienceDomain; subjectId: string;
  unitId: string | null; lessonId: string | null; learningOutcomeIds: string[];
  level: DifferentiationLevel; objective: string; instructions: string;
  successCriteria: string[]; estimatedMinutes: number; materials: string[];
  createdAt: string; updatedAt: string;
}
export interface DifferentiatedActivityCreateInput {
  sourceProjectId?: string | null; title: string; grade: number; scienceDomain: ScienceDomain;
  subjectId: string; level: DifferentiationLevel; objective: string; instructions: string;
  estimatedMinutes: number;
}


export interface DifferentiatedActivityGenerationInput {
  sourceProjectId?: string | null;
  sourceQuestionBankItemId?: string | null;
  title: string;
  grade: number;
  scienceDomain: ScienceDomain;
  subjectId: string;
  objective: string;
  coreTask: string;
  estimatedMinutes: number;
  materials?: string[];
}

export interface DifferentiatedActivityGenerationResult {
  items: DifferentiatedActivity[];
  total: number;
  sourceQuestionBankItemId: string | null;
}
