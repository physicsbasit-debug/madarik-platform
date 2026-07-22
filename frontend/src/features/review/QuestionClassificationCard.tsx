import { BrainCircuit, Sparkles } from "lucide-react";
import type {
  CognitiveCategory,
  QuestionItem,
} from "../../types/project";
import { classifyQuestion } from "./question-classifier";

interface QuestionClassificationCardProps {
  question: QuestionItem;
  disabled?: boolean;
  onUpdateQuestion: (
    questionId: string,
    updates: Partial<QuestionItem>,
  ) => void;
}

const labels: Record<CognitiveCategory, string> = {
  knowledge: "معرفة",
  application: "تطبيق",
  reasoning: "استدلال",
  unclassified: "غير مصنف",
};

export function QuestionClassificationCard({
  question,
  disabled = false,
  onUpdateQuestion,
}: QuestionClassificationCardProps) {
  const category =
    question.cognitiveCategory ?? "unclassified";
  const confidence =
    question.classificationConfidence ?? 0;

  function applyAutomaticClassification() {
    const result = classifyQuestion(question);
    onUpdateQuestion(question.id, {
      cognitiveCategory: result.category,
      classificationConfidence: result.confidence,
      classificationReason: result.reason,
      classificationSource: result.source,
    });
  }

  function setManualCategory(
    nextCategory: CognitiveCategory,
  ) {
    onUpdateQuestion(question.id, {
      cognitiveCategory: nextCategory,
      classificationConfidence: 1,
      classificationReason:
        "تم تعديل التصنيف يدويًا بواسطة المراجع.",
      classificationSource: "manual",
    });
  }

  return (
    <section className="question-classification-card">
      <div className="question-classification-heading">
        <BrainCircuit size={21} />
        <div>
          <span>التصنيف المعرفي</span>
          <h3>{labels[category]}</h3>
        </div>
        <span
          className={
            `classification-badge is-${category}`
          }
        >
          {labels[category]}
        </span>
      </div>

      <div className="question-classification-controls">
        <label>
          <span>الفئة</span>
          <select
            value={category}
            disabled={disabled}
            onChange={(event) =>
              setManualCategory(
                event.target.value as CognitiveCategory,
              )
            }
          >
            <option value="unclassified">
              غير مصنف
            </option>
            <option value="knowledge">معرفة</option>
            <option value="application">
              تطبيق
            </option>
            <option value="reasoning">
              استدلال
            </option>
          </select>
        </label>

        <button
          type="button"
          className="secondary-button compact"
          disabled={disabled}
          onClick={applyAutomaticClassification}
        >
          <Sparkles size={16} />
          تصنيف آلي
        </button>
      </div>

      <div className="classification-confidence">
        <div>
          <span>الثقة</span>
          <strong>
            {Math.round(confidence * 100)}%
          </strong>
        </div>
        <progress
          max={100}
          value={confidence * 100}
        />
      </div>

      <p>
        {question.classificationReason ??
          "لم يُسجل سبب للتصنيف بعد."}
      </p>
      <small>
        المصدر:{" "}
        {question.classificationSource ===
        "automatic_rule"
          ? "قواعد لغوية"
          : "تعديل يدوي"}
      </small>
    </section>
  );
}
