import type {
  ExtractedTextInfo,
  FullExamEndToEndReport,
  FullExamExportReport,
  FullExamIntakeReport,
  FullExamTranslationReport,
  GlossaryTerm,
  ProjectMetadata,
  ProjectReadinessReport,
  ProjectSession,
  PdfLayoutAssetInfo,
  SchoolLogoInfo,
  QuestionItem,
  QuestionBankItem,
  QuestionBankList,
  QuestionBankSearchFilters,
  QuestionBankSearchResult,
  QuestionBankReuseResult,
  AssessmentBlueprint,
  AssessmentDraft,
  AssessmentDraftDetail,
  AssessmentAutoSelectionResult,
  AssessmentBlueprintValidation,
  CognitiveCategory,
  QuestionAssetInfo,
  QuestionPart,
  QuestionStatus,
  StepKey,
  UploadedFileInfo,
  TranslationProviderStatus,
  TranslationBatchSummary,
  AnswerKeyItem,
  EducationalAnalysisReport,
  EducationalQualityToolsReport,
  AuthAccountPublic,
  AuthCreateAccountInput,
  AuthSessionInfo,
  AuthStatus,
  AuthUpdateAccountInput,
  VisualCropRequest,
  GoogleDriveSourceStatus,
  GoogleDriveSourceFile,
  GoogleDriveSourceList,
  GoogleDriveImportResult,
  CurriculumSourceAttachment,
  AttachCurriculumSourceRequest,
  RefreshCurriculumSourcesResult,
} from '../types/project';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';
const AUTH_TOKEN_STORAGE_KEY = 'madarik-auth-token';

function getStoredAuthToken(): string | null {
  return window.localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
}

function buildAuthHeaders(): HeadersInit {
  const token = getStoredAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}


interface ApiAuthAccountPublic {
  id: string;
  username: string;
  display_name: string;
  role: 'owner' | 'teacher' | 'reviewer';
  is_active: boolean;
  created_at: string;
  last_login_at: string | null;
}

interface ApiAuthStatus {
  accounts_exist: boolean;
  requires_bootstrap: boolean;
}

interface ApiAuthSessionInfo {
  token: string;
  account: ApiAuthAccountPublic;
}

function fromApiAuthAccount(account: ApiAuthAccountPublic): AuthAccountPublic {
  return {
    id: account.id,
    username: account.username,
    displayName: account.display_name,
    role: account.role,
    isActive: account.is_active,
    createdAt: account.created_at,
    lastLoginAt: account.last_login_at,
  };
}

function fromApiAuthStatus(status: ApiAuthStatus): AuthStatus {
  return {
    accountsExist: status.accounts_exist,
    requiresBootstrap: status.requires_bootstrap,
  };
}

function fromApiAuthSession(session: ApiAuthSessionInfo): AuthSessionInfo {
  return {
    token: session.token,
    account: fromApiAuthAccount(session.account),
  };
}


interface ApiTranslationProviderStatus {
  provider: string;
  configured: boolean;
  external_enabled?: boolean;
  ready?: boolean;
  reason?: string;
  model: string;
  api_mode?: string;
  base_url_configured?: boolean;
  timeout_seconds?: number;
  max_input_chars?: number;
  max_output_tokens?: number;
  temperature?: number;
  supported_providers?: string[];
  stores_responses?: boolean;
  provider_storage_control?: string;
  acceptance_guard?: string;
  fallback_can_be_accepted?: boolean;
  fallback: string;
}

function fromApiTranslationProviderStatus(status: ApiTranslationProviderStatus): TranslationProviderStatus {
  return {
    provider: status.provider,
    configured: status.configured,
    externalEnabled: status.external_enabled,
    ready: status.ready,
    reason: status.reason,
    model: status.model,
    apiMode: status.api_mode,
    baseUrlConfigured: status.base_url_configured,
    timeoutSeconds: status.timeout_seconds,
    maxInputChars: status.max_input_chars,
    maxOutputTokens: status.max_output_tokens,
    temperature: status.temperature,
    supportedProviders: status.supported_providers,
    storesResponses: status.stores_responses,
    providerStorageControl: status.provider_storage_control,
    acceptanceGuard: status.acceptance_guard,
    fallbackCanBeAccepted: status.fallback_can_be_accepted,
    fallback: status.fallback,
  };
}

interface ApiProjectMetadata {
  school_name: string;
  directorate: string;
  subject: string;
  grade: string;
  semester: string;
  paper_title: string;
  duration: string;
  total_marks: string;
  marks_policy?: ProjectMetadata['marksPolicy'];
  teacher_name: string;
  date: string;
  output_mode: ProjectMetadata['outputMode'];
  export_formats: ProjectMetadata['exportFormats'];
}

interface ApiUploadedFileInfo {
  name: string;
  size: number;
  type: string;
}

interface ApiSchoolLogoInfo {
  name: string;
  size: number;
  type: string;
  data_base64: string;
}

interface ApiPdfLayoutAssetInfo {
  id: string;
  name: string;
  size: number;
  type: string;
  data_base64: string;
  page_number: number;
  source: string;
  note: string;
}

interface ApiExtractedPdfPageInfo {
  page_number: number;
  text: string;
  character_count: number;
  is_text_empty: boolean;
}

interface ApiExtractedTextInfo {
  text: string;
  preview: string;
  page_count: number;
  character_count: number;
  is_text_based: boolean;
  message: string;
  pages?: ApiExtractedPdfPageInfo[];
}

interface ApiQuestionAssetInfo {
  id: string;
  name: string;
  size: number;
  type: string;
  data_base64: string;
}

interface ApiQuestionOption {
  label: string;
  text: string;
}

interface ApiQuestionPart {
  id: string;
  label: string;
  original_text: string;
  translated_text: string;
  marks: number | null;
  parent_id?: string | null;
  order_index: number;
}

interface ApiQuestionItem {
  reused_from_question_bank_item_id?: string | null;
  reused_from_source_project_id?: string | null;
  reused_at?: string | null;
  curriculum_grade?: number | null;
  curriculum_science_domain?: 'general_science' | 'physics' | 'chemistry' | 'biology' | 'environmental_science' | null;
  curriculum_semester_id?: string | null;
  curriculum_subject_id?: string | null;
  curriculum_unit_id?: string | null;
  curriculum_lesson_id?: string | null;
  curriculum_learning_outcome_ids?: string[];
  curriculum_link_source?: string;
  cognitive_category?: CognitiveCategory;
  classification_confidence?: number;
  classification_reason?: string | null;
  classification_source?: string;
  id: string;
  original_number: string;
  original_text: string;
  raw_text?: string | null;
  translated_text: string;
  marks: number | null;
  detected_marks: number | null;
  status: QuestionStatus;
  order_index: number;
  attachment_note?: string | null;
  attachments: ApiQuestionAssetInfo[];
  linked_layout_asset_ids?: string[];
  options?: ApiQuestionOption[];
  parts?: ApiQuestionPart[];
  source_page_numbers?: number[];
  source_page_start?: number | null;
  source_page_end?: number | null;
  review_notes?: string | null;
}

interface ApiGlossaryTerm {
  id: string;
  english_term: string;
  arabic_term: string;
  subject: string;
  status: GlossaryTerm['status'];
  source: GlossaryTerm['source'];
  notes?: string | null;
}


interface ApiAnswerKeyItem {
  id: string;
  question_id: string;
  question_number: string;
  draft_answer: string;
  marks: number | null;
  confidence: string;
  source: string;
  needs_review: boolean;
  notes: string;
}

interface ApiEducationalAnalysisReport {
  id: string;
  question_count: number;
  total_marks: number;
  average_marks: number;
  translated_question_count: number;
  answer_key_items_count: number;
  layout_assets_count: number;
  command_distribution: Record<string, number>;
  marks_distribution: Record<string, number>;
  review_load: string;
  educational_summary: string;
  recommendations: string[];
  warnings: string[];
  needs_review: boolean;
}

interface ApiQualityParetoItem {
  label: string;
  count: number;
  cumulative_percent: number;
}

interface ApiEducationalQualityToolsReport {
  id: string;
  pareto_items: ApiQualityParetoItem[];
  radar_axes: Record<string, number>;
  fishbone_causes: Record<string, string[]>;
  quality_summary: string;
  priority_actions: string[];
  warnings: string[];
  needs_review: boolean;
}

interface ApiProjectReadinessIssue {
  code: string;
  severity: 'error' | 'warning';
  message: string;
}

