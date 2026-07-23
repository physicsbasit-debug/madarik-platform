# Phase 9-B: OneDrive Authentication and Microsoft Graph Adapter

تضيف المرحلة إعدادات OneDrive عبر متغيرات البيئة، وتستخدم تدفق Client
Credentials مع نطاق Microsoft Graph الافتراضي. يدعم المحول قراءة بيانات
driveItem، مقارنة ETag، وتخزين حالة المزامنة، مع تنزيل اختياري من رابط التنزيل
المؤقت الذي يعيده Graph. يبقى المحول معطلًا افتراضيًا ولا تعرض الواجهة أي سر.

خارج النطاق: Authorization Code، Microsoft Picker، سجل النسخ، وفتح الملف كمشروع.
