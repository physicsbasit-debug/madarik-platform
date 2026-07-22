# Phase 3-A: Google Drive Source Foundation

## الهدف

إضافة مصدر Google Drive للقراءة والاستيراد دون ربطه مباشرة بمنطق المناهج أو الأسئلة.

## الأوضاع

- `disabled`: الوضع الافتراضي الآمن.
- `mock`: عرض واختبارات محلية حتمية.
- `google_api`: قراءة Google Drive API باستخدام Access Token ومجلد محدد.

## متغيرات البيئة

```text
MADARIK_GOOGLE_DRIVE_PROVIDER=disabled|mock|google_api
MADARIK_GOOGLE_DRIVE_ACCESS_TOKEN=
MADARIK_GOOGLE_DRIVE_FOLDER_ID=
MADARIK_GOOGLE_DRIVE_TIMEOUT_SECONDS=30
```

## الحماية

- لا يُرجع API الرمز السري.
- التكامل للقراءة فقط.
- لا يُعرض إلا ما داخل المجلد المحدد.
- لا يُستورد ملف غير موجود ضمن القائمة المسموحة.
- الوضع الافتراضي معطل.
- Google Docs يُصدّر إلى PDF عند الاستيراد.

## حدود المرحلة

- لا يوجد OAuth تفاعلي.
- لا يوجد تجديد تلقائي للرمز.
- الملف المستورد لا يُحفظ بعد داخل مشروع مدارك.
- لا توجد مزامنة إصدارات.
- OneDrive مؤجل.