interface ApiProjectReadinessReport {
  ready: boolean;
  exportable_question_count: number;
  translated_question_count: number;
  deleted_question_count: number;
  total_marks: number;
  issues: ApiProjectReadinessIssue[];
}

interface ApiFullExamPageSummary {
  page_number: number;
  kind: 'cover' | 'question' | 'blank' | 'other';
  character_count: number;
  question_numbers: string[];
  visual_reference_count: number;
}

interface ApiFullExamQuestionSpan {
  question_number: string;
  page_numbers: number[];
  page_start: number;
  page_end: number;
  detected_total_marks: number | null;
  visual_reference_count: number;
  linked_layout_asset_count: number;
}

interface ApiFullExamIntakeCheck {
  code: string;
  passed: boolean;
  message: string;
}

interface ApiFullExamIntakeReport {
  status: 'accepted' | 'needs_review' | 'rejected';
  page_count: number;
  content_page_count: number;
  blank_page_count: number;
  cover_page_count: number;
  question_page_count: number;
  detected_question_count: number;
  detected_question_numbers: string[];
  reported_total_marks: number | null;
  detected_total_marks: number | null;
  multi_page_question_count: number;
  visual_reference_count: number;
  auto_linked_layout_asset_count: number;
  pages: ApiFullExamPageSummary[];
  question_spans: ApiFullExamQuestionSpan[];
  checks: ApiFullExamIntakeCheck[];
  warnings: string[];
}


interface ApiFullExamTranslationQuestionSummary {
  question_id: string;
  question_number: string;
  status:
    | 'accepted'
    | 'needs_review'
    | 'untranslated'
    | 'failed'
    | 'deleted';
  total_items: number;
  translated_items: number;
  urgent_review_items: number;
  failed_items: number;
  glossary_violation_count: number;
  fidelity_violation_count: number;
  language_quality_violation_count: number;
  source_page_numbers: number[];
  linked_layout_asset_count: number;
  message: string;
}

interface ApiFullExamTranslationCheck {
  code: string;
  passed: boolean;
  message: string;
}

interface ApiFullExamTranslationReport {
  status: 'accepted' | 'needs_review' | 'incomplete' | 'failed';
  total_questions: number;
  active_questions: number;
  deleted_questions: number;
  translated_questions: number;
  accepted_questions: number;
  needs_review_questions: number;
  untranslated_questions: number;
  failed_questions: number;
  completion_percent: number;
  total_items: number;
  translated_items: number;
  urgent_review_items: number;
  glossary_violation_count: number;
  fidelity_violation_count: number;
  language_quality_violation_count: number;
  source_page_linked_questions: number;
  multi_page_questions: number;
  questions: ApiFullExamTranslationQuestionSummary[];
  checks: ApiFullExamTranslationCheck[];
  warnings: string[];
}


interface ApiFullExamExportCheck {
  code: string;
  passed: boolean;
  message: string;
}

interface ApiFullExamExportFormatSummary {
  format: 'docx' | 'pdf';
  status: 'accepted' | 'needs_review' | 'failed';
  byte_size: number;
  page_count: number | null;
  exported_question_count: number;
  exported_part_count: number;
  exported_attachment_count: number;
  detected_total_marks: number;
  question_order: string[];
  checks: ApiFullExamExportCheck[];
  warnings: string[];
}

interface ApiFullExamExportReport {
  status: 'accepted' | 'needs_review' | 'incomplete' | 'failed';
  requested_formats: Array<'docx' | 'pdf'>;
  generated_formats: Array<'docx' | 'pdf'>;
  accepted_formats: Array<'docx' | 'pdf'>;
  needs_review_formats: Array<'docx' | 'pdf'>;
  failed_formats: Array<'docx' | 'pdf'>;
  active_question_count: number;
  expected_total_marks: number;
  expected_part_count: number;
  expected_attachment_count: number;
  source_page_linked_questions: number;
  multi_page_questions: number;
  formats: ApiFullExamExportFormatSummary[];
  checks: ApiFullExamExportCheck[];
  warnings: string[];
}


interface ApiFullExamEndToEndCheck {
  code: string;
  passed: boolean;
  message: string;
}

interface ApiFullExamEndToEndStageSummary {
  stage:
    | 'intake'
    | 'layout_assets'
    | 'glossary'
    | 'translation'
    | 'readiness'
    | 'docx_export'
    | 'pdf_export'
    | 'final_consistency';
  status:
    | 'accepted'
    | 'needs_review'
    | 'pending'
    | 'failed'
    | 'skipped';
  duration_ms: number;
  message: string;
  checks: ApiFullExamEndToEndCheck[];
  warnings: string[];
  errors: string[];
}

interface ApiFullExamEndToEndReport {
  status: 'accepted' | 'needs_review' | 'rejected';
  run_id: string;
  generated_at: string;
  total_duration_ms: number;
  page_count: number;
  active_question_count: number;
  total_marks: number;
  translation_completion_percent: number;
  requested_formats: Array<'docx' | 'pdf'>;
  generated_formats: Array<'docx' | 'pdf'>;
  accepted_formats: Array<'docx' | 'pdf'>;
  stages: ApiFullExamEndToEndStageSummary[];
  checks: ApiFullExamEndToEndCheck[];
  warnings: string[];
  errors: string[];
}


interface ApiTranslationItemOutcome {
  question_id: string;
  question_number: string;
  item_type: 'question' | 'part';
  part_id?: string | null;
  part_label?: string | null;
  status:
    | 'external_success'
    | 'corrected_success'
    | 'local_fallback'
    | 'skipped'
    | 'failed_safely';
  provider: string;
  used_external_provider: boolean;
  urgent_review: boolean;
  message: string;
}

interface ApiTranslationBatchSummary {
  status:
    | 'completed'
    | 'completed_with_fallbacks'
    | 'completed_with_failures';
  total_questions: number;
  active_questions: number;
  deleted_questions: number;
  total_items: number;
  external_success_count: number;
  corrected_success_count: number;
  local_fallback_count: number;
  skipped_count: number;
  failed_safely_count: number;
  urgent_review_count: number;
  items: ApiTranslationItemOutcome[];
}

interface ApiProjectSession {
  id: string;
  owner_account_id: string | null;
  created_at: string;
  updated_at: string;
  metadata: ApiProjectMetadata;
  uploaded_file: ApiUploadedFileInfo | null;
  school_logo: ApiSchoolLogoInfo | null;
  extracted_text: ApiExtractedTextInfo | null;
  questions: ApiQuestionItem[];
  glossary: ApiGlossaryTerm[];
  layout_assets?: ApiPdfLayoutAssetInfo[];
  answer_key?: ApiAnswerKeyItem[];
  educational_analysis?: ApiEducationalAnalysisReport | null;
  quality_tools?: ApiEducationalQualityToolsReport | null;
  translation_batch_summary?: ApiTranslationBatchSummary | null;
  full_exam_intake_report?: ApiFullExamIntakeReport | null;
  full_exam_translation_report?: ApiFullExamTranslationReport | null;
  full_exam_export_report?: ApiFullExamExportReport | null;
  full_exam_end_to_end_report?: ApiFullExamEndToEndReport | null;
  current_step: StepKey;
}

function toApiMetadata(metadata: ProjectMetadata): ApiProjectMetadata {
  return {
    school_name: metadata.schoolName,
    directorate: metadata.directorate,
    subject: metadata.subject,
    grade: metadata.grade,
    semester: metadata.semester,
    paper_title: metadata.paperTitle,
    duration: metadata.duration,
    total_marks: metadata.totalMarks,
    marks_policy: metadata.marksPolicy ?? 'unresolved',
    teacher_name: metadata.teacherName,
    date: metadata.date,
    output_mode: metadata.outputMode,
    export_formats: metadata.exportFormats,
  };
}

function fromApiMetadata(metadata: ApiProjectMetadata): ProjectMetadata {
  return {
    schoolName: metadata.school_name,
    directorate: metadata.directorate,
    subject: metadata.subject,
    grade: metadata.grade,
    semester: metadata.semester,
    paperTitle: metadata.paper_title,
    duration: metadata.duration,
    totalMarks: metadata.total_marks,
    marksPolicy: metadata.marks_policy ?? 'unresolved',
    teacherName: metadata.teacher_name,
    date: metadata.date,
    outputMode: metadata.output_mode,
    exportFormats: metadata.export_formats,
  };
}

