import type {
  CurriculumCatalog,
  CurriculumLearningOutcome,
  CurriculumLesson,
  CurriculumSemester,
  CurriculumSubject,
  CurriculumUnit,
  ScienceDomain,
} from "../../types/project";

const grades = Array.from({ length: 12 }, (_, index) => index + 1);

const semesters: CurriculumSemester[] = grades.flatMap((grade) => [
  {
    id: `g${grade}-sem1`,
    grade,
    number: 1,
    title: "الفصل الدراسي الأول",
  },
  {
    id: `g${grade}-sem2`,
    grade,
    number: 2,
    title: "الفصل الدراسي الثاني",
  },
]);

function scienceDomainForGrade(grade: number): ScienceDomain {
  return grade <= 8 ? "general_science" : "physics";
}

function subjectTitleForGrade(grade: number): string {
  return grade <= 8 ? "العلوم" : "الفيزياء";
}

const subjects: CurriculumSubject[] = grades.map((grade) => ({
  id: `g${grade}-${scienceDomainForGrade(grade)}`,
  grade,
  scienceDomain: scienceDomainForGrade(grade),
  title: subjectTitleForGrade(grade),
  shortTitle: subjectTitleForGrade(grade),
}));

const units: CurriculumUnit[] = [
  {
    id: "g1-science-sem1-living-things",
    subjectId: "g1-general_science",
    semesterId: "g1-sem1",
    title: "الكائنات الحية وبيئاتها",
    order: 1,
    description: "وحدة تأسيسية نموذجية قابلة للاستبدال ببيانات المنهج المعتمد.",
  },
  {
    id: "g5-science-sem1-matter",
    subjectId: "g5-general_science",
    semesterId: "g5-sem1",
    title: "المادة وتغيراتها",
    order: 1,
    description: "وحدة نموذجية لبنية الصف والوحدة والدرس ونواتج التعلم.",
  },
  {
    id: "g10-physics-sem2-waves",
    subjectId: "g10-physics",
    semesterId: "g10-sem2",
    title: "الموجات",
    order: 1,
    description: "وحدة نموذجية للمرحلة الثانوية.",
  },
];

const lessons: CurriculumLesson[] = [
  {
    id: "g1-living-things-needs",
    unitId: "g1-science-sem1-living-things",
    title: "احتياجات الكائنات الحية",
    order: 1,
    learningOutcomeIds: ["g1-lo-living-needs-1"],
  },
  {
    id: "g5-matter-properties",
    unitId: "g5-science-sem1-matter",
    title: "خصائص المادة",
    order: 1,
    learningOutcomeIds: ["g5-lo-matter-properties-1"],
  },
  {
    id: "g10-waves-properties",
    unitId: "g10-physics-sem2-waves",
    title: "خصائص الموجات",
    order: 1,
    learningOutcomeIds: ["g10-lo-waves-properties-1"],
  },
  {
    id: "g10-waves-equation",
    unitId: "g10-physics-sem2-waves",
    title: "العلاقة بين السرعة والتردد والطول الموجي",
    order: 2,
    learningOutcomeIds: ["g10-lo-wave-equation-1"],
  },
];

const learningOutcomes: CurriculumLearningOutcome[] = [
  {
    id: "g1-lo-living-needs-1",
    grade: 1,
    scienceDomain: "general_science",
    unitId: "g1-science-sem1-living-things",
    lessonId: "g1-living-things-needs",
    code: "G1-SCI-LO-001",
    text: "يحدد الاحتياجات الأساسية للكائنات الحية.",
  },
  {
    id: "g5-lo-matter-properties-1",
    grade: 5,
    scienceDomain: "general_science",
    unitId: "g5-science-sem1-matter",
    lessonId: "g5-matter-properties",
    code: "G5-SCI-LO-001",
    text: "يقارن بين المواد وفق خصائصها الفيزيائية.",
  },
  {
    id: "g10-lo-waves-properties-1",
    grade: 10,
    scienceDomain: "physics",
    unitId: "g10-physics-sem2-waves",
    lessonId: "g10-waves-properties",
    code: "G10-PHY-LO-001",
    text: "يصف السعة والتردد والطول الموجي والزمن الدوري.",
  },
  {
    id: "g10-lo-wave-equation-1",
    grade: 10,
    scienceDomain: "physics",
    unitId: "g10-physics-sem2-waves",
    lessonId: "g10-waves-equation",
    code: "G10-PHY-LO-002",
    text: "يستخدم العلاقة بين سرعة الموجة وترددها وطولها الموجي.",
  },
];

export const scienceCurriculumCatalog: CurriculumCatalog = {
  grades,
  semesters,
  subjects,
  units,
  lessons,
  learningOutcomes,
};
