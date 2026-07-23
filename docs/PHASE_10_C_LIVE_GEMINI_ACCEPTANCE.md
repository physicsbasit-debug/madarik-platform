# Phase 10-C: Live Gemini Acceptance

## الهدف

إغلاق حاجز الاتصال الخارجي الحقيقي قبل الإصدار الإنتاجي، دون كشف مفتاح Gemini
أو نص السؤال أو الترجمة أو استجابة المزود الخام.

## الأسرار المطلوبة

تقرأ البوابة الأسرار الآتية من GitHub Actions:

- `MADARIK_AI_PROVIDER=gemini`
- `MADARIK_AI_EXTERNAL_ENABLED=true`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta`

لا تُحفظ هذه القيم داخل المستودع أو تقرير القبول.

## ما تفحصه البوابة

1. أن المزود المحدد هو Gemini وأن الاتصال الخارجي مفعل.
2. وجود المفتاح والنموذج دون طباعة قيمتهما.
3. استخدام HTTPS والنطاق الرسمي لخدمة Gemini.
4. تنفيذ ترجمة خارجية حقيقية لسؤال فيزياء مضبوط.
5. رفض `local_fallback` أو أي نتيجة لم تستخدم المزود الخارجي.
6. فحص جودة العربية وعدم بقاء نثر إنجليزي غير مفسر.
7. حفظ `Fig. 1.1` و`5.0 V` و`[3]` دون تغيير علمي.
8. الالتزام بالمصطلحات المعتمدة:
   - current = التيار الكهربائي
   - resistance = المقاومة الكهربائية
   - potential difference = فرق الجهد الكهربائي

## حماية البيانات

تقرير JSON المرفوع من GitHub Actions يحتوي فقط على:

- اسم المزود والنموذج.
- حالة الجاهزية والنتيجة.
- أعداد عناصر الفحص.
- بصمات SHA-256 للنصوص بدل النصوص نفسها.
- رموز فشل مختصرة عند الإخفاق.

ولا يحتوي على:

- مفتاح API.
- نص السؤال.
- نص الترجمة.
- الـprompt.
- ملاحظة المزود الداخلية.
- حمولة الطلب أو استجابة Gemini الخام.

## التشغيل

عند رفع ملفات Phase 10-C إلى الفرع
`feat/madarik-science-platform-v2` تعمل البوابة تلقائيًا مرة واحدة بسبب مرشح
المسارات. بعد دمج الملف في الفرع الافتراضي يمكن تشغيلها يدويًا أيضًا من
`workflow_dispatch`.

## معيار النجاح

```text
status=passed
provider=gemini
provider_ready=True
outcome=external_success أو corrected_success
used_external_provider=True
arabic_quality=True
scientific_fidelity=True
glossary_compliance=True
failure_count=0
```

نجاح هذه البوابة يغلق اختبار الاتصال الحي المصغر، لكنه لا يغلق مراجعة ورقة
Cambridge كاملة ولا المراجعة البصرية النهائية لملفي DOCX وPDF.
