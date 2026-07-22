import { useMemo, useState } from "react";
import { ArrowDown, ArrowRight, ArrowUp, ClipboardList, Loader2, Plus, Save, Trash2 } from "lucide-react";
import {
  addAssessmentBankItem,
  createAssessmentDraft,
  removeAssessmentBankItem,
  searchQuestionBankLibrary,
  updateAssessmentBlueprint,
  updateAssessmentLayout,
  autoSelectAssessmentQuestions,
  validateAssessmentDraft,
} from "../../services/api";
import { localCurriculumRepository } from "../curriculum/local-curriculum.repository";
import type {
  AssessmentBlueprint,
  AssessmentDraftDetail,
  AssessmentBlueprintValidation,
  CognitiveCategory,
  QuestionBankItem,
} from "../../types/project";

interface AssessmentBuilderProps {
  projectId: string | null;
  onReturnHome: () => void;
}

const categoryLabels: Record<CognitiveCategory, string> = {
  knowledge: "معرفة",
  application: "تطبيق",
  reasoning: "استدلال",
  unclassified: "غير مصنف",
};


type NumericBlueprintKey =
  | "totalMarks"
  | "targetQuestionCount"
  | "durationMinutes"
  | "knowledgePercent"
  | "applicationPercent"
  | "reasoningPercent";

const numericBlueprintFields: Array<{
  label: string;
  key: NumericBlueprintKey;
  min: number;
  max: number;
}> = [
  { label: "الدرجة الكلية", key: "totalMarks", min: 1, max: 200 },
  { label: "عدد الأسئلة المستهدف", key: "targetQuestionCount", min: 1, max: 100 },
  { label: "المدة بالدقائق", key: "durationMinutes", min: 5, max: 240 },
  { label: "معرفة %", key: "knowledgePercent", min: 0, max: 100 },
  { label: "تطبيق %", key: "applicationPercent", min: 0, max: 100 },
  { label: "استدلال %", key: "reasoningPercent", min: 0, max: 100 },
];

const initialBlueprint: AssessmentBlueprint = {
  title: "اختبار علوم جديد",
  grade: 10,
  scienceDomain: "physics",
  subjectId: "g10-physics",
  semesterId: "g10-sem2",
  unitId: null,
  durationMinutes: 40,
  totalMarks: 20,
  targetQuestionCount: 10,
  knowledgePercent: 30,
  applicationPercent: 40,
  reasoningPercent: 30,
};

