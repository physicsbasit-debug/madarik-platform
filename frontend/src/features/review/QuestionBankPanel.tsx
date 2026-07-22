import { useEffect, useMemo, useState } from "react";
import {
  Archive,
  CheckCircle2,
  Loader2,
  RefreshCw,
  Save,
  Trash2,
} from "lucide-react";
import {
  deleteQuestionBankItem,
  listProjectQuestionBank,
  saveQuestionToBank,
} from "../../services/api";
import type {
  QuestionBankItem,
  QuestionItem,
} from "../../types/project";

interface QuestionBankPanelProps {
  projectId: string;
  selectedQuestion: QuestionItem | null;
  disabled?: boolean;
}

export function QuestionBankPanel({
  projectId,
  selectedQuestion,
  disabled = false,
}: QuestionBankPanelProps) {
  const [items, setItems] = useState<
    QuestionBankItem[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [workingId, setWorkingId] = useState<
    string | null
  >(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function refresh() {
    setLoading(true);
    setError("");
    try {
      const result =
        await listProjectQuestionBank(projectId);
      setItems(result.items);
    } catch {
      setError("تعذر قراءة بنك الأسئلة.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, [projectId]);

  const selectedBankItem = useMemo(
    () =>
      selectedQuestion
        ? items.find(
            (item) =>
              item.sourceQuestionId ===
              selectedQuestion.id,
          ) ?? null
        : null,
    [items, selectedQuestion],
  );

  async function saveSelectedQuestion() {
    if (!selectedQuestion) return;

    setWorkingId(selectedQuestion.id);
    setMessage("");
    setError("");
    try {
      const saved = await saveQuestionToBank(
        projectId,
        selectedQuestion.id,
      );
      setItems((current) => [
        saved,
        ...current.filter(
          (item) => item.id !== saved.id,
        ),
      ]);
      setMessage(
        selectedBankItem
          ? "تم تحديث نسخة السؤال داخل البنك."
          : "تم حفظ السؤال في بنك الأسئلة.",
      );
    } catch {
      setError("تعذر حفظ السؤال في البنك.");
    } finally {
      setWorkingId(null);
    }
  }

  async function removeItem(itemId: string) {
    setWorkingId(itemId);
    setMessage("");
    setError("");
    try {
      await deleteQuestionBankItem(
        projectId,
        itemId,
      );
      setItems((current) =>
        current.filter(
          (item) => item.id !== itemId,
        ),
      );
      setMessage(
        "تم حذف العنصر من البنك دون حذف السؤال الأصلي.",
      );
    } catch {
      setError("تعذر حذف العنصر من البنك.");
    } finally {
      setWorkingId(null);
    }
  }

  return (
    <section className="question-bank-panel">
      <div className="question-bank-heading">
        <div>
          <Archive size={22} />
          <div>
            <span>بنك الأسئلة</span>
            <h3>{items.length} سؤالًا محفوظًا</h3>
          </div>
        </div>
        <button
          type="button"
          className="secondary-button compact"
          disabled={loading}
          onClick={() => void refresh()}
        >
          {loading ? (
            <Loader2
              size={16}
              className="spin-icon"
            />
          ) : (
            <RefreshCw size={16} />
          )}
          تحديث
        </button>
      </div>

      <div className="question-bank-selected">
        <div>
          <strong>
            {selectedQuestion
              ? `السؤال ${
                  selectedQuestion.originalNumber ||
                  "المحدد"
                }`
              : "لا يوجد سؤال محدد"}
          </strong>
          <span>
            {selectedBankItem
              ? "السؤال محفوظ، ويمكن تحديث نسخته."
              : "يمكن حفظ السؤال بعد مراجعته."}
          </span>
        </div>
        <button
          type="button"
          className="primary-button compact"
          disabled={
            disabled ||
            !selectedQuestion ||
            selectedQuestion.status === "deleted" ||
            workingId === selectedQuestion?.id
          }
          onClick={() =>
            void saveSelectedQuestion()
          }
        >
          {workingId === selectedQuestion?.id ? (
            <Loader2
              size={16}
              className="spin-icon"
            />
          ) : selectedBankItem ? (
            <CheckCircle2 size={16} />
          ) : (
            <Save size={16} />
          )}
          {selectedBankItem
            ? "تحديث السؤال المحفوظ"
            : "حفظ في البنك"}
        </button>
      </div>

      {message ? (
        <div className="question-bank-message">
          {message}
        </div>
      ) : null}
      {error ? (
        <div className="question-bank-error">
          {error}
        </div>
      ) : null}

      <div className="question-bank-list">
        {items.length > 0 ? (
          items.map((item) => (
            <article key={item.id}>
              <div>
                <strong>
                  السؤال{" "}
                  {item.questionSnapshot
                    .originalNumber || "—"}
                </strong>
                <span>
                  {item.questionSnapshot
                    .translatedText ||
                    item.questionSnapshot
                      .originalText}
                </span>
                <small>
                  {item.questionSnapshot
                    .cognitiveCategory ??
                    "unclassified"}
                  {" · "}
                  {item.questionSnapshot
                    .curriculumGrade
                    ? `الصف ${
                        item.questionSnapshot
                          .curriculumGrade
                      }`
                    : "دون صف"}
                </small>
              </div>
              <button
                type="button"
                className="secondary-button compact"
                disabled={workingId === item.id}
                onClick={() =>
                  void removeItem(item.id)
                }
              >
                {workingId === item.id ? (
                  <Loader2
                    size={15}
                    className="spin-icon"
                  />
                ) : (
                  <Trash2 size={15} />
                )}
                حذف من البنك
              </button>
            </article>
          ))
        ) : (
          <p className="question-bank-empty">
            لم تُحفظ أسئلة في البنك بعد.
          </p>
        )}
      </div>
    </section>
  );
}
