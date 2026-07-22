import type {
  AssessmentStudentPaperPreview,
} from "../../types/project";

interface AssessmentStudentPreviewProps {
  preview: AssessmentStudentPaperPreview;
}

export function AssessmentStudentPreview({
  preview,
}: AssessmentStudentPreviewProps) {
  return (
    <section className="assessment-student-preview">
      <header>
        <div>
          <span>معاينة ورقة الطالب</span>
          <h2>{preview.title}</h2>
        </div>
        <div className="assessment-paper-meta">
          <span>الصف {preview.grade}</span>
          <span>
            {preview.durationMinutes} دقيقة
          </span>
          <span>
            {preview.totalMarks} درجة
          </span>
        </div>
      </header>

      {preview.sections.map((section) => (
        <section
          key={section.id}
          className="assessment-paper-section"
        >
          <h3>{section.title}</h3>
          {section.instructions ? (
            <p>{section.instructions}</p>
          ) : null}

          {section.questions.map((question) => (
            <article key={question.bankItemId}>
              <span className="assessment-question-number">
                {question.number}.
              </span>
              <div>
                <p>{question.text}</p>
                <div className="assessment-answer-lines">
                  <span />
                  <span />
                </div>
              </div>
              <strong>
                {question.marks} درجات
              </strong>
            </article>
          ))}
        </section>
      ))}

      <section className="assessment-answer-sheet-preview">
        <h3>صفحة الإجابة</h3>
        {preview.sections.flatMap(
          (section) => section.questions,
        ).map((question) => (
          <div key={question.bankItemId}>
            <span>{question.number}.</span>
            <span />
          </div>
        ))}
      </section>
    </section>
  );
}
