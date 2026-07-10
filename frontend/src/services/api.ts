import type {
  ExtractedTextInfo,
  GlossaryTerm,
  ProjectMetadata,
  ProjectSession,
  QuestionItem,
  QuestionStatus,
  StepKey,
  UploadedFileInfo,
} from '../types/project';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';

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

interface ApiExtractedTextInfo {
  text: string;
  preview: string;
  page_count: number;
  character_count: number;
  is_text_based: boolean;
  message: string;
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

interface ApiProjectSession {
  id: string;
  metadata: ApiProjectMetadata;
  uploaded_file: ApiUploadedFileInfo | null;
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

function fromApiProject(project: ApiProjectSession): ProjectSession {
  return {
    id: project.id,
    metadata: fromApiMetadata(project.metadata),
    uploadedFile: project.uploaded_file,
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
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`API request failed ${response.status}: ${body}`);
  }

  return (await response.json()) as T;
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

export async function uploadPdfAndExtractText(projectId: string, file: File): Promise<ProjectSession> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/upload-pdf`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`PDF extraction failed ${response.status}: ${body}`);
  }

  const project = (await response.json()) as ApiProjectSession;
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