function fromApiExtractedText(info: ApiExtractedTextInfo | null): ExtractedTextInfo | null {
  if (!info) return null;
  return {
    text: info.text,
    preview: info.preview,
    pageCount: info.page_count,
    characterCount: info.character_count,
    isTextBased: info.is_text_based,
    message: info.message,
    pages: (info.pages ?? []).map((page) => ({
      pageNumber: page.page_number,
      text: page.text,
      characterCount: page.character_count,
      isTextEmpty: page.is_text_empty,
    })),
  };
}

function fromApiSchoolLogo(info: ApiSchoolLogoInfo | null): SchoolLogoInfo | null {
  if (!info) return null;
  return {
    name: info.name,
    size: info.size,
    type: info.type,
    dataBase64: info.data_base64,
  };
}


function fromApiQualityTools(report: ApiEducationalQualityToolsReport | null | undefined): EducationalQualityToolsReport | null {
  if (!report) return null;
  return {
    id: report.id,
    paretoItems: report.pareto_items.map((item) => ({
      label: item.label,
      count: item.count,
      cumulativePercent: item.cumulative_percent,
    })),
    radarAxes: report.radar_axes,
    fishboneCauses: report.fishbone_causes,
    qualitySummary: report.quality_summary,
    priorityActions: report.priority_actions,
    warnings: report.warnings,
    needsReview: report.needs_review,
  };
}

function fromApiEducationalAnalysis(analysis: ApiEducationalAnalysisReport | null | undefined): EducationalAnalysisReport | null {
  if (!analysis) return null;
  return {
    id: analysis.id,
    questionCount: analysis.question_count,
    totalMarks: analysis.total_marks,
    averageMarks: analysis.average_marks,
    translatedQuestionCount: analysis.translated_question_count,
    answerKeyItemsCount: analysis.answer_key_items_count,
    layoutAssetsCount: analysis.layout_assets_count,
    commandDistribution: analysis.command_distribution,
    marksDistribution: analysis.marks_distribution,
    reviewLoad: analysis.review_load,
    educationalSummary: analysis.educational_summary,
    recommendations: analysis.recommendations,
    warnings: analysis.warnings,
    needsReview: analysis.needs_review,
  };
}

function fromApiAnswerKeyItem(item: ApiAnswerKeyItem): AnswerKeyItem {
  return {
    id: item.id,
    questionId: item.question_id,
    questionNumber: item.question_number,
    draftAnswer: item.draft_answer,
    marks: item.marks,
    confidence: item.confidence,
    source: item.source,
    needsReview: item.needs_review,
    notes: item.notes,
  };
}

function fromApiPdfLayoutAsset(asset: ApiPdfLayoutAssetInfo): PdfLayoutAssetInfo {
  return {
    id: asset.id,
    name: asset.name,
    size: asset.size,
    type: asset.type,
    dataBase64: asset.data_base64,
    pageNumber: asset.page_number,
    source: asset.source,
    note: asset.note,
  };
}

function fromApiQuestionAsset(asset: ApiQuestionAssetInfo): QuestionAssetInfo {
  return {
    id: asset.id,
    name: asset.name,
    size: asset.size,
    type: asset.type,
    dataBase64: asset.data_base64,
  };
}

function fromApiQuestionOption(option: ApiQuestionOption) {
  return {
    label: option.label,
    text: option.text,
  };
}

function fromApiQuestionPart(part: ApiQuestionPart): QuestionPart {
  return {
    id: part.id,
    label: part.label,
    originalText: part.original_text,
    translatedText: part.translated_text,
    marks: part.marks,
    parentId: part.parent_id ?? null,
    orderIndex: part.order_index,
  };
}

function toApiQuestionPart(part: QuestionPart): ApiQuestionPart {
  return {
    id: part.id,
    label: part.label,
    original_text: part.originalText,
    translated_text: part.translatedText,
    marks: part.marks,
    parent_id: part.parentId ?? null,
    order_index: part.orderIndex,
  };
}

function fromApiQuestion(question: ApiQuestionItem): QuestionItem {
  return {
    id: question.id,
    reusedFromQuestionBankItemId: question.reused_from_question_bank_item_id ?? null,
    reusedFromSourceProjectId: question.reused_from_source_project_id ?? null,
    reusedAt: question.reused_at ?? null,
    curriculumGrade: question.curriculum_grade ?? null,
    curriculumScienceDomain: question.curriculum_science_domain ?? null,
    curriculumSemesterId: question.curriculum_semester_id ?? null,
    curriculumSubjectId: question.curriculum_subject_id ?? null,
    curriculumUnitId: question.curriculum_unit_id ?? null,
    curriculumLessonId: question.curriculum_lesson_id ?? null,
    curriculumLearningOutcomeIds: question.curriculum_learning_outcome_ids ?? [],
    curriculumLinkSource: question.curriculum_link_source ?? 'manual',
    cognitiveCategory: question.cognitive_category ?? 'unclassified',
    classificationConfidence: question.classification_confidence ?? 0,
    classificationReason: question.classification_reason ?? null,
    classificationSource: question.classification_source ?? 'manual',
    originalNumber: question.original_number,
    originalText: question.original_text,
    rawText: question.raw_text,
    translatedText: question.translated_text,
    marks: question.marks,
    detectedMarks: question.detected_marks,
    status: question.status,
    orderIndex: question.order_index,
    attachmentNote: question.attachment_note,
    attachments: (question.attachments ?? []).map(fromApiQuestionAsset),
    linkedLayoutAssetIds: question.linked_layout_asset_ids ?? [],
    options: (question.options ?? []).map(fromApiQuestionOption),
    parts: (question.parts ?? []).map(fromApiQuestionPart),
    sourcePageNumbers: question.source_page_numbers ?? [],
    sourcePageStart: question.source_page_start ?? null,
    sourcePageEnd: question.source_page_end ?? null,
    reviewNotes: question.review_notes,
  };
}

function fromApiGlossaryTerm(term: ApiGlossaryTerm): GlossaryTerm {
  return {
    id: term.id,
    englishTerm: term.english_term,
    arabicTerm: term.arabic_term,
    subject: term.subject,
    status: term.status,
    source: term.source,
    notes: term.notes,
  };
}


function fromApiReadinessReport(report: ApiProjectReadinessReport): ProjectReadinessReport {
  return {
    ready: report.ready,
    exportableQuestionCount: report.exportable_question_count,
    translatedQuestionCount: report.translated_question_count,
    deletedQuestionCount: report.deleted_question_count,
    totalMarks: report.total_marks,
    issues: report.issues,
  };
}

function fromApiFullExamIntakeReport(
  report: ApiFullExamIntakeReport | null | undefined,
): FullExamIntakeReport | null {
  if (!report) return null;

  return {
    status: report.status,
    pageCount: report.page_count,
    contentPageCount: report.content_page_count,
    blankPageCount: report.blank_page_count,
    coverPageCount: report.cover_page_count,
    questionPageCount: report.question_page_count,
    detectedQuestionCount: report.detected_question_count,
    detectedQuestionNumbers: report.detected_question_numbers,
    reportedTotalMarks: report.reported_total_marks,
    detectedTotalMarks: report.detected_total_marks,
    multiPageQuestionCount: report.multi_page_question_count,
    visualReferenceCount: report.visual_reference_count,
    autoLinkedLayoutAssetCount: report.auto_linked_layout_asset_count,
    pages: report.pages.map((page) => ({
      pageNumber: page.page_number,
      kind: page.kind,
      characterCount: page.character_count,
      questionNumbers: page.question_numbers,
      visualReferenceCount: page.visual_reference_count,
    })),
    questionSpans: report.question_spans.map((span) => ({
      questionNumber: span.question_number,
      pageNumbers: span.page_numbers,
      pageStart: span.page_start,
      pageEnd: span.page_end,
      detectedTotalMarks: span.detected_total_marks,
      visualReferenceCount: span.visual_reference_count,
      linkedLayoutAssetCount: span.linked_layout_asset_count,
    })),
    checks: report.checks.map((check) => ({
      code: check.code,
      passed: check.passed,
      message: check.message,
    })),
    warnings: report.warnings,
  };
}


