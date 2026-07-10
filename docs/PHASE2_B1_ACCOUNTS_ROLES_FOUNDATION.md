# منصة مدارك - Phase 2-B1 Accounts & Roles Foundation

## الغرض

إضافة طبقة حسابات وصلاحيات أولية فوق SQLite، دون ربط ملكية المشاريع بالمستخدمين بعد.

## ما تم

- إضافة نماذج Auth:
  - `AuthAccountPublic`
  - `AuthStatus`
  - `AuthBootstrapRequest`
  - `AuthLoginRequest`
  - `AuthSessionInfo`
- إضافة Repository للحسابات والجلسات:
  - `backend/app/services/auth_repository.py`
- إضافة API:
  - `GET /api/auth/status`
  - `POST /api/auth/bootstrap`
  - `POST /api/auth/login`
  - `GET /api/auth/me`
  - `POST /api/auth/logout`
- إضافة واجهة حسابات أولية:
  - إنشاء حساب المالك عند أول تشغيل.
  - تسجيل الدخول.
  - عرض الحساب الحالي والدور.
  - تسجيل الخروج.
- تخزين الجلسة في `localStorage` من جهة الواجهة.
- تخزين الحسابات والجلسات في SQLite.

## الأدوار الأولية

- `owner`
- `teacher`
- `reviewer`

## ما لم يدخل

- ربط المشاريع بمالك.
- منع فتح المشاريع حسب المستخدم.
- إدارة حسابات من الواجهة.
- تغيير كلمة المرور.
- دعوات مستخدمين.
- صلاحيات تفصيلية لكل زر.

## ملاحظة

هذه مرحلة أساس. الصلاحيات الفعلية وربط المشاريع بالحسابات يجب أن تأتي في مرحلة لاحقة، حتى لا نكسر مكتبة المشاريع وهي بالكاد تعلمت الوقوف.
