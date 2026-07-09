# منصة مدارك - Phase 0 Skeleton

هيكل تأسيسي لمنصة مدارك، مبني بمنهجية مراحل صغيرة مستقرة:

- Frontend: React + TypeScript + Vite
- Backend: Python + FastAPI
- Docs: قرارات ومخطط ومراحل وواجهات API

## نطاق Phase 0

هذه المرحلة لا تحتوي على OCR أو ترجمة أو تصدير فعلي. الهدف منها تثبيت الهيكل وتشغيل واجهة وخلفية أولية فقط.

## التشغيل السريع

### تشغيل الواجهة

```bash
cd frontend
npm install
npm run dev
```

### تشغيل الخلفية

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## منافذ التشغيل الافتراضية

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Health: http://localhost:8000/api/health

## ملاحظات

- لا تحفظ المنصة ملفات دائمة في Phase 0.
- لا يوجد نظام حسابات في Phase 0.
- الواجهة RTL من البداية.