export default function AssessmentBuilder({
  projectId,
  onReturnHome,
}: AssessmentBuilderProps) {
  const [blueprint, setBlueprint] = useState(initialBlueprint);
  const [detail, setDetail] = useState<AssessmentDraftDetail | null>(null);
  const [bankItems, setBankItems] = useState<QuestionBankItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [workingId, setWorkingId] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [validation, setValidation] = useState<AssessmentBlueprintValidation | null>(null);
  const [shortages, setShortages] = useState<string[]>([]);

  const subjects = useMemo(
    () => localCurriculumRepository.listSubjects(blueprint.grade),
    [blueprint.grade],
  );
  const semesters = useMemo(
    () => localCurriculumRepository.listSemesters(blueprint.grade),
    [blueprint.grade],
  );
  const units = useMemo(() => {
    if (!blueprint.subjectId || !blueprint.semesterId) return [];
    return localCurriculumRepository.listUnits(
      blueprint.subjectId,
      blueprint.semesterId,
    );
  }, [blueprint.subjectId, blueprint.semesterId]);

  const percentTotal =
    blueprint.knowledgePercent +
    blueprint.applicationPercent +
    blueprint.reasoningPercent;

  async function loadCandidates(current: AssessmentBlueprint) {
    const result = await searchQuestionBankLibrary({
      grade: current.grade,
      scienceDomain: current.scienceDomain,
      unitId: current.unitId,
    });
    setBankItems(result.items);
  }

  async function saveBlueprint() {
    if (percentTotal !== 100) {
      setError("يجب أن يكون مجموع نسب المستويات المعرفية 100%.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const next = detail
        ? await updateAssessmentBlueprint(detail.draft.id, blueprint)
        : await createAssessmentDraft(projectId, blueprint);
      setDetail(next);
      await loadCandidates(next.draft.blueprint);
      setMessage(detail ? "تم تحديث جدول المواصفات." : "تم إنشاء مسودة الاختبار.");
    } catch {
      setError("تعذر حفظ مسودة الاختبار.");
    } finally {
      setLoading(false);
    }
  }

  async function addItem(item: QuestionBankItem) {
    if (!detail) return;
    setWorkingId(item.id);
    try {
      setDetail(await addAssessmentBankItem(detail.draft.id, item.id));
    } catch {
      setError("تعذر إضافة السؤال.");
    } finally {
      setWorkingId(null);
    }
  }


async function runAutomaticSelection() {
  if (!detail) return;
  setLoading(true);
  setError("");
  setShortages([]);
  try {
    const result = await autoSelectAssessmentQuestions(detail.draft.id);
    setDetail(result.detail);
    setValidation(result.validation);
    setShortages(result.shortages);
    setMessage("تم تنفيذ الاختيار الآلي، ويمكنك تعديل النتيجة يدويًا.");
  } catch {
    setError("تعذر تنفيذ الاختيار الآلي.");
  } finally {
    setLoading(false);
  }
}

async function runValidation() {
  if (!detail) return;
  setLoading(true);
  setError("");
  try {
    setValidation(await validateAssessmentDraft(detail.draft.id));
  } catch {
    setError("تعذر التحقق من جاهزية المسودة.");
  } finally {
    setLoading(false);
  }
}


function currentConfigurations() {
  if (!detail) return [];
  const byId = new Map(
    detail.draft.itemConfigurations.map(
      (item) => [item.bankItemId, item],
    ),
  );
  return detail.questions.map((question, index) => ({
    bankItemId: question.bankItemId,
    sectionId:
      byId.get(question.bankItemId)?.sectionId ??
      detail.draft.sections[0]?.id ??
      null,
    orderIndex: index + 1,
    marksOverride:
      byId.get(question.bankItemId)?.marksOverride ??
      null,
  }));
}

async function saveLayout(
  nextSections = detail?.draft.sections ?? [],
  nextConfigurations = currentConfigurations(),
) {
  if (!detail) return;
  setLoading(true);
  setError("");
  try {
    const next = await updateAssessmentLayout(
      detail.draft.id,
      nextSections,
      nextConfigurations,
    );
    setDetail(next);
    setMessage("تم حفظ ترتيب الاختبار وأقسامه ودرجاته.");
    setValidation(null);
  } catch {
    setError("تعذر حفظ بناء الاختبار.");
  } finally {
    setLoading(false);
  }
}

function moveQuestion(
  bankItemId: string,
  direction: -1 | 1,
) {
  if (!detail) return;
  const configs = currentConfigurations();
  const index = configs.findIndex(
    (item) => item.bankItemId === bankItemId,
  );
  const target = index + direction;
  if (
    index < 0 ||
    target < 0 ||
    target >= configs.length
  ) {
    return;
  }
  [configs[index], configs[target]] = [
    configs[target],
    configs[index],
  ];
  const normalized = configs.map((item, itemIndex) => ({
    ...item,
    orderIndex: itemIndex + 1,
  }));
  void saveLayout(
    detail.draft.sections,
    normalized,
  );
}

function updateQuestionLayout(
  bankItemId: string,
  updates: {
    sectionId?: string | null;
    marksOverride?: number | null;
  },
) {
  if (!detail) return;
  const configs = currentConfigurations().map((item) =>
    item.bankItemId === bankItemId
      ? { ...item, ...updates }
      : item,
  );
  void saveLayout(detail.draft.sections, configs);
}

function addSection() {
  if (!detail) return;
  const nextSections = [
    ...detail.draft.sections,
    {
      id: crypto.randomUUID(),
      title: `القسم ${detail.draft.sections.length + 1}`,
      instructions: null,
      orderIndex: detail.draft.sections.length + 1,
    },
  ];
  void saveLayout(nextSections);
}

function renameSection(
  sectionId: string,
  title: string,
) {
  if (!detail) return;
  const nextSections = detail.draft.sections.map(
    (section) =>
      section.id === sectionId
        ? { ...section, title }
        : section,
  );
  setDetail({
    ...detail,
    draft: {
      ...detail.draft,
      sections: nextSections,
    },
  });
}

async function removeItem(itemId: string) {
    if (!detail) return;
    setWorkingId(itemId);
    try {
      setDetail(await removeAssessmentBankItem(detail.draft.id, itemId));
    } catch {
      setError("تعذر إزالة السؤال.");
    } finally {
      setWorkingId(null);
    }
  }

  function changeGrade(grade: number) {
    const nextSubjects = localCurriculumRepository.listSubjects(grade);
    const nextSemesters = localCurriculumRepository.listSemesters(grade);
    const subject = nextSubjects[0] ?? null;
    setBlueprint((current) => ({
      ...current,
      grade,
      scienceDomain: subject?.scienceDomain ?? "general_science",
      subjectId: subject?.id ?? "",
      semesterId: nextSemesters[0]?.id ?? null,
      unitId: null,
    }));
  }

  const selectedIds = new Set(detail?.draft.questionBankItemIds ?? []);

  return (
    <main className="assessment-builder" dir="rtl">
      <header className="assessment-builder-header">
        <div>
          <span><ClipboardList size={19} /> منشئ الاختبارات</span>
          <h1>جدول المواصفات ومسودة الاختبار</h1>
          <p>حدّد المستهدفات، ثم أضف أسئلة البنك وراقب التوازن الفعلي.</p>
        </div>
        <button type="button" className="secondary-button" onClick={onReturnHome}>
          <ArrowRight size={18} /> العودة إلى المهام
        </button>
      </header>

      <section className="assessment-blueprint-card">
        <div className="assessment-section-heading">
          <div><span>الخطوة الأولى</span><h2>جدول المواصفات</h2></div>
          <strong className={percentTotal === 100 ? "is-valid" : "is-invalid"}>
            مجموع النسب: {percentTotal}%
          </strong>
        </div>

        <div className="assessment-blueprint-grid">
          <label className="assessment-wide">
            <span>عنوان الاختبار</span>
            <input value={blueprint.title} onChange={(e) =>
              setBlueprint((c) => ({ ...c, title: e.target.value }))} />
          </label>
          <label><span>الصف</span>
            <select value={blueprint.grade} onChange={(e) => changeGrade(Number(e.target.value))}>
              {localCurriculumRepository.listGrades().map((grade) =>
                <option key={grade} value={grade}>الصف {grade}</option>)}
            </select>
          </label>
          <label><span>المادة</span>
            <select value={blueprint.subjectId} onChange={(e) => {
              const subject = subjects.find((item) => item.id === e.target.value);
              setBlueprint((c) => ({
                ...c,
                subjectId: e.target.value,
                scienceDomain: subject?.scienceDomain ?? c.scienceDomain,
                unitId: null,
              }));
            }}>
              {subjects.map((subject) =>
                <option key={subject.id} value={subject.id}>{subject.title}</option>)}
            </select>
          </label>
          <label><span>الفصل</span>
            <select value={blueprint.semesterId ?? ""} onChange={(e) =>
              setBlueprint((c) => ({ ...c, semesterId: e.target.value || null, unitId: null }))}>
              {semesters.map((semester) =>
                <option key={semester.id} value={semester.id}>{semester.title}</option>)}
            </select>
          </label>
          <label><span>الوحدة</span>
            <select value={blueprint.unitId ?? ""} onChange={(e) =>
              setBlueprint((c) => ({ ...c, unitId: e.target.value || null }))}>
              <option value="">كل الوحدات</option>
              {units.map((unit) =>
                <option key={unit.id} value={unit.id}>{unit.title}</option>)}
            </select>
          </label>
          {numericBlueprintFields.map((field) => (
            <label key={field.key}>
              <span>{field.label}</span>
              <input
                type="number"
                min={field.min}
                max={field.max}
                value={blueprint[field.key]}
                onChange={(event) =>
                  setBlueprint((current) => ({
                    ...current,
                    [field.key]: Number(event.target.value),
                  }))}
              />
            </label>
          ))}
        </div>

        <button type="button" className="primary-button"
          disabled={loading || percentTotal !== 100}
          onClick={() => void saveBlueprint()}>
          {loading ? <Loader2 size={17} className="spin-icon" /> : <Save size={17} />}
          {detail ? "حفظ جدول المواصفات" : "إنشاء مسودة الاختبار"}
        </button>
        {detail ? (
          <div className="assessment-blueprint-actions">
            <button type="button" className="secondary-button" disabled={loading} onClick={() => void runAutomaticSelection()}>اختيار آلي</button>
            <button type="button" className="secondary-button" disabled={loading} onClick={() => void runValidation()}>تحقق من الجاهزية</button>
          </div>
        ) : null}
      </section>

      {message ? <div className="assessment-message">{message}</div> : null}
      {error ? <div className="assessment-error">{error}</div> : null}

      {detail ? (
        <>
          <section className="assessment-balance-grid">
            <article><span>الأسئلة</span><strong>{detail.balance.selectedQuestionCount}/{detail.draft.blueprint.targetQuestionCount}</strong><small>المتبقي {detail.balance.remainingQuestionCount}</small></article>
            <article><span>الدرجات</span><strong>{detail.balance.selectedMarks}/{detail.draft.blueprint.totalMarks}</strong><small>المتبقي {detail.balance.remainingMarks}</small></article>
            <article><span>معرفة</span><strong>{detail.balance.knowledgePercent}%</strong><small>المستهدف {detail.draft.blueprint.knowledgePercent}%</small></article>
            <article><span>تطبيق</span><strong>{detail.balance.applicationPercent}%</strong><small>المستهدف {detail.draft.blueprint.applicationPercent}%</small></article>
            <article><span>استدلال</span><strong>{detail.balance.reasoningPercent}%</strong><small>المستهدف {detail.draft.blueprint.reasoningPercent}%</small></article>
          </section>

          {validation ? (
            <section className={validation.ready ? "assessment-validation-panel is-ready" : "assessment-validation-panel"}>
              <div><strong>{validation.ready ? "المسودة متوافقة مع جدول المواصفات" : "المسودة تحتاج معالجة"}</strong><span>{validation.totalSelectedQuestions}/{validation.targetQuestions} أسئلة · {validation.totalSelectedMarks}/{validation.targetMarks} درجات</span></div>
              <div className="assessment-validation-grid">
                <span>معرفة: {validation.knowledgeSelected}/{validation.knowledgeTarget}</span>
                <span>تطبيق: {validation.applicationSelected}/{validation.applicationTarget}</span>
                <span>استدلال: {validation.reasoningSelected}/{validation.reasoningTarget}</span>
                <span>غير مصنف: {validation.unclassifiedSelected}</span>
              </div>
              {validation.issues.length ? <ul>{validation.issues.map((issue) => <li key={issue}>{issue}</li>)}</ul> : null}
              {shortages.length ? <ul className="assessment-shortages">{shortages.map((item) => <li key={item}>{item}</li>)}</ul> : null}
            </section>
          ) : null}

          <section className="assessment-builder-layout">
            <div className="assessment-candidates">
              <div className="assessment-section-heading"><div><span>بنك الأسئلة</span><h2>الأسئلة المرشحة</h2></div><strong>{bankItems.length}</strong></div>
              {bankItems.length ? bankItems.map((item) => {
                const question = item.questionSnapshot;
                const selected = selectedIds.has(item.id);
                return <article key={item.id}>
                  <div><strong>السؤال {question.originalNumber || "—"}</strong>
                    <span>{question.translatedText || question.originalText}</span>
                    <small>{categoryLabels[question.cognitiveCategory ?? "unclassified"]} · {question.marks ?? 0} درجة</small>
                  </div>
                  <button type="button" className="secondary-button compact"
                    disabled={selected || workingId === item.id}
                    onClick={() => void addItem(item)}>
                    {workingId === item.id ? <Loader2 size={15} className="spin-icon" /> : <Plus size={15} />}
                    {selected ? "مضاف" : "إضافة"}
                  </button>
                </article>;
              }) : <p className="assessment-empty">لا توجد أسئلة مطابقة لجدول المواصفات.</p>}
            </div>

            <div className="assessment-selected">
              <div className="assessment-section-manager">
                <div className="assessment-section-heading">
                  <div>
                    <span>بنية الاختبار</span>
                    <h2>الأقسام والترتيب والدرجات</h2>
                  </div>
                  <button
                    type="button"
                    className="secondary-button compact"
                    disabled={loading}
                    onClick={addSection}
                  >
                    <Plus size={15} />
                    إضافة قسم
                  </button>
                </div>
                <div className="assessment-section-list">
                  {detail.draft.sections.map((section) => (
                    <label key={section.id}>
                      <span>اسم القسم</span>
                      <input
                        value={section.title}
                        onChange={(event) =>
                          renameSection(
                            section.id,
                            event.target.value,
                          )
                        }
                        onBlur={() =>
                          void saveLayout(
                            detail.draft.sections,
                          )
                        }
                      />
                    </label>
                  ))}
                </div>
              </div>
              <div className="assessment-section-heading"><div><span>المسودة</span><h2>الأسئلة المختارة</h2></div><strong>{detail.questions.length}</strong></div>
              {detail.questions.length ? detail.questions.map((question, index) =>
                <article key={question.bankItemId} className="assessment-selected-item">
                  <div className="assessment-item-main">
                    <strong>{index + 1}. السؤال {question.questionNumber}</strong>
                    <span>{question.text}</span>
                    <small>
                      {categoryLabels[question.cognitiveCategory]}
                      {" · "}
                      {question.marks} درجة
                      {question.marksOverride !== null
                        ? ` (الأصل ${question.sourceMarks})`
                        : ""}
                    </small>
                  </div>
                  <div className="assessment-item-controls">
                    <label>
                      <span>القسم</span>
                      <select
                        value={question.sectionId ?? ""}
                        onChange={(event) =>
                          updateQuestionLayout(
                            question.bankItemId,
                            {
                              sectionId:
                                event.target.value || null,
                            },
                          )
                        }
                      >
                        <option value="">دون قسم</option>
                        {detail.draft.sections.map((section) => (
                          <option key={section.id} value={section.id}>
                            {section.title}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      <span>الدرجة</span>
                      <input
                        type="number"
                        min={0}
                        max={200}
                        value={
                          question.marksOverride ??
                          question.sourceMarks
                        }
                        onChange={(event) =>
                          updateQuestionLayout(
                            question.bankItemId,
                            {
                              marksOverride:
                                Number(event.target.value),
                            },
                          )
                        }
                      />
                    </label>
                    <div className="assessment-order-buttons">
                      <button
                        type="button"
                        className="secondary-button compact"
                        disabled={index === 0 || loading}
                        onClick={() =>
                          moveQuestion(
                            question.bankItemId,
                            -1,
                          )
                        }
                        aria-label="تحريك السؤال للأعلى"
                      >
                        <ArrowUp size={15} />
                      </button>
                      <button
                        type="button"
                        className="secondary-button compact"
                        disabled={
                          index === detail.questions.length - 1 ||
                          loading
                        }
                        onClick={() =>
                          moveQuestion(
                            question.bankItemId,
                            1,
                          )
                        }
                        aria-label="تحريك السؤال للأسفل"
                      >
                        <ArrowDown size={15} />
                      </button>
                    </div>
                    <button
                      type="button"
                      className="secondary-button compact"
                      disabled={workingId === question.bankItemId}
                      onClick={() =>
                        void removeItem(question.bankItemId)
                      }
                    >
                      {workingId === question.bankItemId
                        ? <Loader2 size={15} className="spin-icon" />
                        : <Trash2 size={15} />}
                      إزالة
                    </button>
                  </div>
                </article>) : <p className="assessment-empty">أضف أسئلة من البنك لبناء المسودة.</p>}
            </div>
          </section>
        </>
      ) : null}
    </main>
  );
}
