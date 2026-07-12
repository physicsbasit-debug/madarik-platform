export type StepKey = 'setup' | 'upload' | 'extract' | 'glossary' | 'review' | 'export';

export type QuestionStatus = 'approved' | 'needs_review' | 'deleted';

export type OutputMode = 'arabic' | 'bilingual';

export type ExportFormat = 'docx' | 'pdf';

export interface ProjectMetadata {
  schoolName: string;
  directorate: string;
  subject: string;
  grade: string;
  semester: string;
  paperTitle: string;
  duration: string;
  totalMarks: string;
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

export interface ExtractedTextInfo {
  text: string;
  preview: string;
  pageCount: number;
  characterCount: number;
  isTextBased: boolean;
  message: string;
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

export interface QuestionItem {
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
  options?: QuestionOption[];
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
  baseUrlConfigured?: boolean;
  timeoutSeconds?: number;
  maxInputChars?: number;
  temperature?: number;
  supportedProviders?: string[];
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
