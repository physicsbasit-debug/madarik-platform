import type { StepKey } from '../types/project';

export interface StepDefinition {
  key: StepKey;
  label: string;
  description: string;
}

export const steps: StepDefinition[] = [
  { key: 'setup', label: 'بيانات الورقة', description: 'إعداد رأس الورقة ونوع النسخة' },
  { key: 'upload', label: 'رفع الملف', description: 'استقبال ملف الاختبار وفحصه شكليًا' },
  { key: 'extract', label: 'استخراج الأسئلة', description: 'عرض أسئلة تجريبية مستقلة' },
  { key: 'glossary', label: 'قاموس الورقة', description: 'توحيد المصطلحات قبل الترجمة' },
  { key: 'review', label: 'مراجعة الأسئلة', description: 'تعديل وحذف وترتيب ودرجات' },
  { key: 'export', label: 'التصدير', description: 'معاينة قرار الإخراج النهائي' },
];
