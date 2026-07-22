import type {
  CognitiveCategory,
  QuestionItem,
} from "../../types/project";

export type QuestionClassificationResult = {
  category: CognitiveCategory;
  confidence: number;
  reason: string;
  source: "automatic_rule";
};

const patterns: Record<
  Exclude<CognitiveCategory, "unclassified">,
  RegExp[]
> = {
  knowledge: [
    /\bdefine\b/i,
    /\bstate\b/i,
    /\bname\b/i,
    /\blist\b/i,
    /\bidentify\b/i,
    /عرّف/u,
    /اذكر/u,
    /سمّ/u,
    /حدد/u,
    /عدّد/u,
  ],
  application: [
    /\bcalculate\b/i,
    /\bdetermine\b/i,
    /\buse\b/i,
    /\bfind\b/i,
    /\bsolve\b/i,
    /احسب/u,
    /أوجد/u,
    /استخدم/u,
    /طبّق/u,
  ],
  reasoning: [
    /\bexplain\b/i,
    /\bjustify\b/i,
    /\bpredict\b/i,
    /\bcompare\b/i,
    /\bevaluate\b/i,
    /فسر/u,
    /علل/u,
    /تنبأ/u,
    /قارن/u,
    /قيّم/u,
    /استنتج/u,
  ],
};

export function classifyQuestionText(
  text: string,
): QuestionClassificationResult {
  const value = text.trim();

  if (!value) {
    return {
      category: "unclassified",
      confidence: 0,
      reason: "لا يوجد نص كافٍ للتصنيف.",
      source: "automatic_rule",
    };
  }

  const scores = Object.fromEntries(
    Object.entries(patterns).map(
      ([category, categoryPatterns]) => [
        category,
        categoryPatterns.filter((pattern) =>
          pattern.test(value),
        ).length,
      ],
    ),
  ) as Record<
    Exclude<CognitiveCategory, "unclassified">,
    number
  >;

  const ranked = (
    Object.entries(scores) as Array<
      [
        Exclude<CognitiveCategory, "unclassified">,
        number,
      ]
    >
  ).sort((a, b) => b[1] - a[1]);

  const [bestCategory, bestScore] = ranked[0];
  const tied =
    ranked.filter(([, score]) => score === bestScore)
      .length > 1;

  if (bestScore === 0) {
    return {
      category: "unclassified",
      confidence: 0.25,
      reason:
        "لم تُكتشف أفعال معرفية واضحة؛ يحتاج السؤال إلى مراجعة.",
      source: "automatic_rule",
    };
  }

  if (tied) {
    return {
      category: "unclassified",
      confidence: 0.4,
      reason:
        "ظهرت مؤشرات متقاربة لأكثر من فئة معرفية.",
      source: "automatic_rule",
    };
  }

  const labels = {
    knowledge: "معرفة",
    application: "تطبيق",
    reasoning: "استدلال",
  };

  return {
    category: bestCategory,
    confidence: Math.min(
      0.55 + bestScore * 0.15,
      0.9,
    ),
    reason:
      `اكتُشفت مؤشرات لغوية ترجّح فئة ` +
      `${labels[bestCategory]}.`,
    source: "automatic_rule",
  };
}

export function classifyQuestion(
  question: QuestionItem,
): QuestionClassificationResult {
  return classifyQuestionText(
    question.translatedText.trim() ||
      question.originalText.trim() ||
      question.rawText?.trim() ||
      "",
  );
}
