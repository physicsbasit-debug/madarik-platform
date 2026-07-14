import type {
  ExtractedTextInfo,
  GlossaryTerm,
  ProjectMetadata,
  ProjectReadinessReport,
  ProjectSession,
  PdfLayoutAssetInfo,
  SchoolLogoInfo,
  QuestionItem,
  QuestionAssetInfo,
  QuestionPart,
  QuestionStatus,
  StepKey,
  UploadedFileInfo,
  TranslationProviderStatus,
  AnswerKeyItem,
  EducationalAnalysisReport,
  EducationalQualityToolsReport,
  AuthAccountPublic,
  AuthCreateAccountInput,
  AuthSessionInfo,
  AuthStatus,
  AuthUpdateAccountInput,
  VisualCropRequest,
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

interface ApiExtractedTextInfo {
  text: string;
  preview: string;
  page_count: number;
  character_count: number;
  is_text_based: boolean;
  message: string;
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

export async function loadDemoContent(projectId: string): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/demo-content`, { method: 'POST' });
  return fromApiProject(project);
}

export async function updateQuestion(
  projectId: string,
  questionId: string,
  updates: Partial<Pick<QuestionItem, 'translatedText' | 'marks' | 'status' | 'parts' | 'reviewNotes'>>,
): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/questions/${questionId}`, {
    method: 'PATCH',
    body: JSON.stringify({
      translated_text: updates.translatedText,
      marks: updates.marks,
      status: updates.status,
      parts: updates.parts?.map(toApiQuestionPart),
      review_notes: updates.reviewNotes,
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