function fromApiFullExamTranslationReport(
  report: ApiFullExamTranslationReport | null | undefined,
): FullExamTranslationReport | null {
  if (!report) return null;

  return {
    status: report.status,
    totalQuestions: report.total_questions,
    activeQuestions: report.active_questions,
    deletedQuestions: report.deleted_questions,
    translatedQuestions: report.translated_questions,
    acceptedQuestions: report.accepted_questions,
    needsReviewQuestions: report.needs_review_questions,
    untranslatedQuestions: report.untranslated_questions,
    failedQuestions: report.failed_questions,
    completionPercent: report.completion_percent,
    totalItems: report.total_items,
    translatedItems: report.translated_items,
    urgentReviewItems: report.urgent_review_items,
    glossaryViolationCount: report.glossary_violation_count,
    fidelityViolationCount: report.fidelity_violation_count,
    languageQualityViolationCount: report.language_quality_violation_count,
    sourcePageLinkedQuestions: report.source_page_linked_questions,
    multiPageQuestions: report.multi_page_questions,
    questions: report.questions.map((question) => ({
      questionId: question.question_id,
      questionNumber: question.question_number,
      status: question.status,
      totalItems: question.total_items,
      translatedItems: question.translated_items,
      urgentReviewItems: question.urgent_review_items,
      failedItems: question.failed_items,
      glossaryViolationCount: question.glossary_violation_count,
      fidelityViolationCount: question.fidelity_violation_count,
      languageQualityViolationCount: question.language_quality_violation_count,
      sourcePageNumbers: question.source_page_numbers,
      linkedLayoutAssetCount: question.linked_layout_asset_count,
      message: question.message,
    })),
    checks: report.checks.map((check) => ({
      code: check.code,
      passed: check.passed,
      message: check.message,
    })),
    warnings: report.warnings,
  };
}


function fromApiFullExamExportReport(
  report: ApiFullExamExportReport | null | undefined,
): FullExamExportReport | null {
  if (!report) return null;

  return {
    status: report.status,
    requestedFormats: report.requested_formats,
    generatedFormats: report.generated_formats,
    acceptedFormats: report.accepted_formats,
    needsReviewFormats: report.needs_review_formats,
    failedFormats: report.failed_formats,
    activeQuestionCount: report.active_question_count,
    expectedTotalMarks: report.expected_total_marks,
    expectedPartCount: report.expected_part_count,
    expectedAttachmentCount: report.expected_attachment_count,
    sourcePageLinkedQuestions: report.source_page_linked_questions,
    multiPageQuestions: report.multi_page_questions,
    formats: report.formats.map((format) => ({
      format: format.format,
      status: format.status,
      byteSize: format.byte_size,
      pageCount: format.page_count,
      exportedQuestionCount: format.exported_question_count,
      exportedPartCount: format.exported_part_count,
      exportedAttachmentCount: format.exported_attachment_count,
      detectedTotalMarks: format.detected_total_marks,
      questionOrder: format.question_order,
      checks: format.checks.map((check) => ({
        code: check.code,
        passed: check.passed,
        message: check.message,
      })),
      warnings: format.warnings,
    })),
    checks: report.checks.map((check) => ({
      code: check.code,
      passed: check.passed,
      message: check.message,
    })),
    warnings: report.warnings,
  };
}


function fromApiFullExamEndToEndReport(
  report: ApiFullExamEndToEndReport | null | undefined,
): FullExamEndToEndReport | null {
  if (!report) return null;

  return {
    status: report.status,
    runId: report.run_id,
    generatedAt: report.generated_at,
    totalDurationMs: report.total_duration_ms,
    pageCount: report.page_count,
    activeQuestionCount: report.active_question_count,
    totalMarks: report.total_marks,
    translationCompletionPercent: report.translation_completion_percent,
    requestedFormats: report.requested_formats,
    generatedFormats: report.generated_formats,
    acceptedFormats: report.accepted_formats,
    stages: report.stages.map((stage) => ({
      stage: stage.stage,
      status: stage.status,
      durationMs: stage.duration_ms,
      message: stage.message,
      checks: stage.checks.map((check) => ({
        code: check.code,
        passed: check.passed,
        message: check.message,
      })),
      warnings: stage.warnings,
      errors: stage.errors,
    })),
    checks: report.checks.map((check) => ({
      code: check.code,
      passed: check.passed,
      message: check.message,
    })),
    warnings: report.warnings,
    errors: report.errors,
  };
}


function fromApiTranslationBatchSummary(
  summary: ApiTranslationBatchSummary | null | undefined,
): TranslationBatchSummary | null {
  if (!summary) return null;

  return {
    status: summary.status,
    totalQuestions: summary.total_questions,
    activeQuestions: summary.active_questions,
    deletedQuestions: summary.deleted_questions,
    totalItems: summary.total_items,
    externalSuccessCount: summary.external_success_count,
    correctedSuccessCount: summary.corrected_success_count,
    localFallbackCount: summary.local_fallback_count,
    skippedCount: summary.skipped_count,
    failedSafelyCount: summary.failed_safely_count,
    urgentReviewCount: summary.urgent_review_count,
    items: summary.items.map((item) => ({
      questionId: item.question_id,
      questionNumber: item.question_number,
      itemType: item.item_type,
      partId: item.part_id ?? null,
      partLabel: item.part_label ?? null,
      status: item.status,
      provider: item.provider,
      usedExternalProvider: item.used_external_provider,
      urgentReview: item.urgent_review,
      message: item.message,
    })),
  };
}

function fromApiProject(project: ApiProjectSession): ProjectSession {
  return {
    id: project.id,
    ownerAccountId: project.owner_account_id,
    createdAt: project.created_at,
    updatedAt: project.updated_at,
    metadata: fromApiMetadata(project.metadata),
    uploadedFile: project.uploaded_file,
    schoolLogo: fromApiSchoolLogo(project.school_logo),
    extractedText: fromApiExtractedText(project.extracted_text),
    questions: project.questions.map(fromApiQuestion),
    glossary: project.glossary.map(fromApiGlossaryTerm),
    layoutAssets: (project.layout_assets ?? []).map(fromApiPdfLayoutAsset),
    answerKey: (project.answer_key ?? []).map(fromApiAnswerKeyItem),
    educationalAnalysis: fromApiEducationalAnalysis(project.educational_analysis),
    qualityTools: fromApiQualityTools(project.quality_tools),
    translationBatchSummary: fromApiTranslationBatchSummary(
      project.translation_batch_summary,
    ),
    fullExamIntakeReport: fromApiFullExamIntakeReport(
      project.full_exam_intake_report,
    ),
    fullExamTranslationReport: fromApiFullExamTranslationReport(
      project.full_exam_translation_report,
    ),
    fullExamExportReport: fromApiFullExamExportReport(
      project.full_exam_export_report,
    ),
    fullExamEndToEndReport: fromApiFullExamEndToEndReport(
      project.full_exam_end_to_end_report,
    ),
    currentStep: project.current_step,
  };
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...buildAuthHeaders(),
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`API request failed ${response.status}: ${body}`);
  }

  return (await response.json()) as T;
}


export async function getAuthStatus(): Promise<AuthStatus> {
  const status = await requestJson<ApiAuthStatus>('/auth/status');
  return fromApiAuthStatus(status);
}

export async function bootstrapOwner(username: string, displayName: string, password: string): Promise<AuthSessionInfo> {
  const session = await requestJson<ApiAuthSessionInfo>('/auth/bootstrap', {
    method: 'POST',
    body: JSON.stringify({ username, display_name: displayName, password }),
  });
  return fromApiAuthSession(session);
}

export async function login(username: string, password: string): Promise<AuthSessionInfo> {
  const session = await requestJson<ApiAuthSessionInfo>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
  return fromApiAuthSession(session);
}

export async function getCurrentAccount(token: string): Promise<AuthAccountPublic> {
  const account = await requestJson<ApiAuthAccountPublic>('/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return fromApiAuthAccount(account);
}

export async function logout(token: string): Promise<void> {
  await requestJson<{ logged_out: boolean }>('/auth/logout', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
}


export async function listAuthAccounts(): Promise<AuthAccountPublic[]> {
  const accounts = await requestJson<ApiAuthAccountPublic[]>('/auth/accounts');
  return accounts.map(fromApiAuthAccount);
}

export async function createAuthAccount(input: AuthCreateAccountInput): Promise<AuthAccountPublic> {
  const account = await requestJson<ApiAuthAccountPublic>('/auth/accounts', {
    method: 'POST',
    body: JSON.stringify({
      username: input.username,
      display_name: input.displayName,
      password: input.password,
      role: input.role,
      is_active: input.isActive,
    }),
  });
  return fromApiAuthAccount(account);
}

export async function updateAuthAccount(accountId: string, input: AuthUpdateAccountInput): Promise<AuthAccountPublic> {
  const account = await requestJson<ApiAuthAccountPublic>(`/auth/accounts/${accountId}`, {
    method: 'PATCH',
    body: JSON.stringify({
      display_name: input.displayName,
      role: input.role,
      is_active: input.isActive,
    }),
  });
  return fromApiAuthAccount(account);
}

export async function getProject(projectId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}`);
  return fromApiProject(project);
}

export async function listProjects(limit = 50): Promise<ProjectSession[]> {
  const projects = await requestJson<ApiProjectSession[]>(`/projects?limit=${encodeURIComponent(String(limit))}`);
  return projects.map(fromApiProject);
}

export async function createProject(metadata: ProjectMetadata): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>('/projects', {
    method: 'POST',
    body: JSON.stringify(toApiMetadata(metadata)),
  });
  return fromApiProject(project);
}

export async function deleteProject(projectId: string): Promise<void> {
  await requestJson<{ deleted: boolean }>(`/projects/${projectId}`, { method: 'DELETE' });
}

export async function updateProjectMetadata(projectId: string, metadata: ProjectMetadata): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/metadata`, {
    method: 'PATCH',
    body: JSON.stringify(toApiMetadata(metadata)),
  });
  return fromApiProject(project);
}

