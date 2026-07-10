import type {
  ExtractedTextInfo,
  GlossaryTerm,
  ProjectMetadata,
  ProjectReadinessReport,
  ProjectSession,
  SchoolLogoInfo,
  QuestionItem,
  QuestionAssetInfo,
  QuestionStatus,
  StepKey,
  UploadedFileInfo,
  TranslationProviderStatus,
  AccountRole,
  AuthAccountPublic,
  AuthCreateAccountInput,
  AuthSessionInfo,
  AuthStatus,
  AuthUpdateAccountInput,
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

interface ApiQuestionItem {
  id: string;
  original_number: string;
  original_text: string;
  translated_text: string;
  marks: number | null;
  detected_marks: number | null;
  status: QuestionStatus;
  order_index: number;
  attachment_note?: string | null;
  attachments: ApiQuestionAssetInfo[];
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


function fromApiQuestionAsset(asset: ApiQuestionAssetInfo): QuestionAssetInfo {
  return {
    id: asset.id,
    name: asset.name,
    size: asset.size,
    type: asset.type,
    dataBase64: asset.data_base64,
  };
}

function fromApiQuestion(question: ApiQuestionItem): QuestionItem {
  return {
    id: question.id,
    originalNumber: question.original_number,
    originalText: question.original_text,
    translatedText: question.translated_text,
    marks: question.marks,
    detectedMarks: question.detected_marks,
    status: question.status,
    orderIndex: question.order_index,
    attachmentNote: question.attachment_note,
    attachments: (question.attachments ?? []).map(fromApiQuestionAsset),
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
  updates: Partial<Pick<QuestionItem, 'translatedText' | 'marks' | 'status' | 'reviewNotes'>>,
): Promise<ProjectSession> {
  const project = await requestJson<ApiProjectSession>(`/projects/${projectId}/questions/${questionId}`, {
    method: 'PATCH',
    body: JSON.stringify({
      translated_text: updates.translatedText,
      marks: updates.marks,
      status: updates.status,
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
  return await requestJson<TranslationProviderStatus>('/projects/translation-provider/status');
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
