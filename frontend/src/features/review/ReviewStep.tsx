import type { VisualCropRequest } from "../../types/project";
import { useState } from "react";
import { VisualCropDialog } from "./VisualCropDialog";
import {
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  CheckCircle2,
  Crop,
  ImagePlus,
  Languages,
  Link2,
  Plus,
  RotateCcw,
  Trash2,
  Unlink,
  X,
} from "lucide-react";
import type { ChangeEvent, CSSProperties } from "react";
import type {
  PdfLayoutAssetInfo,
  QuestionItem,
  QuestionPart,
  QuestionStatus,
  TranslationProviderStatus,
  TranslationBatchSummary,
} from "../../types/project";

interface ReviewStepProps {
  questions: QuestionItem[];
  layoutAssets: PdfLayoutAssetInfo[];
  onUpdateQuestion: (
    questionId: string,
    updates: Partial<QuestionItem>,
  ) => void;
  onMoveQuestion: (questionId: string, direction: "up" | "down") => void;
  onTranslateQuestions: () => void;
  onBulkUpdateStatus: (
    status: QuestionStatus,
    includeDeleted?: boolean,
  ) => void;
  onUploadQuestionAsset: (questionId: string, file: File) => void;
  onDeleteQuestionAsset: (questionId: string, assetId: string) => void;
  onLinkLayoutAsset: (questionId: string, assetId: string) => void;
  onUnlinkLayoutAsset: (questionId: string, assetId: string) => void;
  onCropLayoutAsset: (
    questionId: string,
    assetId: string,
    crop: VisualCropRequest,
  ) => Promise<void>;
  translationProviderStatus: TranslationProviderStatus | null;
  translationBatchSummary?: TranslationBatchSummary | null;
}

const statusLabels: Record<QuestionStatus, string> = {
  approved: "معتمد",
  needs_review: "يحتاج مراجعة",
  deleted: "محذوف",
};

function formatFileSize(size: number) {
  if (size < 1024) return `${size} بايت`;
  if (size < 1024 * 1024) return `${Math.round(size / 1024)} ك.ب`;
  return `${(size / (1024 * 1024)).toFixed(1)} م.ب`;
}

function formatProviderApiMode(apiMode?: string) {
  if (apiMode === "responses") return "Responses API";
  if (apiMode === "generate_content") return "Gemini generateContent";
  if (apiMode === "chat_completions") return "Chat Completions";
  return apiMode ?? "";
}

function formatTranslationBatchStatus(
  status: TranslationBatchSummary["status"],
) {
  if (status === "completed") return "اكتملت دون fallback";
  if (status === "completed_with_fallbacks") return "اكتملت مع fallback محلي";
  return "اكتملت مع عناصر تحتاج مراجعة عاجلة";
}

function sortQuestionParts(parts: QuestionPart[] | undefined) {
  return [...(parts ?? [])].sort((a, b) => a.orderIndex - b.orderIndex);
}

function normalizeQuestionPartHierarchy(parts: QuestionPart[]) {
  const sortedParts = sortQuestionParts(parts);
  const partIds = new Set(sortedParts.map((part) => part.id));
  const sanitizedParts = sortedParts.map((part) => ({
    ...part,
    parentId:
      part.parentId &&
      part.parentId !== part.id &&
      partIds.has(part.parentId)
        ? part.parentId
        : null,
  }));
  const partsByParent = new Map<string | null, QuestionPart[]>();

  for (const part of sanitizedParts) {
    const parentId = part.parentId ?? null;
    const siblings = partsByParent.get(parentId) ?? [];
    siblings.push(part);
    partsByParent.set(parentId, siblings);
  }

  const orderedParts: QuestionPart[] = [];
  const visited = new Set<string>();

  function visit(part: QuestionPart, activePath: Set<string>) {
    if (visited.has(part.id)) return;

    if (activePath.has(part.id)) {
      orderedParts.push({ ...part, parentId: null });
      visited.add(part.id);
      return;
    }

    orderedParts.push(part);
    visited.add(part.id);

    const nextPath = new Set(activePath);
    nextPath.add(part.id);

    for (const child of partsByParent.get(part.id) ?? []) {
      visit(child, nextPath);
    }
  }

  for (const rootPart of partsByParent.get(null) ?? []) {
    visit(rootPart, new Set());
  }

  for (const orphanPart of sanitizedParts) {
    if (!visited.has(orphanPart.id)) {
      visit({ ...orphanPart, parentId: null }, new Set());
    }
  }

  return orderedParts.map((part, index) => ({
    ...part,
    orderIndex: index + 1,
  }));
}