export async function updateProjectStep(projectId: string, currentStep: StepKey): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/step`, {
    method: 'PATCH',
    body: JSON.stringify({ current_step: currentStep }),
  });
  return fromApiProject(project);
}

export async function setUploadedFileInfo(projectId: string, uploadedFile: UploadedFileInfo | null): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/upload-info`, {
    method: 'PUT',
    body: JSON.stringify(uploadedFile),
  });
  return fromApiProject(project);
}

export async function uploadSchoolLogo(projectId: string, file: File): Promise<ProjectSession> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/school-logo`, {
    method: 'POST',
    headers: buildAuthHeaders(),
    body: formData,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`School logo upload failed ${response.status}: ${body}`);
  }

  const project = (await response.json()) as ApiProjectSession;
  return fromApiProject(project);
}

export async function deleteSchoolLogo(projectId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/school-logo`, { method: 'DELETE' });
  return fromApiProject(project);
}

export async function uploadPdfAndExtractText(projectId: string, file: File): Promise<ProjectSession> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/upload-pdf`, {
    method: 'POST',
    headers: buildAuthHeaders(),
    body: formData,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`PDF extraction failed ${response.status}: ${body}`);
  }

  const project = (await response.json()) as ApiProjectSession;
  return fromApiProject(project);
}


export async function uploadPdfOcrAndExtractText(projectId: string, file: File): Promise<ProjectSession> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/upload-pdf-ocr`, {
    method: 'POST',
    headers: buildAuthHeaders(),
    body: formData,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`PDF OCR extraction failed ${response.status}: ${body}`);
  }

  const project = (await response.json()) as ApiProjectSession;
  return fromApiProject(project);
}


export async function uploadImageAndExtractText(projectId: string, file: File): Promise<ProjectSession> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/upload-image-ocr`, {
    method: 'POST',
    headers: buildAuthHeaders(),
    body: formData,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Image OCR failed ${response.status}: ${body}`);
  }

  const project = (await response.json()) as ApiProjectSession;
  return fromApiProject(project);
}


export async function extractPdfLayoutAssets(projectId: string, file: File): Promise<ProjectSession> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/layout-assets/pdf`, {
    method: 'POST',
    body: formData,
    headers: buildAuthHeaders(),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`PDF layout extraction failed ${response.status}: ${body}`);
  }

  const project = (await response.json()) as ApiProjectSession;
  return fromApiProject(project);
}

export async function deletePdfLayoutAsset(projectId: string, assetId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/layout-assets/${assetId}`, {
    method: 'DELETE',
  });
  return fromApiProject(project);
}

export async function linkQuestionLayoutAsset(
  projectId: string,
  questionId: string,
  assetId: string,
): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(
    `/projects/${projectId}/questions/${questionId}/layout-assets/${assetId}`,
    { method: 'POST' },
  );

  return fromApiProject(project);
}

export async function unlinkQuestionLayoutAsset(
  projectId: string,
  questionId: string,
  assetId: string,
): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(
    `/projects/${projectId}/questions/${questionId}/layout-assets/${assetId}`,
    { method: 'DELETE' },
  );

  return fromApiProject(project);
}


export async function cropQuestionLayoutAsset(
  projectId: string,
  questionId: string,
  assetId: string,
  crop: VisualCropRequest,
): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(
    `/projects/${projectId}/questions/${questionId}/layout-assets/${assetId}/crop`,
    {
      method: "POST",
      body: JSON.stringify(crop),
    },
  );

  return fromApiProject(project);
}

export async function parseExtractedQuestions(projectId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/parse-questions`, { method: 'POST' });
  return fromApiProject(project);
}


export async function generateGlossaryFromQuestions(projectId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/glossary/generate`, { method: 'POST' });
  return fromApiProject(project);
}

export async function translateProjectQuestions(projectId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/translate-questions`, { method: 'POST' });
  return fromApiProject(project);
}

export async function retryQuestionTranslation(
  projectId: string,
  questionId: string,
): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(
    `/projects/${projectId}/questions/${questionId}/retry-translation`,
    { method: 'POST' },
  );
  return fromApiProject(project);
}

export async function loadDemoContent(projectId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/demo-content`, { method: 'POST' });
  return fromApiProject(project);
}

export async function updateQuestion(
  projectId: string,
  questionId: string,
  updates: Partial<
    Pick<
      QuestionItem,
      | 'translatedText'
      | 'marks'
      | 'status'
      | 'parts'
      | 'reviewNotes'
      | 'curriculumGrade'
      | 'curriculumScienceDomain'
      | 'curriculumSemesterId'
      | 'curriculumSubjectId'
      | 'curriculumUnitId'
      | 'curriculumLessonId'
      | 'curriculumLearningOutcomeIds'
      | 'curriculumLinkSource'
      | 'cognitiveCategory'
      | 'classificationConfidence'
      | 'classificationReason'
      | 'classificationSource'
    >
  >,
): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/questions/${questionId}`, {
    method: 'PATCH',
    body: JSON.stringify({
      translated_text: updates.translatedText,
      marks: updates.marks,
      status: updates.status,
      parts: updates.parts?.map(toApiQuestionPart),
      review_notes: updates.reviewNotes,
      curriculum_grade: updates.curriculumGrade,
      curriculum_science_domain: updates.curriculumScienceDomain,
      curriculum_semester_id: updates.curriculumSemesterId,
      curriculum_subject_id: updates.curriculumSubjectId,
      curriculum_unit_id: updates.curriculumUnitId,
      curriculum_lesson_id: updates.curriculumLessonId,
      curriculum_learning_outcome_ids: updates.curriculumLearningOutcomeIds,
      curriculum_link_source: updates.curriculumLinkSource,
      cognitive_category: updates.cognitiveCategory,
      classification_confidence: updates.classificationConfidence,
      classification_reason: updates.classificationReason,
      classification_source: updates.classificationSource,
    }),
  });
  return fromApiProject(project);
}

export async function uploadQuestionAsset(projectId: string, questionId: string, file: File): Promise<ProjectSession> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/questions/${questionId}/assets`, {
    method: 'POST',
    headers: buildAuthHeaders(),
    body: formData,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Question asset upload failed ${response.status}: ${body}`);
  }

  const project = (await response.json()) as ApiProjectSession;
  return fromApiProject(project);
}

export async function deleteQuestionAsset(projectId: string, questionId: string, assetId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/questions/${questionId}/assets/${assetId}`, {
    method: 'DELETE',
  });
  return fromApiProject(project);
}


export async function bulkUpdateQuestionStatus(
  projectId: string,
  status: QuestionStatus,
  includeDeleted = false,
): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/questions/bulk-status`, {
    method: 'POST',
    body: JSON.stringify({ status, include_deleted: includeDeleted }),
  });
  return fromApiProject(project);
}

export async function reorderQuestions(projectId: string, orderedQuestionIds: string[]): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/questions/reorder`, {
    method: 'POST',
    body: JSON.stringify({ ordered_question_ids: orderedQuestionIds }),
  });
  return fromApiProject(project);
}

