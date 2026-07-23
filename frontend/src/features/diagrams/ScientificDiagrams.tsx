import { useEffect, useMemo, useState } from "react";
import { ArrowRight, GitBranch, Plus, Trash2 } from "lucide-react";
import {
  createScientificDiagram,
  deleteScientificDiagram,
  exportScientificDiagramFile,
  exportScientificDiagramSvg,
  getScientificDiagramPreview,
  listScientificDiagrams,
} from "../../services/api";
import { localCurriculumRepository } from "../curriculum/local-curriculum.repository";
import { ScientificDiagramPreviewCard } from "./ScientificDiagramPreview";
import type {
  ScientificDiagram,
  ScientificDiagramNode,
  ScientificDiagramPreview,
  ScientificDiagramType,
} from "../../types/project";

interface Props {
  projectId: string | null;
  onReturnHome: () => void;
}

const typeLabels: Record<ScientificDiagramType, string> = {
  process: "مخطط عملية",
  cycle: "دورة",
  comparison: "مقارنة",
  sequence: "تسلسل",
  structure: "تركيب",
  cause_effect: "سبب ونتيجة",
};

export default function ScientificDiagrams({
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

  const [items, setItems] = useState<ScientificDiagram[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [diagramType, setDiagramType] =
    useState<ScientificDiagramType>("process");
  const [nodesText, setNodesText] = useState("");
  const [edgeLabelsText, setEdgeLabelsText] = useState("");
  const [error, setError] = useState("");
  const [preview, setPreview] =
    useState<ScientificDiagramPreview | null>(null);
  const [message, setMessage] = useState("");

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
    void listScientificDiagrams()
      .then(setItems)
      .catch(() => setError("تعذر تحميل الرسوم العلمية."));
  }, []);

  function buildNodes(): ScientificDiagramNode[] {
    return nodesText
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean)
      .map((label, index) => ({
        id: crypto.randomUUID(),
        label,
        description: null,
        orderIndex: index + 1,
      }));
  }

  async function save() {
    const nodes = buildNodes();
    if (!title.trim() || !nodes.length || !subject) {
      setError(
        "العنوان والمادة وعقدة واحدة على الأقل مطلوبة.",
      );
      return;
    }
    const edgeLabels = edgeLabelsText
      .split("\n")
      .map((item) => item.trim());
    try {
      const created = await createScientificDiagram({
        sourceProjectId: projectId,
        title: title.trim(),
        diagramType,
        grade,
        scienceDomain: subject.scienceDomain,
        subjectId: subject.id,
        semesterId: semester?.id ?? null,
        unitId,
        lessonId,
        learningOutcomeIds: outcomes.map((item) => item.id),
        description: description.trim() || null,
        nodes,
        edges: nodes.slice(1).map((node, index) => ({
          id: crypto.randomUUID(),
          sourceNodeId: nodes[index].id,
          targetNodeId: node.id,
          label: edgeLabels[index] || null,
          orderIndex: index + 1,
        })),
      });
      setItems((current) => [created, ...current]);
      setTitle("");
      setDescription("");
      setNodesText("");
      setEdgeLabelsText("");
      setError("");
    } catch {
      setError("تعذر حفظ الرسم العلمي.");
    }
  }

  async function openPreview(diagramId: string) {
    setError("");
    try {
      setPreview(await getScientificDiagramPreview(diagramId));
    } catch {
      setError("تعذر تحميل معاينة الرسم.");
    }
  }

  async function downloadSvg(diagramId: string) {
    setError("");
    setMessage("");
    try {
      const result = await exportScientificDiagramSvg(diagramId);
      if (!result.exportReady) {
        setError(result.issues.join(" "));
        return;
      }
      const blob = new Blob([result.svg], {
        type: "image/svg+xml;charset=utf-8",
      });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = result.filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      setMessage(`تم تنزيل الرسم: ${result.filename}`);
    } catch {
      setError("تعذر تنزيل SVG.");
    }
  }

  async function downloadBinary(
    diagramId: string,
    format: "png" | "pdf",
  ) {
    setError("");
    setMessage("");
    try {
      const result = await exportScientificDiagramFile(
        diagramId,
        format,
      );
      if (!result.exportReady) {
        setError(result.issues.join(" "));
        return;
      }
      setMessage(`تم تنزيل الرسم: ${result.filename}`);
    } catch {
      setError("تعذر تصدير الرسم.");
    }
  }

  async function remove(diagramId: string) {
    try {
      await deleteScientificDiagram(diagramId);
      setItems((current) =>
        current.filter((item) => item.id !== diagramId),
      );
    } catch {
      setError("تعذر حذف الرسم.");
    }
  }

  return (
    <main className="scientific-diagrams" dir="rtl">
      <header className="scientific-diagrams-header">
        <div>
          <span>
            <GitBranch size={18} /> الرسوم والمخططات العلمية
          </span>
          <h1>بناء مخططات علمية منظمة</h1>
          <p>أنشئ الرسم واربطه بالصف والمادة والوحدة والدرس.</p>
        </div>
        <button
          type="button"
          className="secondary-button"
          onClick={onReturnHome}
        >
          <ArrowRight size={18} /> العودة
        </button>
      </header>

      <section className="scientific-diagram-form">
        <h2>إنشاء رسم علمي</h2>
        <div className="scientific-diagram-curriculum-grid">
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
        </div>

        <div>
          <input
            placeholder="عنوان الرسم"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
          />
          <select
            value={diagramType}
            onChange={(event) =>
              setDiagramType(
                event.target.value as ScientificDiagramType,
              )
            }
          >
            {Object.entries(typeLabels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <textarea
            placeholder="وصف الرسم"
            value={description}
            onChange={(event) =>
              setDescription(event.target.value)
            }
          />
          <textarea
            placeholder="العقد، سطر لكل عنصر"
            value={nodesText}
            onChange={(event) => setNodesText(event.target.value)}
          />
          <textarea
            placeholder="تسميات الروابط، سطر لكل رابط"
            value={edgeLabelsText}
            onChange={(event) =>
              setEdgeLabelsText(event.target.value)
            }
          />
        </div>
        <button
          type="button"
          className="primary-button"
          onClick={() => void save()}
        >
          <Plus size={17} /> حفظ الرسم
        </button>
      </section>

      {error ? (
        <div className="scientific-diagram-error">{error}</div>
      ) : null}
      {message ? (
        <div className="scientific-diagram-message">{message}</div>
      ) : null}
      {preview ? (
        <ScientificDiagramPreviewCard
          preview={preview}
          onClose={() => setPreview(null)}
        />
      ) : null}

      <section className="scientific-diagram-list">
        <h2>الرسوم المحفوظة</h2>
        {items.map((item) => (
          <article key={item.id}>
            <div>
              <span>{typeLabels[item.diagramType]}</span>
              <h3>{item.title}</h3>
            </div>
            <p>{item.description}</p>
            <div className="scientific-diagram-node-row">
              {item.nodes.map((node) => (
                <span key={node.id}>{node.label}</span>
              ))}
            </div>
            <div className="scientific-diagram-actions">
              <button
                type="button"
                className="secondary-button compact"
                onClick={() => void openPreview(item.id)}
              >
                معاينة
              </button>
              <button
                type="button"
                className="secondary-button compact"
                onClick={() => void downloadSvg(item.id)}
              >
                تنزيل SVG
              </button>
              <button
                type="button"
                className="secondary-button compact"
                onClick={() => void downloadBinary(item.id, "png")}
              >
                تنزيل PNG
              </button>
              <button
                type="button"
                className="secondary-button compact"
                onClick={() => void downloadBinary(item.id, "pdf")}
              >
                تنزيل PDF
              </button>
              <button
                type="button"
                className="secondary-button compact"
                onClick={() => void remove(item.id)}
              >
                <Trash2 size={15} /> حذف
              </button>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}
