import { useMemo, useState } from "react";
import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  ChevronLeft,
  FlaskConical,
  GraduationCap,
  LibraryBig,
  ListTree,
} from "lucide-react";
import { localCurriculumRepository } from "./local-curriculum.repository";
import GoogleDriveSourcePanel from "./GoogleDriveSourcePanel";

type CurriculumBrowserProps = {
  projectId: string | null;
  onReturnHome: () => void;
};

export default function CurriculumBrowser({
  projectId,
  onReturnHome,
}: CurriculumBrowserProps) {
  const grades = useMemo(
    () => localCurriculumRepository.listGrades(),
    [],
  );
  const [grade, setGrade] = useState(10);
  const semesters = localCurriculumRepository.listSemesters(grade);
  const [semesterNumber, setSemesterNumber] = useState<1 | 2>(2);
  const semester =
    semesters.find((item) => item.number === semesterNumber) ??
    semesters[0];
  const subjects = localCurriculumRepository.listSubjects(grade);
  const subject = subjects[0] ?? null;
  const units =
    subject && semester
      ? localCurriculumRepository.listUnits(subject.id, semester.id)
      : [];
  const [selectedUnitId, setSelectedUnitId] = useState<string | null>(
    null,
  );
  const activeUnit =
    units.find((unit) => unit.id === selectedUnitId) ?? units[0] ?? null;
  const lessons = activeUnit
    ? localCurriculumRepository.listLessons(activeUnit.id)
    : [];

  return (
    <main className="curriculum-browser" dir="rtl">
      <header className="curriculum-browser-header">
        <div>
          <span>
            <LibraryBig size={18} />
            مكتبة المناهج
          </span>
          <h1>هيكل مناهج العلوم من الصف 1 إلى 12</h1>
          <p>
            استعرض الصف والفصل والمادة والوحدة والدروس ونواتج التعلم.
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

      <section className="curriculum-browser-grid">
        <aside className="curriculum-filter-card">
          <div className="curriculum-card-title">
            <GraduationCap size={22} />
            <h2>اختيار المنهج</h2>
          </div>

          <label>
            <span>الصف</span>
            <select
              value={grade}
              onChange={(event) => {
                setGrade(Number(event.target.value));
                setSelectedUnitId(null);
              }}
            >
              {grades.map((item) => (
                <option value={item} key={item}>
                  الصف {item}
                </option>
              ))}
            </select>
          </label>

          <div className="curriculum-semester-switch">
            {([1, 2] as const).map((number) => (
              <button
                type="button"
                key={number}
                className={
                  semesterNumber === number ? "is-active" : undefined
                }
                onClick={() => {
                  setSemesterNumber(number);
                  setSelectedUnitId(null);
                }}
              >
                الفصل {number === 1 ? "الأول" : "الثاني"}
              </button>
            ))}
          </div>

          <div className="curriculum-subject-summary">
            <FlaskConical size={22} />
            <div>
              <span>المادة</span>
              <strong>{subject?.title ?? "لا توجد مادة"}</strong>
            </div>
          </div>

          <div className="curriculum-seed-note">
            البيانات الحالية نموذج بنيوي. المحتوى الرسمي سيُستورد
            لاحقًا من ملفات المنهج المعتمدة.
          </div>
        </aside>

        <section className="curriculum-content-card">
          <div className="curriculum-card-title">
            <ListTree size={22} />
            <div>
              <span>{semester?.title}</span>
              <h2>الوحدات والدروس</h2>
            </div>
          </div>

          {units.length > 0 ? (
            <div className="curriculum-unit-layout">
              <nav className="curriculum-unit-list">
                {units.map((unit) => (
                  <button
                    type="button"
                    key={unit.id}
                    className={
                      activeUnit?.id === unit.id ? "is-active" : undefined
                    }
                    onClick={() => setSelectedUnitId(unit.id)}
                  >
                    <span>الوحدة {unit.order}</span>
                    <strong>{unit.title}</strong>
                    <ChevronLeft size={18} />
                  </button>
                ))}
              </nav>

              <div className="curriculum-unit-detail">
                <div className="curriculum-unit-heading">
                  <BookOpen size={24} />
                  <div>
                    <span>الوحدة {activeUnit?.order}</span>
                    <h3>{activeUnit?.title}</h3>
                    {activeUnit?.description ? (
                      <p>{activeUnit.description}</p>
                    ) : null}
                  </div>
                </div>

                <div className="curriculum-lessons-list">
                  {lessons.map((lesson) => {
                    const outcomes =
                      localCurriculumRepository.listLearningOutcomes(
                        lesson.unitId,
                        lesson.id,
                      );

                    return (
                      <article key={lesson.id}>
                        <div className="curriculum-lesson-heading">
                          <span>الدرس {lesson.order}</span>
                          <h4>{lesson.title}</h4>
                        </div>
                        <div className="curriculum-outcomes-list">
                          {outcomes.map((outcome) => (
                            <div key={outcome.id}>
                              <CheckCircle2 size={17} />
                              <div>
                                <code>{outcome.code}</code>
                                <p>{outcome.text}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </article>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : (
            <div className="curriculum-empty-state">
              لا توجد وحدات نموذجية لهذا الصف والفصل حتى الآن.
            </div>
          )}
        </section>
      </section>

      <GoogleDriveSourcePanel
        projectId={projectId}
        grade={grade}
        scienceDomain={
          subject?.scienceDomain ?? "general_science"
        }
        semesterId={semester?.id ?? ""}
        subjectId={subject?.id ?? ""}
        unitId={activeUnit?.id ?? null}
      />
    </main>
  );
}