export async function updateGlossaryTerm(
  projectId: string,
  termId: string,
  updates: Partial<Pick<GlossaryTerm, 'arabicTerm' | 'status' | 'notes'>>,
): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/glossary/${termId}`, {
    method: 'PATCH',
    body: JSON.stringify({
      arabic_term: updates.arabicTerm,
      status: updates.status,
      notes: updates.notes,
    }),
  });
  return fromApiProject(project);
}

export async function getFullExamEndToEndAcceptance(
  projectId: string,
): Promise<FullExamEndToEndReport | null> {
  const report = await requestJson<ApiFullExamEndToEndReport | null>(
    `/projects/${projectId}/full-exam/acceptance`,
  );
  return fromApiFullExamEndToEndReport(report);
}

export async function runFullExamEndToEndAcceptance(
  projectId: string,
): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(
    `/projects/${projectId}/full-exam/acceptance/run`,
    { method: 'POST' },
  );
  return fromApiProject(project);
}


export async function getFullExamExportAcceptance(
  projectId: string,
): Promise<FullExamExportReport | null> {
  const report = await requestJson<ApiFullExamExportReport | null>(
    `/projects/${projectId}/export/acceptance`,
  );
  return fromApiFullExamExportReport(report);
}


export async function exportProjectDocx(projectId: string): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/export/docx`, {
    method: 'POST',
    headers: buildAuthHeaders(),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`DOCX export failed ${response.status}: ${body}`);
  }

  return await response.blob();
}


export async function exportProjectPdf(projectId: string): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/export/pdf`, {
    method: 'POST',
    headers: buildAuthHeaders(),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`PDF export failed ${response.status}: ${body}`);
  }

  return await response.blob();
}


export async function getTranslationProviderStatus(): Promise<TranslationProviderStatus> {
  const status = await requestJson<ApiTranslationProviderStatus>('/projects/translation-provider/status');
  return fromApiTranslationProviderStatus(status);
}


export async function generateAnswerKeyDraft(projectId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/answer-key/draft`, {
    method: 'POST',
  });
  return fromApiProject(project);
}

export async function clearAnswerKey(projectId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/answer-key`, {
    method: 'DELETE',
  });
  return fromApiProject(project);
}


export async function generateEducationalAnalysis(projectId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/educational-analysis`, {
    method: 'POST',
  });
  return fromApiProject(project);
}

export async function clearEducationalAnalysis(projectId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/educational-analysis`, {
    method: 'DELETE',
  });
  return fromApiProject(project);
}


export async function generateQualityTools(projectId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/quality-tools`, {
    method: 'POST',
  });
  return fromApiProject(project);
}

export async function clearQualityTools(projectId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/quality-tools`, {
    method: 'DELETE',
  });
  return fromApiProject(project);
}

export async function getProjectReadiness(projectId: string): Promise<ProjectReadinessReport> {
  const report = await requestJson<ApiProjectReadinessReport>(`/projects/${projectId}/readiness`);
  return fromApiReadinessReport(report);
}


export async function exportProjectSnapshot(projectId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/snapshot`);
  return fromApiProject(project);
}

export async function importProjectSnapshot(snapshot: unknown): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>('/projects/import-snapshot', {
    method: 'POST',
    body: JSON.stringify(snapshot),
  });
  return fromApiProject(project);
}


interface ApiGoogleDriveSourceStatus {
  provider: 'google_drive';
  mode: string;
  configured: boolean;
  ready: boolean;
  reason: string;
  folder_configured: boolean;
  token_configured: boolean;
  supported_mime_types: string[];
  read_only: boolean;
}

interface ApiGoogleDriveSourceFile {
  id: string;
  provider: 'google_drive';
  file_name: string;
  mime_type: string;
  size_bytes: number | null;
  web_url: string | null;
  folder_id: string | null;
  modified_at: string | null;
  checksum: string | null;
  access_scope: 'read_only';
}

interface ApiGoogleDriveSourceList {
  status: ApiGoogleDriveSourceStatus;
  files: ApiGoogleDriveSourceFile[];
}

interface ApiGoogleDriveImportResult {
  source: ApiGoogleDriveSourceFile;
  downloaded: boolean;
  byte_count: number;
  message: string;
}

function fromApiGoogleDriveStatus(
  status: ApiGoogleDriveSourceStatus,
): GoogleDriveSourceStatus {
  return {
    provider: status.provider,
    mode: status.mode,
    configured: status.configured,
    ready: status.ready,
    reason: status.reason,
    folderConfigured: status.folder_configured,
    tokenConfigured: status.token_configured,
    supportedMimeTypes: status.supported_mime_types,
    readOnly: status.read_only,
  };
}

function fromApiGoogleDriveFile(
  file: ApiGoogleDriveSourceFile,
): GoogleDriveSourceFile {
  return {
    id: file.id,
    provider: file.provider,
    fileName: file.file_name,
    mimeType: file.mime_type,
    sizeBytes: file.size_bytes,
    webUrl: file.web_url,
    folderId: file.folder_id,
    modifiedAt: file.modified_at,
    checksum: file.checksum,
    accessScope: file.access_scope,
  };
}

export async function getGoogleDriveSourceStatus(): Promise<GoogleDriveSourceStatus> {
  const response = await fetch(
    `${API_BASE_URL}/cloud-sources/google-drive/status`,
    { headers: buildAuthHeaders() },
  );
  if (!response.ok) throw new Error('Failed to read Google Drive status');
  return fromApiGoogleDriveStatus(
    (await response.json()) as ApiGoogleDriveSourceStatus,
  );
}

export async function listGoogleDriveSourceFiles(): Promise<GoogleDriveSourceList> {
  const response = await fetch(
    `${API_BASE_URL}/cloud-sources/google-drive/files`,
    { headers: buildAuthHeaders() },
  );
  if (!response.ok) throw new Error('Failed to list Google Drive files');
  const payload = (await response.json()) as ApiGoogleDriveSourceList;
  return {
    status: fromApiGoogleDriveStatus(payload.status),
    files: payload.files.map(fromApiGoogleDriveFile),
  };
}

export async function importGoogleDriveSourceFile(
  fileId: string,
): Promise<GoogleDriveImportResult> {
  const response = await fetch(
    `${API_BASE_URL}/cloud-sources/google-drive/import`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...buildAuthHeaders(),
      },
      body: JSON.stringify({ file_id: fileId }),
    },
  );
  if (!response.ok) throw new Error('Failed to import Google Drive file');
  const payload = (await response.json()) as ApiGoogleDriveImportResult;
  return {
    source: fromApiGoogleDriveFile(payload.source),
    downloaded: payload.downloaded,
    byteCount: payload.byte_count,
    message: payload.message,
  };
}


interface ApiCurriculumSourceAttachment {
  id: string;
  provider: string;
  source_file_id: string;
  file_name: string;
  mime_type: string;
  size_bytes: number | null;
  checksum: string | null;
  grade: number;
  science_domain: string;
  semester_id: string;
  subject_id: string;
  unit_id: string | null;
  source_document_type: string;
  imported_at: string;
  source_modified_at: string | null;
  source_refresh_status: 'unknown' | 'current' | 'changed' | 'missing' | 'unverifiable';
  last_checked_at: string | null;
  refresh_message: string | null;
  version_history: Array<{
    id: string;
    checksum: string | null;
    size_bytes: number | null;
    file_name: string;
    mime_type: string;
    source_modified_at: string | null;
    recorded_at: string;
  }>;
}

interface ApiCurriculumSourceListResponse {
  items: ApiCurriculumSourceAttachment[];
}

function fromApiCurriculumSource(
  source: ApiCurriculumSourceAttachment,
): CurriculumSourceAttachment {
  return {
    id: source.id,
    provider: source.provider,
    sourceFileId: source.source_file_id,
    fileName: source.file_name,
    mimeType: source.mime_type,
    sizeBytes: source.size_bytes,
    checksum: source.checksum,
    grade: source.grade,
    scienceDomain: source.science_domain,
    semesterId: source.semester_id,
    subjectId: source.subject_id,
    unitId: source.unit_id,
    sourceDocumentType: source.source_document_type,
    importedAt: source.imported_at,
    sourceModifiedAt: source.source_modified_at,
    sourceRefreshStatus: source.source_refresh_status,
    lastCheckedAt: source.last_checked_at,
    refreshMessage: source.refresh_message,
    versionHistory: source.version_history.map((version) => ({
      id: version.id,
      checksum: version.checksum,
      sizeBytes: version.size_bytes,
      fileName: version.file_name,
      mimeType: version.mime_type,
      sourceModifiedAt: version.source_modified_at,
      recordedAt: version.recorded_at,
    })),
  };
}

