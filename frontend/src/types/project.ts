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

export interface QuestionItem {
  id: string;
  originalNumber: string;
  originalText: string;
  translatedText: string;
  marks: number | null;
  detectedMarks: number | null;
  status: QuestionStatus;
  orderIndex: number;
  attachmentNote?: string | null;
  attachments: QuestionAssetInfo[];
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

export interface ProjectSession {
  id: string;
  createdAt: string;
  updatedAt: string;
  metadata: ProjectMetadata;
  uploadedFile: UploadedFileInfo | null;
  schoolLogo: SchoolLogoInfo | null;
  extractedText: ExtractedTextInfo | null;
  questions: QuestionItem[];
  glossary: GlossaryTerm[];
  currentStep: StepKey;
}

export type ApiConnectionStatus = 'connecting' | 'connected' | 'syncing' | 'offline';

export interface TranslationProviderStatus {
  provider: string;
  configured: boolean;
  model: string;
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
