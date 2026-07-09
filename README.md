# منصة مدارك - Phase 1-A Static UI Fix 1

واجهة ثابتة متعددة الخطوات لمنصة مدارك، مبنية فوق Phase 0 Skeleton.

## حالة المرحلة

هذه المرحلة تركّز على تجربة المستخدم فقط:

- واجهة RTL متعددة الخطوات.
- بيانات ورقة قابلة للتعديل.
- رفع ملف شكلي دون معالجة فعلية.
- أسئلة تجريبية ثابتة.
- قاموس مصطلحات تجريبي قابل للتعديل.
- بطاقات مراجعة للأسئلة.
- تعديل ترجمة السؤال.
- تعديل الدرجة.
- حذف واستعادة السؤال.
- رفع/إنزال السؤال وإعادة الترقيم بصريًا.
- شاشة تصدير شكلية.

## ما لا تحتويه هذه المرحلة

- لا يوجد OCR.
- لا توجد قراءة PDF فعلية.
- لا توجد ترجمة AI فعلية.
- لا يوجد تصدير DOCX/PDF فعلي.
- لا يوجد حفظ دائم.
- لا يوجد نظام حسابات.

## التشغيل المحلي للواجهة

```bash
cd frontend
npm install
npm run dev
```

## بناء الواجهة

```bash
cd frontend
npm install
npm run build
```

## تشغيل الخلفية

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

على Windows:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## اختبار الخلفية

```bash
cd backend
pytest -q
```

## معيار قبول Phase 1-A

- `npm run build` ينجح.
- اختبارات الخلفية تنجح.
- GitHub Actions يعطي علامة خضراء.
- لا توجد وظائف AI/OCR/Export حقيقية داخل المرحلة.


## Phase 1-A Fix 1

- تثبيت إصدارات React/Vite/TypeScript/Lucide بدل استخدام latest.
- تحديث package-lock.json لضمان تثبيت اعتمادات الواجهة في GitHub Actions.
- لا تغييرات منطقية على واجهة Phase 1-A.
