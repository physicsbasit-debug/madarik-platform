# منصة مدارك - Phase 2-C1 AI Provider Hardening

## الغرض

تقوية طبقة مزود الذكاء الاصطناعي قبل الاعتماد الجاد عليها، مع بقاء fallback آمنًا وعدم كشف الأسرار.

## ما تم

- توسيع حالة مزود الترجمة:
  - `ready`
  - `reason`
  - `external_enabled`
  - `timeout_seconds`
  - `max_input_chars`
  - `temperature`
  - `supported_providers`
  - `base_url_configured`
- دعم تسمية:
  - `mock`
  - `openai`
  - `openai-compatible`
- إضافة قرار آمن قبل الاتصال الخارجي:
  - مزود غير مدعوم.
  - مفاتيح ناقصة.
  - الاتصال الخارجي معطل.
  - النص أطول من الحد.
- تحسين fallback عند:
  - timeout.
  - HTTP error.
  - استجابة فارغة.
  - خطأ شبكة.
- إضافة إعدادات بيئية:
  - `MADARIK_AI_EXTERNAL_ENABLED`
  - `MADARIK_AI_MAX_INPUT_CHARS`
  - `MADARIK_AI_TEMPERATURE`
- عدم كشف `MADARIK_AI_API_KEY` في أي endpoint.

## ما لم يدخل

- واجهة إعداد مفاتيح AI من داخل التطبيق.
- دفع أو حدود تكلفة فعلية.
- اختيار مزود من الواجهة.
- سجل تدقيق تفصيلي لكل طلب.
- توليد نموذج إجابة.

## ملاحظة

هذه مرحلة تقوية أمان واستقرار. المزود الخارجي يبقى اختياريًا، والفشل لا يكسر مسار العمل. لأن ربط منتج تعليمي كامل بمزاج API خارجي فكرة تصلح كاختبار صبر، لا كمعمارية.
