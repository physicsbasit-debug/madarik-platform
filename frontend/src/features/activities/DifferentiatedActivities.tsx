import { useEffect, useState } from "react";
import {
  ArrowRight,
  Layers3,
  Loader2,
  Plus,
  Trash2,
} from "lucide-react";
import {
  createDifferentiatedActivity,
  deleteDifferentiatedActivity,
  generateDifferentiatedActivities,
  listDifferentiatedActivities,
  searchQuestionBankLibrary,
} from "../../services/api";
import type {
  DifferentiatedActivity,
  DifferentiationLevel,
  QuestionBankItem,
  ScienceDomain,
} from "../../types/project";

interface Props {
  projectId: string | null;
  onReturnHome: () => void;
}

const labels: Record<DifferentiationLevel, string> = {
  support: "دعم",
  core: "أساسي",
  extension: "إثراء",
};

export default function DifferentiatedActivities({
  projectId,
  onReturnHome,
}: Props) {
  const [items, setItems] = useState<DifferentiatedActivity[]>([]);
  const [bankItems, setBankItems] = useState<QuestionBankItem[]>([]);
  const [title, setTitle] = useState("");
  const [objective, setObjective] = useState("");
  const [instructions, setInstructions] = useState("");
  const [coreTask, setCoreTask] = useState("");
  const [selectedBankItemId, setSelectedBankItemId] =
    useState<string | null>(null);
  const [level, setLevel] =
    useState<DifferentiationLevel>("core");
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function refresh() {
    try {
      const [activities, bank] = await Promise.all([
        listDifferentiatedActivities(),
        searchQuestionBankLibrary({}),
      ]);
      setItems(activities);
      setBankItems(bank.items);
    } catch {
      setError("تعذر تحميل الأنشطة.");
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function saveOne() {
    if (!title.trim() || !objective.trim() || !instructions.trim()) {
      setError("العنوان والهدف والتعليمات مطلوبة.");
      return;
    }
    setWorking(true);
    setError("");
    try {
      const created = await createDifferentiatedActivity({
        sourceProjectId: projectId,
        title: title.trim(),
        grade: 10,
        scienceDomain: "physics" as ScienceDomain,
        subjectId: "g10-physics",
        level,
        objective: objective.trim(),
        instructions: instructions.trim(),
        estimatedMinutes: 20,
      });
      setItems((current) => [created, ...current]);
      setMessage("تم حفظ النشاط.");
    } catch {
      setError("تعذر حفظ النشاط.");
    } finally {
      setWorking(false);
    }
  }

  async function generateSet() {
    if (!title.trim() || !objective.trim() || !coreTask.trim()) {
      setError("العنوان والهدف والمهمة الأساسية مطلوبة.");
      return;
    }
    setWorking(true);
    setError("");
    setMessage("");
    try {
      const result = await generateDifferentiatedActivities({
        sourceProjectId: projectId,
        sourceQuestionBankItemId: selectedBankItemId,
        title: title.trim(),
        grade: 10,
        scienceDomain: "physics" as ScienceDomain,
        subjectId: "g10-physics",
        objective: objective.trim(),
        coreTask: coreTask.trim(),
        estimatedMinutes: 20,
      });
      setItems((current) => [...result.items, ...current]);
      setMessage("تم إنشاء ثلاث نسخ: دعم، أساسي، وإثراء.");
    } catch {
      setError("تعذر توليد الأنشطة.");
    } finally {
      setWorking(false);
    }
  }

  async function remove(id: string) {
    try {
      await deleteDifferentiatedActivity(id);
      setItems((current) =>
        current.filter((item) => item.id !== id),
      );
    } catch {
      setError("تعذر حذف النشاط.");
    }
  }

  return (
    <main className="differentiated-activities" dir="rtl">
      <header className="differentiated-header">
        <div>
          <span>
            <Layers3 size={18} />
            الأنشطة المتمايزة
          </span>
          <h1>أنشطة علمية بمستويات دعم مختلفة</h1>
        </div>
        <button
          type="button"
          className="secondary-button"
          onClick={onReturnHome}
        >
          <ArrowRight size={18} />
          العودة
        </button>
      </header>

      <section className="differentiated-form-card">
        <h2>إنشاء أو توليد نشاط</h2>
        <div className="differentiated-form-grid">
          <input
            placeholder="العنوان"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
          />
          <select
            value={level}
            onChange={(event) =>
              setLevel(
                event.target.value as DifferentiationLevel,
              )
            }
          >
            <option value="support">دعم</option>
            <option value="core">أساسي</option>
            <option value="extension">إثراء</option>
          </select>
          <textarea
            placeholder="الهدف"
            value={objective}
            onChange={(event) =>
              setObjective(event.target.value)
            }
          />
          <textarea
            placeholder="التعليمات للنشاط اليدوي"
            value={instructions}
            onChange={(event) =>
              setInstructions(event.target.value)
            }
          />
          <textarea
            placeholder="المهمة الأساسية المشتركة للتوليد"
            value={coreTask}
            onChange={(event) =>
              setCoreTask(event.target.value)
            }
          />
          <select
            value={selectedBankItemId ?? ""}
            onChange={(event) =>
              setSelectedBankItemId(
                event.target.value || null,
              )
            }
          >
            <option value="">دون سؤال مرجعي</option>
            {bankItems.map((item) => (
              <option key={item.id} value={item.id}>
                {item.questionSnapshot.translatedText ||
                  item.questionSnapshot.originalText}
              </option>
            ))}
          </select>
        </div>

        <div className="differentiated-action-row">
          <button
            type="button"
            className="primary-button"
            disabled={working}
            onClick={() => void generateSet()}
          >
            {working ? (
              <Loader2 size={17} className="spin-icon" />
            ) : (
              <Layers3 size={17} />
            )}
            توليد ثلاث نسخ
          </button>
          <button
            type="button"
            className="secondary-button"
            disabled={working}
            onClick={() => void saveOne()}
          >
            <Plus size={17} />
            حفظ نشاط واحد
          </button>
        </div>
      </section>

      {message ? (
        <div className="differentiated-success">
          {message}
        </div>
      ) : null}
      {error ? (
        <div className="differentiated-error">
          {error}
        </div>
      ) : null}

      <section className="differentiated-list">
        <h2>الأنشطة المحفوظة</h2>
        {items.map((item) => (
          <article key={item.id}>
            <div className="differentiated-item-heading">
              <div>
                <span
                  className={`differentiated-level ${item.level}`}
                >
                  {labels[item.level]}
                </span>
                <h3>{item.title}</h3>
              </div>
              <button
                type="button"
                className="secondary-button compact"
                onClick={() => void remove(item.id)}
              >
                <Trash2 size={15} />
                حذف
              </button>
            </div>
            <p>{item.objective}</p>
            <section>
              <strong>التعليمات</strong>
              <p>{item.instructions}</p>
            </section>
          </article>
        ))}
      </section>
    </main>
  );
}
