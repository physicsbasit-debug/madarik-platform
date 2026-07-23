import { useEffect, useMemo, useState } from "react";
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
  exportDifferentiatedActivity,
  generateDifferentiatedActivities,
  getDifferentiatedActivityPreview,
  listDifferentiatedActivities,
  searchQuestionBankLibrary,
} from "../../services/api";
import { localCurriculumRepository } from "../curriculum/local-curriculum.repository";
import { DifferentiatedActivityPreviewCard } from "./DifferentiatedActivityPreview";
import type {
  DifferentiatedActivity,
  DifferentiatedActivityPreview,
  DifferentiationLevel,
  QuestionBankItem,
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
  const grades = useMemo(
    () => localCurriculumRepository.listGrades(),
    [],
  );
  const [grade, setGrade] = useState(10);
  const subjects = useMemo(
    () => localCurriculumRepository.listSubjects(grade),
    [grade],
  );
  const [subjectId, setSubjectId] = useState("g10-physics");
  const subject =
    subjects.find((item) => item.id === subjectId) ??
    subjects[0];
  const semesters = useMemo(
    () => localCurriculumRepository.listSemesters(grade),
    [grade],
  );
  const [semesterId, setSemesterId] = useState("g10-sem2");
  const semester =
    semesters.find((item) => item.id === semesterId) ??
    semesters[0];
  const units = useMemo(
    () =>
      subject && semester
        ? localCurriculumRepository.listUnits(
            subject.id,
            semester.id,
          )
        : [],
    [subject, semester],
  );
  const [unitId, setUnitId] = useState<string | null>(
    "g10-physics-sem2-waves",
  );
  const lessons = useMemo(
    () =>
      unitId
        ? localCurriculumRepository.listLessons(unitId)
        : [],
    [unitId],
  );
  const [lessonId, setLessonId] =
    useState<string | null>(null);
  const outcomes = useMemo(
    () =>
      unitId
        ? localCurriculumRepository.listLearningOutcomes(
            unitId,
            lessonId ?? undefined,
          )
        : [],
    [unitId, lessonId],
  );

  const [items, setItems] =
    useState<DifferentiatedActivity[]>([]);
  const [bankItems, setBankItems] =
    useState<QuestionBankItem[]>([]);
  const [title, setTitle] = useState("");
  const [objective, setObjective] = useState("");
  const [instructions, setInstructions] = useState("");
  const [coreTask, setCoreTask] = useState("");
  const [successCriteriaText, setSuccessCriteriaText] =
    useState("");
  const [materialsText, setMaterialsText] = useState("");
  const [estimatedMinutes, setEstimatedMinutes] =
    useState(20);
  const [selectedBankItemId, setSelectedBankItemId] =
    useState<string | null>(null);
  const [level, setLevel] =
    useState<DifferentiationLevel>("core");
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [preview, setPreview] =
    useState<DifferentiatedActivityPreview | null>(null);

  useEffect(() => {
    const nextSubjects =
      localCurriculumRepository.listSubjects(grade);
    const nextSubject = nextSubjects[0];
    const nextSemesters =
      localCurriculumRepository.listSemesters(grade);
    const nextSemester = nextSemesters[0];
    setSubjectId(nextSubject?.id ?? "");
    setSemesterId(nextSemester?.id ?? "");
    const nextUnits =
      nextSubject && nextSemester
        ? localCurriculumRepository.listUnits(
            nextSubject.id,
            nextSemester.id,
          )
        : [];
    setUnitId(nextUnits[0]?.id ?? null);
    setLessonId(null);
  }, [grade]);

  useEffect(() => {
    if (!subject || !semester) return;
    const nextUnits = localCurriculumRepository.listUnits(
      subject.id,
      semester.id,
    );
    if (!nextUnits.some((unit) => unit.id === unitId)) {
      setUnitId(nextUnits[0]?.id ?? null);
      setLessonId(null);
    }
  }, [subject, semester, unitId]);

  useEffect(() => {
    void Promise.all([
      listDifferentiatedActivities(),
      searchQuestionBankLibrary({}),
    ])
      .then(([activities, bank]) => {
        setItems(activities);
        setBankItems(bank.items);
      })
      .catch(() => setError("تعذر تحميل الأنشطة."));
  }, []);

  function lines(value: string) {
    return value
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  function curriculumPayload() {
    if (!subject) {
      throw new Error("لا توجد مادة متاحة للصف المحدد.");
    }
    return {
      grade,
      scienceDomain: subject.scienceDomain,
      subjectId: subject.id,
      semesterId: semester?.id ?? null,
      unitId,
      lessonId,
      learningOutcomeIds: outcomes.map((item) => item.id),
    };
  }

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
        ...curriculumPayload(),
        level,
        objective: objective.trim(),
        instructions: instructions.trim(),
        successCriteria: lines(successCriteriaText),
        estimatedMinutes,
        materials: lines(materialsText),
      });
      setItems((current) => [created, ...current]);
      setMessage("تم حفظ النشاط.");
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : "تعذر حفظ النشاط.",
      );
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
        ...curriculumPayload(),
        objective: objective.trim(),
        coreTask: coreTask.trim(),
        estimatedMinutes,
        materials: lines(materialsText),
      });
      setItems((current) => [...result.items, ...current]);
      setMessage("تم إنشاء ثلاث نسخ: دعم، أساسي، وإثراء.");
    } catch (generationError) {
      setError(
        generationError instanceof Error
          ? generationError.message
          : "تعذر توليد الأنشطة.",
      );
    } finally {
      setWorking(false);
    }
  }

  async function openPreview(activityId: string) {
    setWorking(true);
    setError("");
    try {
      setPreview(
        await getDifferentiatedActivityPreview(activityId),
      );
    } catch {
      setError("تعذر تحميل معاينة النشاط.");
    } finally {
      setWorking(false);
    }
  }

  async function runExport(
    activityId: string,
    format: "docx" | "pdf",
  ) {
    setWorking(true);
    setError("");
    setMessage("");
    try {
      const result = await exportDifferentiatedActivity(
        activityId,
        format,
      );
      if (result.exportReady) {
        setMessage(
          `تم تنزيل ملف ${format.toUpperCase()}: ${result.filename}`,
        );
      } else {
        setError(result.issues.join(" "));
      }
    } catch {
      setError("تعذر تصدير النشاط.");
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
            <Layers3 size={18} /> الأنشطة المتمايزة
          </span>
          <h1>أنشطة علمية بمستويات دعم مختلفة</h1>
        </div>
        <button
          type="button"
          className="secondary-button"
          onClick={onReturnHome}
        >
          <ArrowRight size={18} /> العودة
        </button>
      </header>

      <section className="differentiated-form-card">
        <h2>إنشاء أو توليد نشاط</h2>
        <div className="differentiated-curriculum-grid">
          <label>
            الصف
            <select
              value={grade}
              onChange={(event) =>
                setGrade(Number(event.target.value))
              }
            >
              {grades.map((item) => (
                <option key={item} value={item}>
                  الصف {item}
                </option>
              ))}
            </select>
          </label>
          <label>
            المادة
            <select
              value={subject?.id ?? ""}
              onChange={(event) =>
                setSubjectId(event.target.value)
              }
            >
              {subjects.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.title}
                </option>
              ))}
            </select>
          </label>
          <label>
            الفصل
            <select
              value={semester?.id ?? ""}
              onChange={(event) =>
                setSemesterId(event.target.value)
              }
            >
              {semesters.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.title}
                </option>
              ))}
            </select>
          </label>
          <label>
            الوحدة
            <select
              value={unitId ?? ""}
              onChange={(event) => {
                setUnitId(event.target.value || null);
                setLessonId(null);
              }}
            >
              <option value="">دون وحدة</option>
              {units.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.title}
                </option>
              ))}
            </select>
          </label>
          <label>
            الدرس
            <select
              value={lessonId ?? ""}
              onChange={(event) =>
                setLessonId(event.target.value || null)
              }
            >
              <option value="">دون درس محدد</option>
              {lessons.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.title}
                </option>
              ))}
            </select>
          </label>
          <label>
            المدة
            <input
              type="number"
              min={5}
              max={180}
              value={estimatedMinutes}
              onChange={(event) =>
                setEstimatedMinutes(Number(event.target.value))
              }
            />
          </label>
        </div>

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
            onChange={(event) => setObjective(event.target.value)}
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
            onChange={(event) => setCoreTask(event.target.value)}
          />
          <textarea
            placeholder="معايير النجاح، معيار في كل سطر"
            value={successCriteriaText}
            onChange={(event) =>
              setSuccessCriteriaText(event.target.value)
            }
          />
          <textarea
            placeholder="الأدوات والمواد، عنصر في كل سطر"
            value={materialsText}
            onChange={(event) =>
              setMaterialsText(event.target.value)
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
            <Plus size={17} /> حفظ نشاط واحد
          </button>
        </div>
      </section>

      {message ? (
        <div className="differentiated-success">{message}</div>
      ) : null}
      {error ? (
        <div className="differentiated-error">{error}</div>
      ) : null}
      {preview ? (
        <DifferentiatedActivityPreviewCard
          preview={preview}
          onClose={() => setPreview(null)}
        />
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
              <div className="differentiated-card-actions">
                <button
                  type="button"
                  className="secondary-button compact"
                  disabled={working}
                  onClick={() => void openPreview(item.id)}
                >
                  معاينة
                </button>
                <button
                  type="button"
                  className="secondary-button compact"
                  disabled={working}
                  onClick={() => void runExport(item.id, "docx")}
                >
                  DOCX
                </button>
                <button
                  type="button"
                  className="secondary-button compact"
                  disabled={working}
                  onClick={() => void runExport(item.id, "pdf")}
                >
                  PDF
                </button>
                <button
                  type="button"
                  className="secondary-button compact"
                  disabled={working}
                  onClick={() => void remove(item.id)}
                >
                  <Trash2 size={15} /> حذف
                </button>
              </div>
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
