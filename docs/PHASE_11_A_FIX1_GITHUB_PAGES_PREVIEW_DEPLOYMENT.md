# Phase 11-A Fix 1: GitHub Pages Preview Deployment

## المشكلة

نجحت بوابة الاختبارات والبناء بعد Phase 11-A، لكن واجهة GitHub Pages بقيت على
النسخة القديمة. السبب أن Workflow بوابة الإصدار كان ينفذ `npm run build` فقط،
ثم ينتهي دون رفع `frontend/dist` أو تشغيل GitHub Pages deployment.

## الإصلاح

أضيف Workflow مستقل:

```text
.github/workflows/deploy-phase11a-preview.yml
```

ويعمل عند رفع تغييرات الواجهة إلى الفرع:

```text
feat/madarik-science-platform-v2
```

وينفذ بالترتيب:

1. تثبيت Node.js 22 واعتمادات Frontend.
2. تشغيل ESLint.
3. بناء Vite للإنتاج.
4. تمرير المسار العام `/madarik-platform/` إلى أمر `vite build --base` دون تغيير إعداد التطوير المحلي.
5. تمرير `MADARIK_API_BASE_URL` من Repository Variables عند توفره.
6. رفع `frontend/dist` عبر `actions/upload-pages-artifact`.
7. نشره عبر `actions/deploy-pages` إلى بيئة `github-pages`.

## إعداد GitHub المطلوب

داخل المستودع:

```text
Settings → Pages → Build and deployment → Source → GitHub Actions
```

ومتغير عنوان Backend، عند توفر Backend منشور، يوضع في:

```text
Settings → Secrets and variables → Actions → Variables
Name: MADARIK_API_BASE_URL
Value: https://your-backend.example.com/api
```

لا يوضع هذا العنوان ضمن Secrets لأنه ليس مفتاحًا سريًا.

## معيار القبول

يجب أن يظهر Workflow باسم:

```text
Deploy Phase 11-A Platform Preview
```

وتنجح مهمتاه:

```text
Build new platform UX
Deploy new platform UX
```

بعدها يعرض رابط GitHub Pages الغلاف الجديد للمنصة بدل واجهة المراحل الثلاث
القديمة.
