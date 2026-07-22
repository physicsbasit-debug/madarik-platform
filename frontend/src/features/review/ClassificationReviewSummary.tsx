import { AlertTriangle, CheckCircle2 } from "lucide-react";
import type { QuestionItem } from "../../types/project";

interface ClassificationReviewSummaryProps {
  questions: QuestionItem[];
}

export function ClassificationReviewSummary({
  questions,
}: ClassificationReviewSummaryProps) {
  const active = questions.filter(
    (question) => question.status !== "deleted",
  );
  const unclassified = active.filter(
    (question) =>
      (question.cognitiveCategory ??
        "unclassified") === "unclassified",
  );
  const unlinked = active.filter(
    (question) =>
      !question.curriculumGrade ||
      !question.curriculumSubjectId ||
      !question.curriculumSemesterId,
  );
  const complete =
    active.length -
    new Set([
      ...unclassified.map((item) => item.id),
      ...unlinked.map((item) => item.id),
    ]).size;

  return (
    <section className="classification-review-summary">
      <div>
        <CheckCircle2 size={20} />
        <span>مكتمل التصنيف والربط</span>
        <strong>{complete}</strong>
      </div>
      <div>
        <AlertTriangle size={20} />
        <span>غير مصنف</span>
        <strong>{unclassified.length}</strong>
      </div>
      <div>
        <AlertTriangle size={20} />
        <span>غير مرتبط بالمنهج</span>
        <strong>{unlinked.length}</strong>
      </div>
    </section>
  );
}