function getQuestionPartDepth(part: QuestionPart, parts: QuestionPart[]) {
  const partsById = new Map(parts.map((item) => [item.id, item]));
  const visited = new Set([part.id]);
  let depth = 0;
  let current = part;

  while (current.parentId) {
    const parent = partsById.get(current.parentId);

    if (!parent || visited.has(parent.id)) break;

    visited.add(parent.id);
    depth += 1;
    current = parent;
  }

  return depth;
}

function getQuestionPartSiblings(part: QuestionPart, parts: QuestionPart[]) {
  return parts.filter(
    (candidate) => (candidate.parentId ?? null) === (part.parentId ?? null),
  );
}

function getQuestionPartsTotalMarks(parts: QuestionPart[]) {
  if (parts.length === 0) return null;

  const partsById = new Map(parts.map((part) => [part.id, part]));
  const childrenByParent = new Map<string, QuestionPart[]>();

  for (const part of parts) {
    if (!part.parentId || !partsById.has(part.parentId)) continue;
    const children = childrenByParent.get(part.parentId) ?? [];
    children.push(part);
    childrenByParent.set(part.parentId, children);
  }

  const roots = parts.filter(
    (part) => !part.parentId || !partsById.has(part.parentId),
  );

  function getBranchMarks(
    part: QuestionPart,
    visited: Set<string>,
  ): number | null {
    if (visited.has(part.id)) return part.marks;

    const nextVisited = new Set(visited);
    nextVisited.add(part.id);

    const childMarks = (childrenByParent.get(part.id) ?? [])
      .map((child) => getBranchMarks(child, nextVisited))
      .filter((value): value is number => value !== null);

    if (childMarks.length > 0) {
      return childMarks.reduce((sum, value) => sum + value, 0);
    }

    return part.marks;
  }

  const rootMarks = roots
    .map((part) => getBranchMarks(part, new Set()))
    .filter((value): value is number => value !== null);

  return rootMarks.length > 0
    ? rootMarks.reduce((sum, value) => sum + value, 0)
    : null;
}

function canMoveQuestionPart(
  part: QuestionPart,
  parts: QuestionPart[],
  direction: "up" | "down",
) {
  const siblings = getQuestionPartSiblings(part, parts);
  const index = siblings.findIndex((candidate) => candidate.id === part.id);

  if (direction === "up") return index > 0;
  return index >= 0 && index < siblings.length - 1;
}

const childPartLabels = [
  "(i)",
  "(ii)",
  "(iii)",
  "(iv)",
  "(v)",
  "(vi)",
  "(vii)",
  "(viii)",
  "(ix)",
  "(x)",
];

