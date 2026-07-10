from app.models.project import GlossaryTerm, QuestionItem


def get_demo_questions() -> list[QuestionItem]:
    """Return stable Phase 1-B demo questions from the backend.

    These are deliberately static. Real extraction, OCR, and translation are deferred.
    """

    return [
        QuestionItem(
            id="q-1",
            original_number="1",
            original_text="State the function of the cell membrane. [1]",
            translated_text="اذكر وظيفة غشاء الخلية. [1]",
            marks=1,
            detected_marks=1,
            status="approved",
            order_index=1,
            attachment_note="لا توجد صورة مرتبطة بهذا السؤال.",
        ),
        QuestionItem(
            id="q-2",
            original_number="2",
            original_text="Explain why the current decreases when the resistance increases. [2]",
            translated_text="فسّر لماذا تقل شدة التيار عندما تزداد المقاومة. [2]",
            marks=2,
            detected_marks=2,
            status="needs_review",
            order_index=2,
            attachment_note="رسم دائرة كهربائية تجريبي سيُحفظ كصورة في المراحل اللاحقة.",
            review_notes="تحقق لاحقًا من ارتباط السؤال بالرسم عند تفعيل استخراج الصور.",
        ),
        QuestionItem(
            id="q-3",
            original_number="3",
            original_text="Calculate the speed of a wave with frequency 50 Hz and wavelength 0.40 m. [2]",
            translated_text="احسب سرعة موجة ترددها 50 Hz وطولها الموجي 0.40 m. [2]",
            marks=2,
            detected_marks=2,
            status="approved",
            order_index=3,
            attachment_note="المعادلات والوحدات تُترك كما هي في Phase 1-B.",
        ),
        QuestionItem(
            id="q-4",
            original_number="4",
            original_text="Describe how the rate of reaction changes when the temperature is increased. [3]",
            translated_text="صف كيف يتغير معدل التفاعل عند زيادة درجة الحرارة. [3]",
            marks=3,
            detected_marks=3,
            status="approved",
            order_index=4,
            attachment_note="جدول نتائج تجريبي سيُربط بالسؤال في مرحلة استخراج الملفات الحقيقية.",
        ),
    ]


def get_demo_glossary() -> list[GlossaryTerm]:
    """Return stable Phase 1-B demo glossary terms from the backend."""

    return [
        GlossaryTerm(
            id="t-1",
            english_term="cell membrane",
            arabic_term="غشاء الخلية",
            subject="أحياء",
            status="approved",
            source="mock",
        ),
        GlossaryTerm(
            id="t-2",
            english_term="current",
            arabic_term="شدة التيار",
            subject="فيزياء",
            status="approved",
            source="mock",
        ),
        GlossaryTerm(
            id="t-3",
            english_term="resistance",
            arabic_term="المقاومة",
            subject="فيزياء",
            status="approved",
            source="mock",
        ),
        GlossaryTerm(
            id="t-4",
            english_term="rate of reaction",
            arabic_term="معدل التفاعل",
            subject="كيمياء",
            status="needs_review",
            source="mock",
            notes="مصطلح قابل للمراجعة حسب سياق المنهج.",
        ),
    ]
