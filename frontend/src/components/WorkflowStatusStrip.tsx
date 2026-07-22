import { BookOpenCheck, CircleAlert, FileCheck2, ListChecks } from 'lucide-react';

interface WorkflowStatusStripProps {
  activeQuestions: number;
  needsReview: number;
  glossaryNeedsReview: number;
  outputLabel: string;
}

export function WorkflowStatusStrip({
  activeQuestions,
  needsReview,
  glossaryNeedsReview,
  outputLabel,
}: WorkflowStatusStripProps) {
  return (
    <section className="workspace-status-strip" aria-label="ملخص حالة المشروع">
      <div>
        <ListChecks size={20} />
        <span>الأسئلة</span>
        <strong>{activeQuestions}</strong>
      </div>
      <div className={needsReview > 0 ? 'needs-attention' : 'is-ready'}>
        <CircleAlert size={20} />
        <span>تحتاج مراجعة</span>
        <strong>{needsReview}</strong>
      </div>
      <div className={glossaryNeedsReview > 0 ? 'needs-attention' : 'is-ready'}>
        <BookOpenCheck size={20} />
        <span>مصطلحات غير معتمدة</span>
        <strong>{glossaryNeedsReview}</strong>
      </div>
      <div className="is-ready">
        <FileCheck2 size={20} />
        <span>المخرج</span>
        <strong>{outputLabel}</strong>
      </div>
    </section>
  );
}