export async function listProjectCurriculumSources(
  projectId: string,
): Promise<CurriculumSourceAttachment[]> {
  const response = await fetch(
    `${API_BASE_URL}/cloud-sources/projects/${projectId}/curriculum-sources`,
    { headers: buildAuthHeaders() },
  );
  if (!response.ok) {
    throw new Error('Failed to list curriculum sources');
  }
  const payload =
    (await response.json()) as ApiCurriculumSourceListResponse;
  return payload.items.map(fromApiCurriculumSource);
}

export async function attachGoogleDriveCurriculumSource(
  projectId: string,
  request: AttachCurriculumSourceRequest,
): Promise<CurriculumSourceAttachment> {
  const response = await fetch(
    `${API_BASE_URL}/cloud-sources/projects/${projectId}/curriculum-sources/google-drive`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...buildAuthHeaders(),
      },
      body: JSON.stringify({
        source_file_id: request.sourceFileId,
        grade: request.grade,
        science_domain: request.scienceDomain,
        semester_id: request.semesterId,
        subject_id: request.subjectId,
        unit_id: request.unitId,
        source_document_type: request.sourceDocumentType,
      }),
    },
  );
  if (!response.ok) {
    throw new Error('Failed to attach curriculum source');
  }
  return fromApiCurriculumSource(
    (await response.json()) as ApiCurriculumSourceAttachment,
  );
}

export async function deleteProjectCurriculumSource(
  projectId: string,
  attachmentId: string,
): Promise<CurriculumSourceAttachment> {
  const response = await fetch(
    `${API_BASE_URL}/cloud-sources/projects/${projectId}/curriculum-sources/${attachmentId}`,
    {
      method: 'DELETE',
      headers: buildAuthHeaders(),
    },
  );
  if (!response.ok) {
    throw new Error('Failed to delete curriculum source');
  }
  return fromApiCurriculumSource(
    (await response.json()) as ApiCurriculumSourceAttachment,
  );
}


interface ApiRefreshCurriculumSourcesResponse {
  items: ApiCurriculumSourceAttachment[];
  checked_count: number;
  changed_count: number;
  missing_count: number;
  unverifiable_count: number;
}

export async function checkProjectCurriculumSourceUpdates(
  projectId: string,
): Promise<RefreshCurriculumSourcesResult> {
  const response = await fetch(
    `${API_BASE_URL}/cloud-sources/projects/${projectId}/curriculum-sources/check-refresh`,
    {
      method: 'POST',
      headers: buildAuthHeaders(),
    },
  );
  if (!response.ok) {
    throw new Error(
      'Failed to check curriculum source updates',
    );
  }

  const payload =
    (await response.json()) as ApiRefreshCurriculumSourcesResponse;

  return {
    items: payload.items.map(fromApiCurriculumSource),
    checkedCount: payload.checked_count,
    changedCount: payload.changed_count,
    missingCount: payload.missing_count,
    unverifiableCount: payload.unverifiable_count,
  };
}


export async function acceptProjectCurriculumSourceUpdate(
  projectId: string,
  attachmentId: string,
): Promise<CurriculumSourceAttachment> {
  const response = await fetch(
    `${API_BASE_URL}/cloud-sources/projects/${projectId}/curriculum-sources/${attachmentId}/accept-update`,
    {
      method: 'POST',
      headers: buildAuthHeaders(),
    },
  );
  if (!response.ok) {
    throw new Error('Failed to accept curriculum source update');
  }

  return fromApiCurriculumSource(
    (await response.json()) as ApiCurriculumSourceAttachment,
  );
}


interface ApiQuestionBankItem {
  id: string;
  source_project_id: string;
  source_question_id: string;
  owner_account_id: string | null;
  content_fingerprint: string;
  question_snapshot: ApiQuestionItem;
  created_at: string;
  updated_at: string;
}

interface ApiQuestionBankListResponse {
  items: ApiQuestionBankItem[];
  total: number;
}

function fromApiQuestionBankItem(
  item: ApiQuestionBankItem,
): QuestionBankItem {
  return {
    id: item.id,
    sourceProjectId: item.source_project_id,
    sourceQuestionId: item.source_question_id,
    ownerAccountId: item.owner_account_id,
    contentFingerprint: item.content_fingerprint,
    questionSnapshot: fromApiQuestion(
      item.question_snapshot,
    ),
    createdAt: item.created_at,
    updatedAt: item.updated_at,
  };
}

export async function listProjectQuestionBank(
  projectId: string,
): Promise<QuestionBankList> {
  const response = await fetch(
    `${API_BASE_URL}/projects/${projectId}/question-bank`,
    {
      headers: buildAuthHeaders(),
    },
  );
  if (!response.ok) {
    throw new Error('Failed to list question bank');
  }

  const payload =
    (await response.json()) as ApiQuestionBankListResponse;
  return {
    items: payload.items.map(fromApiQuestionBankItem),
    total: payload.total,
  };
}

export async function saveQuestionToBank(
  projectId: string,
  questionId: string,
): Promise<QuestionBankItem> {
  const response = await fetch(
    `${API_BASE_URL}/projects/${projectId}/questions/${questionId}/question-bank`,
    {
      method: 'POST',
      headers: buildAuthHeaders(),
    },
  );
  if (!response.ok) {
    throw new Error('Failed to save question to bank');
  }

  return fromApiQuestionBankItem(
    (await response.json()) as ApiQuestionBankItem,
  );
}

export async function deleteQuestionBankItem(
  projectId: string,
  itemId: string,
): Promise<QuestionBankItem> {
  const response = await fetch(
    `${API_BASE_URL}/projects/${projectId}/question-bank/${itemId}`,
    {
      method: 'DELETE',
      headers: buildAuthHeaders(),
    },
  );
  if (!response.ok) {
    throw new Error('Failed to delete question bank item');
  }

  return fromApiQuestionBankItem(
    (await response.json()) as ApiQuestionBankItem,
  );
}


export async function searchQuestionBankLibrary(
  filters: QuestionBankSearchFilters,
): Promise<QuestionBankSearchResult> {
  const params = new URLSearchParams();

  if (filters.query?.trim()) {
    params.set('query', filters.query.trim());
  }
  if (filters.grade) {
    params.set('grade', String(filters.grade));
  }
  if (filters.scienceDomain) {
    params.set(
      'science_domain',
      filters.scienceDomain,
    );
  }
  if (filters.unitId) {
    params.set('unit_id', filters.unitId);
  }
  if (filters.cognitiveCategory) {
    params.set(
      'cognitive_category',
      filters.cognitiveCategory,
    );
  }

  const response = await fetch(
    `${API_BASE_URL}/projects/question-bank/library?${params.toString()}`,
    {
      headers: buildAuthHeaders(),
    },
  );
  if (!response.ok) {
    throw new Error(
      'Failed to search question bank library',
    );
  }

  const payload =
    (await response.json()) as {
      items: ApiQuestionBankItem[];
      total: number;
      query: string | null;
      grade: number | null;
      science_domain: string | null;
      unit_id: string | null;
      cognitive_category: string | null;
    };

  return {
    items: payload.items.map(
      fromApiQuestionBankItem,
    ),
    total: payload.total,
    filters,
  };
}

export async function getQuestionBankLibraryItem(
  itemId: string,
): Promise<QuestionBankItem> {
  const response = await fetch(
    `${API_BASE_URL}/projects/question-bank/library/${itemId}`,
    {
      headers: buildAuthHeaders(),
    },
  );
  if (!response.ok) {
    throw new Error(
      'Failed to read question bank item',
    );
  }

  return fromApiQuestionBankItem(
    (await response.json()) as ApiQuestionBankItem,
  );
}


interface ApiQuestionBankReuseResponse {
  target_project_id: string;
  source_bank_item_id: string;
  reused: boolean;
  question: ApiQuestionItem;
}

export async function reuseQuestionBankItemInProject(
  itemId: string,
  targetProjectId: string,
): Promise<QuestionBankReuseResult> {
  const response = await fetch(
    `${API_BASE_URL}/projects/question-bank/library/${itemId}/reuse/${targetProjectId}`,
    {
      method: 'POST',
      headers: buildAuthHeaders(),
    },
  );
  if (!response.ok) {
    throw new Error(
      'Failed to reuse question bank item',
    );
  }

  const payload =
    (await response.json()) as ApiQuestionBankReuseResponse;

  return {
    targetProjectId: payload.target_project_id,
    sourceBankItemId: payload.source_bank_item_id,
    reused: payload.reused,
    question: fromApiQuestion(payload.question),
  };
}


interface ApiAssessmentBlueprint {
  title: string;
  grade: number;
  science_domain: string;
  subject_id: string;
  semester_id: string | null;
  unit_id: string | null;
  duration_minutes: number;
  total_marks: number;
  target_question_count: number;
  knowledge_percent: number;
  application_percent: number;
  reasoning_percent: number;
}