function createQuestionPart(
  orderIndex: number,
  parentId: string | null = null,
  label?: string,
): QuestionPart {
  return {
    id:
      globalThis.crypto?.randomUUID?.() ??
      `question-part-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    label: label ?? (parentId ? "(i)" : "(جديد)"),
    originalText: "",
    translatedText: "",
    marks: null,
    parentId,
    orderIndex,
  };
}

export function ReviewStep({
  questions,
  layoutAssets,
  onUpdateQuestion,
  onMoveQuestion,
  onTranslateQuestions,
  onBulkUpdateStatus,
  onUploadQuestionAsset,
  onDeleteQuestionAsset,
  onLinkLayoutAsset,
  onUnlinkLayoutAsset,
  onCropLayoutAsset,
  translationProviderStatus,
  translationBatchSummary,
}: ReviewStepProps) {
  const sortedQuestions = [...questions].sort(
    (a, b) => a.orderIndex - b.orderIndex,
  );
  const activeQuestions = sortedQuestions.filter(
    (question) => question.status !== "deleted",
  );

  const [cropTarget, setCropTarget] = useState<{
    questionId: string;
    asset: PdfLayoutAssetInfo;
  } | null>(null);
  const [cropSaving, setCropSaving] = useState(false);

  async function handleSaveCrop(
    crop: VisualCropRequest,
  ) {
    if (!cropTarget) return;

    setCropSaving(true);

    try {
      await onCropLayoutAsset(
        cropTarget.questionId,
        cropTarget.asset.id,
        crop,
      );
      setCropTarget(null);
    } finally {
      setCropSaving(false);
    }
  }

  function getCurrentNumber(questionId: string) {
    const index = activeQuestions.findIndex(
      (question) => question.id === questionId,
    );
    return index >= 0 ? index + 1 : "—";
  }

  function canMove(question: QuestionItem, direction: "up" | "down") {
    if (question.status === "deleted") return false;
    const index = activeQuestions.findIndex((item) => item.id === question.id);
    if (direction === "up") return index > 0;
    return index >= 0 && index < activeQuestions.length - 1;
  }

  function handleAssetInput(
    questionId: string,
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    onUploadQuestionAsset(questionId, file);
  }

  function saveQuestionParts(question: QuestionItem, parts: QuestionPart[]) {
    onUpdateQuestion(question.id, {
      parts: normalizeQuestionPartHierarchy(parts),
    });
  }

  function updateQuestionPart(
    question: QuestionItem,
    partId: string,
    updates: Partial<QuestionPart>,
  ) {
    const nextParts = sortQuestionParts(question.parts).map((part) =>
      part.id === partId ? { ...part, ...updates } : part,
    );
    saveQuestionParts(question, nextParts);
  }

  function addQuestionPart(question: QuestionItem) {
    const currentParts = normalizeQuestionPartHierarchy(question.parts ?? []);
    saveQuestionParts(question, [
      ...currentParts,
      createQuestionPart(currentParts.length + 1),
    ]);
  }

  function addChildQuestionPart(question: QuestionItem, parentId: string) {
    const currentParts = normalizeQuestionPartHierarchy(question.parts ?? []);
    const childIndex = currentParts.filter(
      (part) => part.parentId === parentId,
    ).length;
    const childLabel =
      childPartLabels[childIndex] ?? `(${childIndex + 1})`;

    saveQuestionParts(question, [
      ...currentParts,
      createQuestionPart(
        currentParts.length + 1,
        parentId,
        childLabel,
      ),
    ]);
  }

  function deleteQuestionPart(question: QuestionItem, partId: string) {
    const currentParts = normalizeQuestionPartHierarchy(question.parts ?? []);
    const deletedPart = currentParts.find((part) => part.id === partId);
    const nextParts = currentParts
      .filter((part) => part.id !== partId)
      .map((part) =>
        part.parentId === partId
          ? {
              ...part,
              parentId: deletedPart?.parentId ?? null,
            }
          : part,
      );

    saveQuestionParts(question, nextParts);
  }

  function moveQuestionPart(
    question: QuestionItem,
    partId: string,
    direction: "up" | "down",
  ) {
    const currentParts = normalizeQuestionPartHierarchy(question.parts ?? []);
    const currentPart = currentParts.find((part) => part.id === partId);

    if (!currentPart) return;

    const siblings = getQuestionPartSiblings(currentPart, currentParts);
    const currentSiblingIndex = siblings.findIndex(
      (part) => part.id === partId,
    );
    const targetSiblingIndex =
      direction === "up"
        ? currentSiblingIndex - 1
        : currentSiblingIndex + 1;

    if (
      currentSiblingIndex < 0 ||
      targetSiblingIndex < 0 ||
      targetSiblingIndex >= siblings.length
    ) {
      return;
    }

    const targetPart = siblings[targetSiblingIndex];
    const nextParts = currentParts.map((part) => {
      if (part.id === currentPart.id) {
        return {
          ...part,
          orderIndex: targetPart.orderIndex,
        };
      }

      if (part.id === targetPart.id) {
        return {
          ...part,
          orderIndex: currentPart.orderIndex,
        };
      }

      return part;
    });

    saveQuestionParts(question, nextParts);
  }

  return (
    <section className="review-layout">
      <div className="section-heading split-heading">
        <div>
          <p className="eyebrow">مراجعة الأسئلة</p>
          <h3>بطاقات مستقلة قابلة للتعديل والحذف والترتيب</h3>
          <p>
            أي سؤال محذوف لا يدخل في التصدير النهائي، ويُعاد ترقيم الأسئلة
            المعتمدة تلقائيًا. يمكن الآن ربط صورة أو جدول بكل سؤال يدويًا.
          </p>
        </div>
        <button
          className="primary-button"
          type="button"
          onClick={onTranslateQuestions}
          disabled={activeQuestions.length === 0}
        >
          <Languages size={18} />
          ترجمة الأسئلة وأجزائها
        </button>
      </div>

      <div className="notice-card translation-notice">
        <strong>مرفقات الأسئلة:</strong>
        <span>
          تستطيع ربط صور/جداول يدوية بالسؤال لتظهر في المراجعة والتصدير. استخراج
          الصور تلقائيًا من PDF مؤجل لمرحلة لاحقة.
        </span>
      </div>

      <div className="notice-card translation-notice">
        <strong>مزود الترجمة:</strong>
        <span>
          {translationProviderStatus?.ready
            ? `جاهز للترجمة الفعلية: ${translationProviderStatus.provider} / ${translationProviderStatus.model}`
            : "الترجمة الخارجية غير جاهزة؛ سيُستخدم fallback المحلي"}
          {translationProviderStatus?.ready && translationProviderStatus.apiMode
            ? ` عبر ${formatProviderApiMode(translationProviderStatus.apiMode)}`
            : ""}
          . تُترجم أجزاء السؤال بصورة مستقلة عند وجودها، ويُفحص التزام الناتج
          بالمصطلحات المعتمدة وبالأرقام والوحدات والمعادلات والصيغ والدرجات
          والمراجع العلمية المحمية. عند وجود أي مخالفة تُجرى محاولة تصحيح واحدة
          فقط قبل الرجوع إلى fallback المحلي. ترسل مدارك طلبات OpenAI الرسمية
          عبر Responses API وطلبات Gemini عبر generateContent مع store=false،
          وتبقى مراجعة المعلم إلزامية قبل التصدير.
        </span>
      </div>

      {translationBatchSummary ? (
        <div className="notice-card translation-notice">
          <strong>ملخص دفعة الترجمة:</strong>
          <span>
            {formatTranslationBatchStatus(translationBatchSummary.status)}.
            العناصر: {translationBatchSummary.totalItems}، نجاح خارجي مباشر:{" "}
            {translationBatchSummary.externalSuccessCount}، نجاح بعد التصحيح:{" "}
            {translationBatchSummary.correctedSuccessCount}، fallback محلي:{" "}
            {translationBatchSummary.localFallbackCount}، متجاوزة:{" "}
            {translationBatchSummary.skippedCount}، فشل محفوظ بأمان:{" "}
            {translationBatchSummary.failedSafelyCount}.
            {translationBatchSummary.urgentReviewCount > 0
              ? ` تحتاج ${translationBatchSummary.urgentReviewCount} عناصر إلى مراجعة عاجلة.`
              : " لا توجد عناصر مصنفة للمراجعة العاجلة."}
          </span>
        </div>
      ) : null}

      <div className="review-bulk-actions">
        <button
          type="button"
          className="secondary-button compact"
          onClick={() => onBulkUpdateStatus("approved", false)}
          disabled={activeQuestions.length === 0}
        >
          <CheckCircle2 size={16} />
          اعتماد كل الأسئلة النشطة
        </button>
        <button
          type="button"
          className="secondary-button compact"
          onClick={() => onBulkUpdateStatus("needs_review", false)}
          disabled={activeQuestions.length === 0}
        >
          <RotateCcw size={16} />
          تحويل النشطة إلى تحتاج مراجعة
        </button>
        <button
          type="button"
          className="secondary-button compact"
          onClick={() => onBulkUpdateStatus("needs_review", true)}
          disabled={sortedQuestions.length === 0}
        >
          <RotateCcw size={16} />
          استعادة الكل للمراجعة
        </button>
      </div>

      <div className="question-card-list">
        {sortedQuestions.map((question) => {
          const linkedAssetIds = question.linkedLayoutAssetIds ?? [];
          const linkedLayoutAssets = layoutAssets.filter((asset) =>
            linkedAssetIds.includes(asset.id),
          );
          const availableLayoutAssets = layoutAssets.filter(
            (asset) => !linkedAssetIds.includes(asset.id),
          );
          const questionParts = normalizeQuestionPartHierarchy(
            question.parts ?? [],
          );
          const questionPartsTotalMarks =
            getQuestionPartsTotalMarks(questionParts);
          const hasQuestionMarksGuidance =
            questionPartsTotalMarks !== null &&
            question.marks !== questionPartsTotalMarks;

          return (
            <article
              key={question.id}
              className={`question-card ${question.status === "deleted" ? "is-deleted" : ""}`}
            >
              <header className="question-card-header">
                <div>
                  <span className="status-pill">
                    السؤال {getCurrentNumber(question.id)}
                  </span>
                  <strong>الأصل: {question.originalNumber}</strong>
                </div>
                <select
                  value={question.status}
                  onChange={(event) =>
                    onUpdateQuestion(question.id, {
                      status: event.target.value as QuestionStatus,
                    })
                  }
                >
                  <option value="approved">{statusLabels.approved}</option>
                  <option value="needs_review">
                    {statusLabels.needs_review}
                  </option>
                  <option value="deleted">{statusLabels.deleted}</option>
                </select>
              </header>

              <label>
                النص الأصلي
                <textarea value={question.originalText} readOnly dir="ltr" />
              </label>

              <label>
                الترجمة العربية
                <textarea
                  value={question.translatedText}
                  onChange={(event) =>
                    onUpdateQuestion(question.id, {
                      translatedText: event.target.value,
                    })
                  }
                />
              </label>

              <section className="question-parts-panel">
                <div className="question-parts-header">
                  <div>
                    <strong>أجزاء السؤال</strong>
                    <span>
                      {questionParts.length > 0
                        ? `${questionParts.length} جزء محفوظ بهيكل رئيسي وفرعي`
                        : "لا توجد أجزاء منظمة لهذا السؤال"}
                    </span>
                  </div>
                  <button
                    type="button"
                    className="secondary-button compact"
                    onClick={() => addQuestionPart(question)}
                    disabled={question.status === "deleted"}
                  >
                    <Plus size={16} />
                    إضافة جزء رئيسي
                  </button>
                </div>

                {questionParts.length > 0 ? (
                  <div className="question-parts-list">
                    {questionParts.map((part, partIndex) => {
                      const partDepth = getQuestionPartDepth(
                        part,
                        questionParts,
                      );
                      const parentPart = part.parentId
                        ? questionParts.find(
                            (candidate) => candidate.id === part.parentId,
                          )
                        : null;
                      const parentCandidates = questionParts.filter(
                        (candidate) =>
                          candidate.id !== part.id &&
                          !candidate.parentId &&
                          candidate.orderIndex < part.orderIndex,
                      );

                      return (
                        <article
                        key={part.id}
                        className={`question-part-card ${
                          partDepth > 0 ? "is-child" : "is-root"
                        }`}
                        style={
                          {
                            "--question-part-depth": partDepth,
                          } as CSSProperties
                        }
                      >
                        <header className="question-part-card-header">
                          <div>
                            <span>
                              {partDepth > 0
                                ? `جزء فرعي تابع لـ ${
                                    parentPart?.label || "جزء رئيسي"
                                  }`
                                : `جزء رئيسي · الترتيب ${partIndex + 1}`}
                            </span>
                            <strong>{part.label.trim() || "بدون وسم"}</strong>
                          </div>
                          <div className="question-part-actions">
                            {partDepth === 0 ? (
                              <button
                                type="button"
                                className="secondary-button compact"
                                onClick={() =>
                                  addChildQuestionPart(question, part.id)
                                }
                                disabled={question.status === "deleted"}
                              >
                                <Plus size={15} />
                                إضافة فرعي
                              </button>
                            ) : null}
                            <button
                              type="button"
                              className="secondary-button compact"
                              onClick={() =>
                                moveQuestionPart(question, part.id, "up")
                              }
                              disabled={
                                question.status === "deleted" ||
                                !canMoveQuestionPart(
                                  part,
                                  questionParts,
                                  "up",
                                )
                              }
                            >
                              <ArrowUp size={15} />
                              رفع
                            </button>
                            <button
                              type="button"
                              className="secondary-button compact"
                              onClick={() =>
                                moveQuestionPart(question, part.id, "down")
                              }
                              disabled={
                                question.status === "deleted" ||
                                !canMoveQuestionPart(
                                  part,
                                  questionParts,
                                  "down",
                                )
                              }
                            >
                              <ArrowDown size={15} />
                              إنزال
                            </button>
                            <button
                              type="button"
                              className="danger-button compact"
                              onClick={() =>
                                deleteQuestionPart(question, part.id)
                              }
                              disabled={question.status === "deleted"}
                            >
                              <Trash2 size={15} />
                              حذف الجزء
                            </button>
                          </div>
                        </header>

                        <div className="question-part-fields">
                          <label>
                            وسم الجزء
                            <input
                              value={part.label}
                              dir="ltr"
                              onChange={(event) =>
                                updateQuestionPart(question, part.id, {
                                  label: event.target.value,
                                })
                              }
                              disabled={question.status === "deleted"}
                              placeholder="مثل (a) أو (i)"
                            />
                          </label>

                          <label>
                            الدرجة
                            <input
                              type="number"
                              min="0"
                              step="1"
                              value={part.marks ?? ""}
                              onChange={(event) => {
                                const rawValue = event.target.value;
                                updateQuestionPart(question, part.id, {
                                  marks:
                                    rawValue === "" ? null : Number(rawValue),
                                });
                              }}
                              disabled={question.status === "deleted"}
                            />
                          </label>

                          <label className="question-part-parent-field">
                            التبعية
                            <select
                              value={part.parentId ?? ""}
                              onChange={(event) =>
                                updateQuestionPart(question, part.id, {
                                  parentId: event.target.value || null,
                                })
                              }
                              disabled={question.status === "deleted"}
                            >
                              <option value="">جزء رئيسي</option>
                              {parentCandidates.map((candidate) => (
                                <option
                                  key={candidate.id}
                                  value={candidate.id}
                                >
                                  فرعي تابع لـ{" "}
                                  {candidate.label.trim() || "جزء رئيسي"}
                                </option>
                              ))}
                            </select>
                          </label>

                          <label className="question-part-field-wide">
                            النص الأصلي
                            <textarea
                              value={part.originalText}
                              dir="ltr"
                              onChange={(event) =>
                                updateQuestionPart(question, part.id, {
                                  originalText: event.target.value,
                                })
                              }
                              disabled={question.status === "deleted"}
                            />
                          </label>

                          <label className="question-part-field-wide">
                            الترجمة العربية
                            <textarea
                              value={part.translatedText}
                              onChange={(event) =>
                                updateQuestionPart(question, part.id, {
                                  translatedText: event.target.value,
                                })
                              }
                              disabled={question.status === "deleted"}
                            />
                          </label>
                        </div>
                        </article>
                      );
                    })}
                  </div>
                ) : (
                  <div className="question-parts-empty">
                    أضف الأجزاء يدويًا عند الحاجة، أو اترك السؤال دون أجزاء إذا
                    كان سؤالًا مستقلًا أو اختيارًا من متعدد.
                  </div>
                )}
              </section>

              <div className="question-tools-grid">
                <label>
                  الدرجة
                  <input
                    type="number"
                    min="0"
                    value={question.marks ?? ""}
                    onChange={(event) => {
                      const rawValue = event.target.value;
                      onUpdateQuestion(question.id, {
                        marks: rawValue === "" ? null : Number(rawValue),
                      });
                    }}
                  />
                </label>

                <label>
                  ملاحظة مراجعة
                  <input
                    value={question.reviewNotes ?? ""}
                    onChange={(event) =>
                      onUpdateQuestion(question.id, {
                        reviewNotes: event.target.value,
                      })
                    }
                    placeholder="اختياري"
                  />
                </label>
              </div>

              {hasQuestionMarksGuidance ? (
                <div className="question-marks-guidance">
                  <AlertTriangle size={22} />
                  <div>
                    <strong>
                      {question.marks === null
                        ? "درجة السؤال العامة غير محددة"
                        : "درجة السؤال لا تتطابق مع مجموع أجزائه"}
                    </strong>
                    <span>
                      {question.marks === null
                        ? `مجموع الأجزاء المحسوب هو ${questionPartsTotalMarks}. سيُستخدم هذا المجموع في التصدير عند بقاء الدرجة العامة فارغة.`
                        : `الدرجة الحالية ${question.marks}، بينما مجموع الأجزاء المحسوب ${questionPartsTotalMarks}. التصدير متاح وسيستخدم الدرجة العامة الحالية حتى اعتماد المجموع.`}
                    </span>
                  </div>
                  <button
                    type="button"
                    className="secondary-button compact"
                    onClick={() =>
                      onUpdateQuestion(question.id, {
                        marks: questionPartsTotalMarks,
                      })
                    }
                    disabled={question.status === "deleted"}
                  >
                    اعتماد مجموع الأجزاء: {questionPartsTotalMarks}
                  </button>
                </div>
              ) : null}

              <section className="asset-panel">
                <div className="asset-panel-header">
                  <div>
                    <strong>مرفقات السؤال</strong>
                    <span>
                      {question.attachments.length > 0
                        ? `${question.attachments.length} مرفق`
                        : "لا توجد مرفقات بعد"}
                    </span>
                  </div>
                  <label className="secondary-button compact asset-upload-button">
                    <ImagePlus size={16} />
                    إضافة صورة/جدول
                    <input
                      type="file"
                      accept="image/png,image/jpeg"
                      onChange={(event) => handleAssetInput(question.id, event)}
                    />
                  </label>
                </div>

                {question.attachments.length > 0 ? (
                  <div className="asset-gallery">
                    {question.attachments.map((asset) => (
                      <figure key={asset.id} className="asset-card">
                        <img
                          src={`data:${asset.type};base64,${asset.dataBase64}`}
                          alt={asset.name}
                        />
                        <figcaption>
                          <span>{asset.name}</span>
                          <small>{formatFileSize(asset.size)}</small>
                        </figcaption>
                        <button
                          type="button"
                          className="asset-delete-button"
                          onClick={() =>
                            onDeleteQuestionAsset(question.id, asset.id)
                          }
                          aria-label="حذف المرفق"
                        >
                          <X size={15} />
                        </button>
                      </figure>
                    ))}
                  </div>
                ) : (
                  <div className="attachment-box">
                    {question.attachmentNote ??
                      "يمكنك إضافة صورة رسم أو جدول لهذا السؤال يدويًا."}
                  </div>
                )}
              </section>

              <section className="layout-link-panel">
                <div className="asset-panel-header">
                  <div>
                    <strong>صفحات PDF المرجعية</strong>
                    <span>
                      {linkedLayoutAssets.length > 0
                        ? `${linkedLayoutAssets.length} صفحة مرجعية مرتبطة بهذا السؤال`
                        : "لا توجد صفحة PDF مرجعية مرتبطة بهذا السؤال"}
                    </span>
                  </div>
                </div>

                {linkedLayoutAssets.length > 0 ? (
                  <div className="question-layout-assets-grid">
                    {linkedLayoutAssets.map((asset) => (
                      <article
                        key={asset.id}
                        className="question-layout-asset-card is-linked"
                      >
                        <img
                          src={`data:${asset.type};base64,${asset.dataBase64}`}
                          alt={`لقطة مرتبطة من الصفحة ${asset.pageNumber}`}
                        />
                        <div className="question-layout-asset-body">
                          <strong>صفحة {asset.pageNumber}</strong>
                          <span>{asset.note || asset.name}</span>
                          <div className="question-layout-asset-actions">
                            <button
                              type="button"
                              className="primary-button compact"
                              onClick={() =>
                                setCropTarget({
                                  questionId: question.id,
                                  asset,
                                })
                              }
                              disabled={question.status === "deleted"}
                            >
                              <Crop size={15} />
                              قص الشكل
                            </button>

                            <button
                              type="button"
                              className="secondary-button compact"
                              onClick={() =>
                                onUnlinkLayoutAsset(
                                  question.id,
                                  asset.id,
                                )
                              }
                              disabled={question.status === "deleted"}
                            >
                              <Unlink size={15} />
                              فك الربط
                            </button>
                          </div>
                        </div>
                      </article>
                    ))}
                  </div>
                ) : (
                  <div className="attachment-box">
                    لم تُربط أي صفحة PDF مرجعية بهذا السؤال بعد.
                  </div>
                )}

                <div className="layout-link-divider">
                  <strong>اللقطات المتاحة للربط</strong>
                  <span>
                    {availableLayoutAssets.length > 0
                      ? `${availableLayoutAssets.length} لقطة متاحة`
                      : layoutAssets.length > 0
                        ? "جميع اللقطات مرتبطة بهذا السؤال"
                        : "لا توجد لقطات مستخرجة من PDF"}
                  </span>
                </div>

                {availableLayoutAssets.length > 0 ? (
                  <div className="question-layout-assets-grid">
                    {availableLayoutAssets.map((asset) => (
                      <article
                        key={asset.id}
                        className="question-layout-asset-card"
                      >
                        <img
                          src={`data:${asset.type};base64,${asset.dataBase64}`}
                          alt={`لقطة متاحة من الصفحة ${asset.pageNumber}`}
                        />
                        <div className="question-layout-asset-body">
                          <strong>صفحة {asset.pageNumber}</strong>
                          <span>{asset.note || asset.name}</span>
                          <button
                            type="button"
                            className="primary-button compact"
                            onClick={() =>
                              onLinkLayoutAsset(question.id, asset.id)
                            }
                            disabled={question.status === "deleted"}
                          >
                            <Link2 size={15} />
                            ربط بالسؤال
                          </button>
                        </div>
                      </article>
                    ))}
                  </div>
                ) : null}
              </section>

              <footer className="card-actions">
                <button
                  type="button"
                  className="secondary-button compact"
                  disabled={!canMove(question, "up")}
                  onClick={() => onMoveQuestion(question.id, "up")}
                >
                  <ArrowUp size={16} />
                  رفع
                </button>
                <button
                  type="button"
                  className="secondary-button compact"
                  disabled={!canMove(question, "down")}
                  onClick={() => onMoveQuestion(question.id, "down")}
                >
                  <ArrowDown size={16} />
                  إنزال
                </button>
                {question.status === "deleted" ? (
                  <button
                    type="button"
                    className="primary-button compact"
                    onClick={() =>
                      onUpdateQuestion(question.id, { status: "needs_review" })
                    }
                  >
                    <RotateCcw size={16} />
                    استعادة
                  </button>
                ) : (
                  <button
                    type="button"
                    className="danger-button compact"
                    onClick={() =>
                      onUpdateQuestion(question.id, { status: "deleted" })
                    }
                  >
                    <Trash2 size={16} />
                    حذف
                  </button>
                )}
              </footer>
            </article>
          );
        })}
      </div>
      {cropTarget ? (
        <VisualCropDialog
          asset={cropTarget.asset}
          isSaving={cropSaving}
          onCancel={() => {
            if (!cropSaving) {
              setCropTarget(null);
            }
          }}
          onSave={handleSaveCrop}
        />
      ) : null}

    </section>
  );
}
