import { BookOpenCheck, Link2, Unlink } from "lucide-react";
import { useMemo } from "react";
import { localCurriculumRepository } from "../curriculum/local-curriculum.repository";
import type { QuestionItem } from "../../types/project";

interface QuestionCurriculumLinkCardProps {
  question: QuestionItem;
  disabled?: boolean;
  onUpdateQuestion: (
    questionId: string,
    updates: Partial<QuestionItem>,
  ) => void;
}

export function QuestionCurriculumLinkCard({
  question,
  disabled = false,
  onUpdateQuestion,
}: QuestionCurriculumLinkCardProps) {
  const grades = useMemo(
    () => localCurriculumRepository.listGrades(),
    [],
  );

  const grade = question.curriculumGrade ?? 10;
  const semesters =
    localCurriculumRepository.listSemesters(grade);
  const subjects =
    localCurriculumRepository.listSubjects(grade);

  const semesterId =
    question.curriculumSemesterId ??
    semesters[0]?.id ??
    "";
  const subjectId =
    question.curriculumSubjectId ??
    subjects[0]?.id ??
    "";
  const subject =
    subjects.find((item) => item.id === subjectId) ??
    subjects[0] ??
    null;

  const units =
    subject && semesterId
      ? localCurriculumRepository.listUnits(
          subject.id,
          semesterId,
        )
      : [];
  const unitId =
    question.curriculumUnitId ?? units[0]?.id ?? "";
  const lessons = unitId
    ? localCurriculumRepository.listLessons(unitId)
    : [];
  const lessonId =
    question.curriculumLessonId ??
    lessons[0]?.id ??
    "";
  const outcomes = unitId
    ? localCurriculumRepository.listLearningOutcomes(
        unitId,
        lessonId || undefined,
      )
    : [];
  const selectedOutcomeIds =
    question.curriculumLearningOutcomeIds ?? [];

  function update(
    updates: Partial<QuestionItem>,
  ) {
    onUpdateQuestion(question.id, {
      ...updates,
      curriculumLinkSource: "manual",
    });
  }

  function changeGrade(nextGrade: number) {
    const nextSemesters =
      localCurriculumRepository.listSemesters(
        nextGrade,
      );
    const nextSubjects =
      localCurriculumRepository.listSubjects(
        nextGrade,
      );
    const nextSubject = nextSubjects[0] ?? null;

    update({
      curriculumGrade: nextGrade,
      curriculumScienceDomain:
        nextSubject?.scienceDomain ?? null,
      curriculumSemesterId:
        nextSemesters[0]?.id ?? null,
      curriculumSubjectId:
        nextSubject?.id ?? null,
      curriculumUnitId: null,
      curriculumLessonId: null,
      curriculumLearningOutcomeIds: [],
    });
  }

  function changeSemester(nextSemesterId: string) {
    update({
      curriculumSemesterId: nextSemesterId,
      curriculumUnitId: null,
      curriculumLessonId: null,
      curriculumLearningOutcomeIds: [],
    });
  }

  function changeSubject(nextSubjectId: string) {
    const nextSubject =
      subjects.find(
        (item) => item.id === nextSubjectId,
      ) ?? null;

    update({
      curriculumSubjectId: nextSubjectId,
      curriculumScienceDomain:
        nextSubject?.scienceDomain ?? null,
      curriculumUnitId: null,
      curriculumLessonId: null,
      curriculumLearningOutcomeIds: [],
    });
  }

  function changeUnit(nextUnitId: string) {
    update({
      curriculumUnitId: nextUnitId || null,
      curriculumLessonId: null,
      curriculumLearningOutcomeIds: [],
    });
  }

  function changeLesson(nextLessonId: string) {
    update({
      curriculumLessonId: nextLessonId || null,
      curriculumLearningOutcomeIds: [],
    });
  }

  function toggleOutcome(outcomeId: string) {
    const next = selectedOutcomeIds.includes(
      outcomeId,
    )
      ? selectedOutcomeIds.filter(
          (item) => item !== outcomeId,
        )
      : [...selectedOutcomeIds, outcomeId];

    update({
      curriculumLearningOutcomeIds: next,
    });
  }

  function clearLink() {
    update({
      curriculumGrade: null,
      curriculumScienceDomain: null,
      curriculumSemesterId: null,
      curriculumSubjectId: null,
      curriculumUnitId: null,
      curriculumLessonId: null,
      curriculumLearningOutcomeIds: [],
    });
  }

  const linked = Boolean(
    question.curriculumGrade &&
      question.curriculumSubjectId &&
      question.curriculumSemesterId,
  );

  return (
    <section className="question-curriculum-link-card">
      <div className="question-curriculum-link-heading">
        <BookOpenCheck size={21} />
        <div>
          <span>الارتباط المنهجي</span>
          <h3>
            {linked
              ? "مرتبط بالمنهج"
              : "غير مرتبط"}
          </h3>
        </div>
        <span
          className={
            linked
              ? "curriculum-link-badge is-linked"
              : "curriculum-link-badge"
          }
        >
          {linked ? "مرتبط" : "غير مرتبط"}
        </span>
      </div>

      <div className="curriculum-link-grid">
        <label>
          <span>الصف</span>
          <select
            value={grade}
            disabled={disabled}
            onChange={(event) =>
              changeGrade(
                Number(event.target.value),
              )
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
          <span>الفصل</span>
          <select
            value={semesterId}
            disabled={disabled}
            onChange={(event) =>
              changeSemester(event.target.value)
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
          <span>المادة</span>
          <select
            value={subjectId}
            disabled={disabled}
            onChange={(event) =>
              changeSubject(event.target.value)
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
          <span>الوحدة</span>
          <select
            value={unitId}
            disabled={disabled}
            onChange={(event) =>
              changeUnit(event.target.value)
            }
          >
            <option value="">غير محددة</option>
            {units.map((item) => (
              <option key={item.id} value={item.id}>
                {item.title}
              </option>
            ))}
          </select>
        </label>

        <label className="curriculum-link-wide">
          <span>الدرس</span>
          <select
            value={lessonId}
            disabled={disabled || !unitId}
            onChange={(event) =>
              changeLesson(event.target.value)
            }
          >
            <option value="">غير محدد</option>
            {lessons.map((item) => (
              <option key={item.id} value={item.id}>
                {item.title}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="curriculum-outcome-selector">
        <strong>نواتج التعلم</strong>
        {outcomes.length > 0 ? (
          outcomes.map((outcome) => (
            <label key={outcome.id}>
              <input
                type="checkbox"
                disabled={disabled}
                checked={selectedOutcomeIds.includes(
                  outcome.id,
                )}
                onChange={() =>
                  toggleOutcome(outcome.id)
                }
              />
              <span>
                <code>{outcome.code}</code>
                {outcome.text}
              </span>
            </label>
          ))
        ) : (
          <p>
            لا توجد نواتج تعلم نموذجية لهذا
            الاختيار حتى الآن.
          </p>
        )}
      </div>

      <div className="curriculum-link-actions">
        <div>
          <Link2 size={17} />
          <span>
            المصدر: ربط يدوي قابل للمراجعة
          </span>
        </div>
        <button
          type="button"
          className="secondary-button compact"
          disabled={disabled || !linked}
          onClick={clearLink}
        >
          <Unlink size={16} />
          فك الارتباط
        </button>
      </div>
    </section>
  );
}
