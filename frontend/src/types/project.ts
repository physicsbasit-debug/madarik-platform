export type StepKey = 'setup' | 'upload' | 'extract' | 'glossary' | 'review' | 'export';

export type QuestionStatus = 'approved' | 'needs_review' | 'deleted';

export interface ProjectMetadata {
  schoolName: string;
  subject: string;
  grade: string;
  semester: string;
  paperTitle: string;
  duration: string;
  totalMarks: string;
  teacherName: string;
  date: string;
  outputMode: 'arabic' | 'bilingual';
}

export interface QuestionItem {
  id: string;
  originalNumber: string;
  currentNumber: number;
  originalText: string;
  translatedText: string;
  marks: number | null;
  status: QuestionStatus;
  orderIndex: number;
}

export interface GlossaryTerm {
  id: string;
  englishTerm: string;
  arabicTerm: string;
  status: 'approved' | 'needs_review';
}
