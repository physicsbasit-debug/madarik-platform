# Phase 4-A1: Real Scientific Translation Provider

## الهدف

تفعيل ترجمة علمية فعلية داخل منصة مدارك مع الحفاظ على fallback محلي آمن عند تعذر الاتصال الخارجي.

## المساران المدعومان

- `openai`: يستخدم OpenAI Responses API.
- `openai-compatible`: يستخدم Chat Completions لدى أي مزود متوافق.
- `mock`: ترجمة محلية تجريبية، وهي القيمة الافتراضية.

## الإعداد المحلي

```bash
cd /workspaces/madarik-platform
cp backend/.env.example backend/.env
chmod 600 backend/.env
```

افتح `backend/.env` وضع مفتاح API الحقيقي بدل القيمة الوهمية، ثم أعد تشغيل Backend.

## إعداد OpenAI المقترح

```dotenv
MADARIK_AI_PROVIDER=openai
MADARIK_AI_API_KEY=...
MADARIK_AI_MODEL=gpt-5.6-terra
MADARIK_AI_BASE_URL=https://api.openai.com/v1
MADARIK_AI_EXTERNAL_ENABLED=true
```

يمكن تغيير النموذج إلى نموذج متاح للحساب. النموذج في المثال يوازن بين الجودة والتكلفة، وليس قفلًا معماريًا.

## الخصوصية

- لا يرسل المفتاح إلى Frontend ولا يعرضه endpoint الحالة.
- يستخدم OpenAI الرسمي `store=false` حتى لا تُحفظ الاستجابة ككائن قابل للاسترجاع عبر Responses API.
- ملف `backend/.env` مستبعد من Git عبر `backend/.gitignore`.
- متغيرات البيئة وCodespaces Secrets تتقدم على ملف `.env` المحلي.

## السلوك عند الخطأ

أي مهلة أو خطأ HTTP أو استجابة فارغة لا يوقف المشروع؛ تستخدم المنصة fallback المحلي وتضيف ملاحظة مراجعة واضحة.

## اختبار القبول

1. يظهر مزود الترجمة في شاشة المراجعة بوصفه جاهزًا.
2. ترجمة سؤال علمي تنتج عربية فعلية لا تبدأ بعبارة `ترجمة أولية تحتاج مراجعة:`.
3. تحفظ الرموز والوحدات والدرجة.
4. تترجم أجزاء السؤال الهرمية بصورة مستقلة.
5. تبقى الترجمة بعد تحديث الصفحة.
6. عند تعطيل المزود يعود fallback دون تعطل المنصة.
