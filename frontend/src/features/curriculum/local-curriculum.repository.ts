import { scienceCurriculumCatalog } from "../../content/seed/science-curriculum.seed";
import type {
  CurriculumLearningOutcome,
  CurriculumLesson,
  CurriculumSemester,
  CurriculumSubject,
  CurriculumUnit,
} from "../../types/project";

export type CurriculumRepository = {
  listGrades(): number[];
  listSemesters(grade: number): CurriculumSemester[];
  listSubjects(grade: number): CurriculumSubject[];
  listUnits(subjectId: string, semesterId: string): CurriculumUnit[];
  listLessons(unitId: string): CurriculumLesson[];
  listLearningOutcomes(
    unitId: string,
    lessonId?: string,
  ): CurriculumLearningOutcome[];
};

export const localCurriculumRepository: CurriculumRepository = {
  listGrades() {
    return [...scienceCurriculumCatalog.grades];
  },

  listSemesters(grade) {
    return scienceCurriculumCatalog.semesters.filter(
      (semester) => semester.grade === grade,
    );
  },

  listSubjects(grade) {
    return scienceCurriculumCatalog.subjects.filter(
      (subject) => subject.grade === grade,
    );
  },

  listUnits(subjectId, semesterId) {
    return scienceCurriculumCatalog.units
      .filter(
        (unit) =>
          unit.subjectId === subjectId &&
          unit.semesterId === semesterId,
      )
      .sort((left, right) => left.order - right.order);
  },

  listLessons(unitId) {
    return scienceCurriculumCatalog.lessons
      .filter((lesson) => lesson.unitId === unitId)
      .sort((left, right) => left.order - right.order);
  },

  listLearningOutcomes(unitId, lessonId) {
    return scienceCurriculumCatalog.learningOutcomes.filter(
      (outcome) =>
        outcome.unitId === unitId &&
        (!lessonId || outcome.lessonId === lessonId),
    );
  },
};
