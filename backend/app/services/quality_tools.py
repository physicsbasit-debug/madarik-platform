from __future__ import annotations

from collections import Counter

from app.models.project import EducationalQualityToolsReport, ProjectSession, QuestionItem, QuestionStatus


def _active_questions(project: ProjectSession) -> list[QuestionItem]:
    return sorted(
        [question for question in project.questions if question.status != QuestionStatus.deleted],
        key=lambda question: question.order_index,
    )


def _classify_review_issue(question: QuestionItem) -> str:
    if not question.translated_text.strip():
        return "ترجمة غير مكتملة"
    if question.marks is None:
        return "درجة غير محددة"
    if question.status == QuestionStatus.needs_review:
        return "يحتاج مراجعة"
    if not question.review_notes and question.marks and question.marks >= 4:
        return "سؤال ممتد يحتاج تدقيق"
    return "جاهز مبدئيًا"


def _score(value: float, max_value: float) -> float:
    if max_value <= 0:
        return 0.0
    return round(max(0.0, min(100.0, (value / max_value) * 100)), 1)


def build_quality_tools_report(project: ProjectSession) -> EducationalQualityToolsReport:
    """Build foundational Pareto/Radar/Fishbone data for the assessment.

    This is not a final evaluation report. It is a structured quality lens for
    a teacher review workflow. Naturally the universe demanded Pareto charts
    before the PDFs learned manners, but here we are.
    """

    questions = _active_questions(project)
    question_count = len(questions)
    total_marks = sum(question.marks or 0 for question in questions)

    issue_counter = Counter(_classify_review_issue(question) for question in questions)
    pareto_items: list[dict[str, float | int | str]] = []
    running_total = 0
    issue_total = sum(count for label, count in issue_counter.items() if label != "جاهز مبدئيًا") or sum(issue_counter.values())

    for label, count in sorted(issue_counter.items(), key=lambda item: item[1], reverse=True):
        if label == "جاهز مبدئيًا" and len(issue_counter) > 1:
            continue
        running_total += count
        cumulative = round((running_total / max(issue_total, 1)) * 100, 1)
        pareto_items.append(
            {
                "label": label,
                "count": count,
                "cumulative_percent": cumulative,
            }
        )

    translated_count = sum(1 for question in questions if question.translated_text.strip())
    marked_count = sum(1 for question in questions if question.marks is not None)
    approved_count = sum(1 for question in questions if question.status == QuestionStatus.approved)
    answer_key_count = len(project.answer_key)
    layout_count = len(project.layout_assets)

    radar_axes = {
        "اكتمال الترجمة": _score(translated_count, question_count),
        "اكتمال الدرجات": _score(marked_count, question_count),
        "اعتماد المراجعة": _score(approved_count, question_count),
        "جاهزية نموذج الإجابة": _score(answer_key_count, question_count),
        "دعم الرسوم والتخطيط": 100.0 if layout_count else (50.0 if not project.uploaded_file else 0.0),
    }

    fishbone_causes: dict[str, list[str]] = {
        "الترجمة والمصطلحات": [],
        "الدرجات ونموذج الإجابة": [],
        "التخطيط والرسوم": [],
        "المراجعة والاعتماد": [],
    }

    if translated_count < question_count:
        fishbone_causes["الترجمة والمصطلحات"].append("بعض الأسئلة لا تحتوي ترجمة مكتملة.")
    if marked_count < question_count:
        fishbone_causes["الدرجات ونموذج الإجابة"].append("بعض الأسئلة بلا درجات محددة.")
    if answer_key_count < question_count:
        fishbone_causes["الدرجات ونموذج الإجابة"].append("مسودة نموذج الإجابة غير مكتملة أو غير مولدة.")
    if project.uploaded_file and project.uploaded_file.name.lower().endswith(".pdf") and not layout_count:
        fishbone_causes["التخطيط والرسوم"].append("لا توجد لقطات تخطيط PDF لمراجعة الرسوم والجداول.")
    if approved_count < question_count:
        fishbone_causes["المراجعة والاعتماد"].append("توجد أسئلة لم تعتمد بعد بعد المراجعة.")

    fishbone_causes = {
        category: causes or ["لا توجد ملاحظة ظاهرة في هذا المحور."]
        for category, causes in fishbone_causes.items()
    }

    priority_actions: list[str] = []
    if translated_count < question_count:
        priority_actions.append("استكمال ترجمة الأسئلة غير المترجمة قبل التصدير النهائي.")
    if marked_count < question_count:
        priority_actions.append("مراجعة الدرجات الناقصة وربطها بمجموع الورقة.")
    if answer_key_count < question_count:
        priority_actions.append("توليد أو تحديث مسودة نموذج الإجابة ثم مراجعتها يدويًا.")
    if approved_count < question_count:
        priority_actions.append("اعتماد الأسئلة بعد مراجعة الترجمة والدرجة ونص السؤال.")
    if not priority_actions:
        priority_actions.append("تنفيذ مراجعة بشرية نهائية للتأكد من سلامة الورقة قبل الطباعة.")

    warnings: list[str] = []
    if question_count == 0:
        warnings.append("لا توجد أسئلة نشطة لبناء أدوات الجودة.")
    if total_marks == 0 and question_count:
        warnings.append("مجموع الدرجات صفر أو غير محدد.")
    if len(pareto_items) == 0:
        warnings.append("لا توجد بيانات كافية لبناء قراءة باريتو.")

    quality_summary = (
        f"تقرأ أدوات الجودة {question_count} سؤالًا نشطًا بإجمالي {total_marks} درجة. "
        "تعرض القراءة Pareto لأولويات المراجعة، ومحاور Radar لجاهزية الورقة، وFishbone لأسباب الضعف المحتملة. "
        "هذه أدوات مساعدة لا حكم نهائي، حتى لا نرتكب مسرحية اليقين الزائف المعتادة."
    )

    return EducationalQualityToolsReport(
        pareto_items=pareto_items,
        radar_axes=radar_axes,
        fishbone_causes=fishbone_causes,
        quality_summary=quality_summary,
        priority_actions=priority_actions,
        warnings=warnings,
        needs_review=True,
    )
