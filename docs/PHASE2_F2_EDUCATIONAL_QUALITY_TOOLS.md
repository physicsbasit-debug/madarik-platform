# منصة مدارك - Phase 2-F2 Educational Quality Tools

## الغرض

إضافة أدوات جودة تربوية تأسيسية فوق التحليل التربوي: Pareto وRadar وFishbone، بهدف مساعدة المعلم على تحديد أولويات مراجعة الورقة.

## ما تم

- إضافة نموذج:
  - `EducationalQualityToolsReport`
- إضافة حقل داخل المشروع:
  - `quality_tools`
- إضافة خدمة:
  - `backend/app/services/quality_tools.py`
- إضافة endpoints:
  - `POST /api/projects/{project_id}/quality-tools`
  - `DELETE /api/projects/{project_id}/quality-tools`
- توليد:
  - Pareto لأولويات المراجعة.
  - Radar لمحاور الجاهزية.
  - Fishbone لأسباب الضعف المحتملة.
  - إجراءات ذات أولوية.
  - تنبيهات.
- عرض الأدوات في خطوة التصدير.

## حدود المرحلة

- لا يوجد رسم بياني حقيقي باستخدام مكتبة رسوم بعد.
- لا يوجد تصدير أدوات الجودة في PDF/DOCX.
- لا يوجد تحليل مهارات رسمي.
- لا يوجد ربط بمعايير المنهج.
- لا يوجد Pareto تفاعلي أو Radar مرسوم بصريًا بعد؛ هذه بنية بيانات وعرض أولي.

## معيار القبول

- توليد أدوات الجودة من الأسئلة النشطة.
- حفظ `quality_tools` داخل المشروع.
- عرض Pareto/Radar/Fishbone في الواجهة.
- حذف أدوات الجودة.
- بقاء اختبارات Backend وFrontend خضراء.
