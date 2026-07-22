import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  Archive,
  BookOpen,
  Filter,
  Loader2,
  RefreshCw,
  Search,
  Trash2,
  CopyPlus,
} from "lucide-react";
import {
  deleteQuestionBankItem,
  searchQuestionBankLibrary,
  reuseQuestionBankItemInProject,
} from "../../services/api";
import { localCurriculumRepository } from "../curriculum/local-curriculum.repository";
import type {
  CognitiveCategory,
  QuestionBankItem,
  QuestionItem,
  ScienceDomain,
} from "../../types/project";

interface QuestionBankLibraryProps {
  projectId: string | null;
  onQuestionReused: (question: QuestionItem) => void;
  onReturnHome: () => void;
}

const categoryLabels: Record<
  CognitiveCategory,
  string
> = {
  knowledge: "معرفة",
  application: "تطبيق",
  reasoning: "استدلال",
  unclassified: "غير مصنف",
};

export default function QuestionBankLibrary({
  projectId,
  onQuestionReused,
  onReturnHome,
}: QuestionBankLibraryProps) {
  const [query, setQuery] = useState("");
  const [grade, setGrade] =
    useState<number | null>(null);
  const [scienceDomain, setScienceDomain] =
    useState<ScienceDomain | null>(null);
  const [unitId, setUnitId] =
    useState<string | null>(null);
  const [category, setCategory] =
    useState<CognitiveCategory | null>(null);
  const [items, setItems] = useState<
    QuestionBankItem[]
  >([]);
  const [selectedItem, setSelectedItem] =
    useState<QuestionBankItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [workingId, setWorkingId] =
    useState<string | null>(null);
  const [reuseMessage, setReuseMessage] = useState("");

  const subjects = useMemo(
    () =>
      grade
        ? localCurriculumRepository
            .listSubjects(grade)
        : [],
    [grade],
  );
  const semesters = useMemo(
    () =>
      grade
        ? localCurriculumRepository
            .listSemesters(grade)
        : [],
    [grade],
  );
  const units = useMemo(() => {
    if (!grade || subjects.length === 0) {
      return [];
    }
    return semesters.flatMap((semester) =>
      localCurriculumRepository.listUnits(
        subjects[0].id,
        semester.id,
      ),
    );
  }, [grade, subjects, semesters]);

  async function runSearch() {
    setLoading(true);
    setError("");
    try {
      const result =
        await searchQuestionBankLibrary({
          query,
          grade,
          scienceDomain,
          unitId,
          cognitiveCategory: category,
        });
      setItems(result.items);
      setSelectedItem((current) => {
        if (
          current &&
          result.items.some(
            (item) => item.id === current.id,
          )
        ) {
          return current;
        }
        return result.items[0] ?? null;
      });
    } catch {
      setError("تعذر البحث في بنك الأسئلة.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void runSearch();
  }, []);

  function clearFilters() {
    setQuery("");
    setGrade(null);
    setScienceDomain(null);
    setUnitId(null);
    setCategory(null);
  }


async function reuseSelectedItem() {
  if (!selectedItem || !projectId) {
    setError("يجب فتح مشروع قبل إعادة استخدام السؤال.");
    return;
  }

  setWorkingId(`reuse-${selectedItem.id}`);
  setError("");
  setReuseMessage("");

  try {
    const result =
      await reuseQuestionBankItemInProject(
        selectedItem.id,
        projectId,
      );
    onQuestionReused(result.question);
    setReuseMessage(
      result.reused
        ? "تمت إضافة نسخة مستقلة إلى المشروع الحالي، وحالتها تحتاج مراجعة."
        : "هذا السؤال مضاف مسبقًا إلى المشروع الحالي.",
    );
  } catch {
    setError("تعذر إعادة استخدام السؤال في المشروع.");
  } finally {
    setWorkingId(null);
  }
}

  async function removeItem(item: QuestionBankItem) {
    setWorkingId(item.id);
    setError("");
    try {
      await deleteQuestionBankItem(
        item.sourceProjectId,
        item.id,
      );
      setItems((current) =>
        current.filter(
          (currentItem) =>
            currentItem.id !== item.id,
        ),
      );
      setSelectedItem((current) =>
        current?.id === item.id
          ? null
          : current,
      );
    } catch {
      setError("تعذر حذف السؤال من البنك.");
    } finally {
      setWorkingId(null);
    }
  }

  return (
    <main
      className="question-bank-library"
      dir="rtl"
    >
      <header className="question-bank-library-header">
        <div>
          <span>
            <Archive size={18} />
            مكتبة بنك الأسئلة
          </span>
          <h1>البحث والتصفية في الأسئلة المحفوظة</h1>
          <p>
            استعرض الأسئلة المراجعة حسب النص
            والمنهج والتصنيف المعرفي.
          </p>
        </div>
        <button
          type="button"
          className="secondary-button"
          onClick={onReturnHome}
        >
          <ArrowRight size={18} />
          العودة إلى المهام
        </button>
      </header>

      <section className="question-bank-filter-panel">
        <div className="question-bank-filter-title">
          <Filter size={20} />
          <h2>خيارات البحث</h2>
        </div>

        <div className="question-bank-filter-grid">
          <label className="question-bank-filter-query">
            <span>البحث النصي</span>
            <div>
              <Search size={17} />
              <input
                value={query}
                onChange={(event) =>
                  setQuery(event.target.value)
                }
                placeholder="ابحث في نص السؤال أو رقمه..."
              />
            </div>
          </label>

          <label>
            <span>الصف</span>
            <select
              value={grade ?? ""}
              onChange={(event) => {
                const value = event.target.value;
                setGrade(
                  value ? Number(value) : null,
                );
                setUnitId(null);
              }}
            >
              <option value="">كل الصفوف</option>
              {localCurriculumRepository
                .listGrades()
                .map((item) => (
                  <option
                    key={item}
                    value={item}
                  >
                    الصف {item}
                  </option>
                ))}
            </select>
          </label>

          <label>
            <span>المجال العلمي</span>
            <select
              value={scienceDomain ?? ""}
              onChange={(event) =>
                setScienceDomain(
                  (event.target.value ||
                    null) as ScienceDomain | null,
                )
              }
            >
              <option value="">كل المجالات</option>
              <option value="general_science">
                العلوم العامة
              </option>
              <option value="physics">
                الفيزياء
              </option>
              <option value="chemistry">
                الكيمياء
              </option>
              <option value="biology">
                الأحياء
              </option>
              <option value="environmental_science">
                العلوم البيئية
              </option>
            </select>
          </label>

          <label>
            <span>الوحدة</span>
            <select
              value={unitId ?? ""}
              disabled={!grade}
              onChange={(event) =>
                setUnitId(
                  event.target.value || null,
                )
              }
            >
              <option value="">كل الوحدات</option>
              {units.map((unit) => (
                <option
                  key={unit.id}
                  value={unit.id}
                >
                  {unit.title}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span>التصنيف المعرفي</span>
            <select
              value={category ?? ""}
              onChange={(event) =>
                setCategory(
                  (event.target.value ||
                    null) as CognitiveCategory | null,
                )
              }
            >
              <option value="">كل التصنيفات</option>
              {(
                Object.keys(
                  categoryLabels,
                ) as CognitiveCategory[]
              ).map((value) => (
                <option
                  key={value}
                  value={value}
                >
                  {categoryLabels[value]}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="question-bank-filter-actions">
          <button
            type="button"
            className="primary-button"
            onClick={() => void runSearch()}
            disabled={loading}
          >
            {loading ? (
              <Loader2
                size={17}
                className="spin-icon"
              />
            ) : (
              <Search size={17} />
            )}
            بحث
          </button>
          <button
            type="button"
            className="secondary-button"
            onClick={clearFilters}
          >
            مسح الفلاتر
          </button>
          <button
            type="button"
            className="secondary-button"
            onClick={() => void runSearch()}
            disabled={loading}
          >
            <RefreshCw size={17} />
            تحديث
          </button>
        </div>
      </section>

      {error ? (
        <div className="question-bank-library-error">
          {error}
        </div>
      ) : null}
      {reuseMessage ? (
        <div className="question-bank-library-success">
          {reuseMessage}
        </div>
      ) : null}

      <section className="question-bank-library-layout">
        <aside className="question-bank-results">
          <div className="question-bank-results-heading">
            <h2>النتائج</h2>
            <span>{items.length}</span>
          </div>

          {items.length > 0 ? (
            items.map((item) => {
              const question =
                item.questionSnapshot;
              return (
                <button
                  type="button"
                  key={item.id}
                  className={
                    selectedItem?.id === item.id
                      ? "is-active"
                      : undefined
                  }
                  onClick={() =>
                    setSelectedItem(item)
                  }
                >
                  <strong>
                    السؤال{" "}
                    {question.originalNumber ||
                      "—"}
                  </strong>
                  <span>
                    {question.translatedText ||
                      question.originalText}
                  </span>
                  <small>
                    {categoryLabels[
                      question.cognitiveCategory ??
                        "unclassified"
                    ]}
                    {" · "}
                    {question.curriculumGrade
                      ? `الصف ${
                          question.curriculumGrade
                        }`
                      : "دون صف"}
                  </small>
                </button>
              );
            })
          ) : (
            <p>
              لا توجد نتائج مطابقة للفلاتر.
            </p>
          )}
        </aside>

        <section className="question-bank-preview">
          {selectedItem ? (
            <>
              <div className="question-bank-preview-heading">
                <BookOpen size={22} />
                <div>
                  <span>معاينة السؤال</span>
                  <h2>
                    السؤال{" "}
                    {selectedItem.questionSnapshot
                      .originalNumber || "—"}
                  </h2>
                </div>
              </div>

              <div className="question-bank-preview-body">
                <section>
                  <h3>النص الأصلي</h3>
                  <p>
                    {selectedItem.questionSnapshot
                      .originalText ||
                      "لا يوجد نص أصلي."}
                  </p>
                </section>
                <section>
                  <h3>النص المترجم</h3>
                  <p>
                    {selectedItem.questionSnapshot
                      .translatedText ||
                      "لا توجد ترجمة."}
                  </p>
                </section>
                <section className="question-bank-preview-metadata">
                  <div>
                    <span>التصنيف</span>
                    <strong>
                      {categoryLabels[
                        selectedItem
                          .questionSnapshot
                          .cognitiveCategory ??
                          "unclassified"
                      ]}
                    </strong>
                  </div>
                  <div>
                    <span>الصف</span>
                    <strong>
                      {selectedItem
                        .questionSnapshot
                        .curriculumGrade ?? "—"}
                    </strong>
                  </div>
                  <div>
                    <span>الدرجة</span>
                    <strong>
                      {selectedItem
                        .questionSnapshot
                        .marks}
                    </strong>
                  </div>
                  <div>
                    <span>المشروع المصدر</span>
                    <strong>
                      {selectedItem.sourceProjectId}
                    </strong>
                  </div>
                </section>
              </div>

              <div className="question-bank-preview-actions">
                <button
                  type="button"
                  className="primary-button"
                  disabled={
                    !projectId ||
                    workingId === `reuse-${selectedItem.id}`
                  }
                  onClick={() =>
                    void reuseSelectedItem()
                  }
                >
                  {workingId === `reuse-${selectedItem.id}` ? (
                    <Loader2
                      size={16}
                      className="spin-icon"
                    />
                  ) : (
                    <CopyPlus size={16} />
                  )}
                  إضافة إلى المشروع الحالي
                </button>
                <button
                  type="button"
                  className="secondary-button danger"
                  disabled={
                    workingId === selectedItem.id
                  }
                  onClick={() =>
                    void removeItem(selectedItem)
                  }
                >
                  {workingId === selectedItem.id ? (
                    <Loader2
                      size={16}
                      className="spin-icon"
                    />
                  ) : (
                    <Trash2 size={16} />
                  )}
                  حذف من البنك
                </button>
              </div>
            </>
          ) : (
            <div className="question-bank-preview-empty">
              اختر سؤالًا لمعاينته.
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