interface ApiAssessmentDraft {
  id: string;
  owner_account_id: string | null;
  source_project_id: string | null;
  blueprint: ApiAssessmentBlueprint;
  question_bank_item_ids: string[];
  status: "draft" | "ready";
  created_at: string;
  updated_at: string;
}

interface ApiAssessmentDraftDetail {
  draft: ApiAssessmentDraft;
  questions: Array<{
    bank_item_id: string;
    question_number: string;
    text: string;
    marks: number;
    cognitive_category:
      | "knowledge"
      | "application"
      | "reasoning"
      | "unclassified";
    grade: number | null;
    unit_id: string | null;
  }>;
  balance: {
    selected_question_count: number;
    selected_marks: number;
    remaining_question_count: number;
    remaining_marks: number;
    knowledge_count: number;
    application_count: number;
    reasoning_count: number;
    unclassified_count: number;
    knowledge_percent: number;
    application_percent: number;
    reasoning_percent: number;
    question_target_met: boolean;
    marks_target_met: boolean;
    cognitive_targets_valid: boolean;
  };
}

function toApiAssessmentBlueprint(
  blueprint: AssessmentBlueprint,
): ApiAssessmentBlueprint {
  return {
    title: blueprint.title,
    grade: blueprint.grade,
    science_domain: blueprint.scienceDomain,
    subject_id: blueprint.subjectId,
    semester_id: blueprint.semesterId,
    unit_id: blueprint.unitId,
    duration_minutes: blueprint.durationMinutes,
    total_marks: blueprint.totalMarks,
    target_question_count: blueprint.targetQuestionCount,
    knowledge_percent: blueprint.knowledgePercent,
    application_percent: blueprint.applicationPercent,
    reasoning_percent: blueprint.reasoningPercent,
  };
}

function fromApiAssessmentDraft(
  draft: ApiAssessmentDraft,
): AssessmentDraft {
  return {
    id: draft.id,
    ownerAccountId: draft.owner_account_id,
    sourceProjectId: draft.source_project_id,
    blueprint: {
      title: draft.blueprint.title,
      grade: draft.blueprint.grade,
      scienceDomain:
        draft.blueprint.science_domain as AssessmentBlueprint["scienceDomain"],
      subjectId: draft.blueprint.subject_id,
      semesterId: draft.blueprint.semester_id,
      unitId: draft.blueprint.unit_id,
      durationMinutes: draft.blueprint.duration_minutes,
      totalMarks: draft.blueprint.total_marks,
      targetQuestionCount:
        draft.blueprint.target_question_count,
      knowledgePercent: draft.blueprint.knowledge_percent,
      applicationPercent:
        draft.blueprint.application_percent,
      reasoningPercent: draft.blueprint.reasoning_percent,
    },
    questionBankItemIds: draft.question_bank_item_ids,
    status: draft.status,
    createdAt: draft.created_at,
    updatedAt: draft.updated_at,
  };
}

function fromApiAssessmentDetail(
  payload: ApiAssessmentDraftDetail,
): AssessmentDraftDetail {
  return {
    draft: fromApiAssessmentDraft(payload.draft),
    questions: payload.questions.map((question) => ({
      bankItemId: question.bank_item_id,
      questionNumber: question.question_number,
      text: question.text,
      marks: question.marks,
      cognitiveCategory: question.cognitive_category,
      grade: question.grade,
      unitId: question.unit_id,
    })),
    balance: {
      selectedQuestionCount:
        payload.balance.selected_question_count,
      selectedMarks: payload.balance.selected_marks,
      remainingQuestionCount:
        payload.balance.remaining_question_count,
      remainingMarks: payload.balance.remaining_marks,
      knowledgeCount: payload.balance.knowledge_count,
      applicationCount: payload.balance.application_count,
      reasoningCount: payload.balance.reasoning_count,
      unclassifiedCount:
        payload.balance.unclassified_count,
      knowledgePercent: payload.balance.knowledge_percent,
      applicationPercent:
        payload.balance.application_percent,
      reasoningPercent: payload.balance.reasoning_percent,
      questionTargetMet:
        payload.balance.question_target_met,
      marksTargetMet: payload.balance.marks_target_met,
      cognitiveTargetsValid:
        payload.balance.cognitive_targets_valid,
    },
  };
}

export async function createAssessmentDraft(
  sourceProjectId: string | null,
  blueprint: AssessmentBlueprint,
): Promise<AssessmentDraftDetail> {
  const response = await fetch(
    `${API_BASE_URL}/projects/assessment-builder`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...buildAuthHeaders(),
      },
      body: JSON.stringify({
        source_project_id: sourceProjectId,
        blueprint: toApiAssessmentBlueprint(blueprint),
      }),
    },
  );
  if (!response.ok) {
    throw new Error('Failed to create assessment draft');
  }
  return fromApiAssessmentDetail(
    (await response.json()) as ApiAssessmentDraftDetail,
  );
}

export async function updateAssessmentBlueprint(
  draftId: string,
  blueprint: AssessmentBlueprint,
): Promise<AssessmentDraftDetail> {
  const response = await fetch(
    `${API_BASE_URL}/projects/assessment-builder/${draftId}/blueprint`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...buildAuthHeaders(),
      },
      body: JSON.stringify(
        toApiAssessmentBlueprint(blueprint),
      ),
    },
  );
  if (!response.ok) {
    throw new Error('Failed to update assessment blueprint');
  }
  return fromApiAssessmentDetail(
    (await response.json()) as ApiAssessmentDraftDetail,
  );
}

export async function addAssessmentBankItem(
  draftId: string,
  bankItemId: string,
): Promise<AssessmentDraftDetail> {
  const response = await fetch(
    `${API_BASE_URL}/projects/assessment-builder/${draftId}/items/${bankItemId}`,
    {
      method: 'POST',
      headers: buildAuthHeaders(),
    },
  );
  if (!response.ok) {
    throw new Error('Failed to add assessment item');
  }
  return fromApiAssessmentDetail(
    (await response.json()) as ApiAssessmentDraftDetail,
  );
}

export async function removeAssessmentBankItem(
  draftId: string,
  bankItemId: string,
): Promise<AssessmentDraftDetail> {
  const response = await fetch(
    `${API_BASE_URL}/projects/assessment-builder/${draftId}/items/${bankItemId}`,
    {
      method: 'DELETE',
      headers: buildAuthHeaders(),
    },
  );
  if (!response.ok) {
    throw new Error('Failed to remove assessment item');
  }
  return fromApiAssessmentDetail(
    (await response.json()) as ApiAssessmentDraftDetail,
  );
}


function fromApiAssessmentValidation(payload: any): AssessmentBlueprintValidation {
  return {
    ready: payload.ready,
    totalSelectedQuestions: payload.total_selected_questions,
    targetQuestions: payload.target_questions,
    totalSelectedMarks: payload.total_selected_marks,
    targetMarks: payload.target_marks,
    knowledgeSelected: payload.knowledge_selected,
    knowledgeTarget: payload.knowledge_target,
    applicationSelected: payload.application_selected,
    applicationTarget: payload.application_target,
    reasoningSelected: payload.reasoning_selected,
    reasoningTarget: payload.reasoning_target,
    unclassifiedSelected: payload.unclassified_selected,
    issues: payload.issues,
  };
}

export async function autoSelectAssessmentQuestions(
  draftId: string,
): Promise<AssessmentAutoSelectionResult> {
  const response = await fetch(
    `${API_BASE_URL}/projects/assessment-builder/${draftId}/auto-select`,
    { method: 'POST', headers: buildAuthHeaders() },
  );
  if (!response.ok) throw new Error('Failed to auto-select assessment questions');
  const payload = await response.json();
  return {
    detail: fromApiAssessmentDetail(payload.detail),
    validation: fromApiAssessmentValidation(payload.validation),
    selectedItemIds: payload.selected_item_ids,
    skippedItemIds: payload.skipped_item_ids,
    shortages: payload.shortages,
  };
}

export async function validateAssessmentDraft(
  draftId: string,
): Promise<AssessmentBlueprintValidation> {
  const response = await fetch(
    `${API_BASE_URL}/projects/assessment-builder/${draftId}/validate`,
    { headers: buildAuthHeaders() },
  );
  if (!response.ok) throw new Error('Failed to validate assessment draft');
  return fromApiAssessmentValidation(await response.json());
}
