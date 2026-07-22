import type { StepKey } from '../types/project';

export type WorkflowStageKey = 'start' | 'review' | 'export';

export interface StepDefinition {
  key: WorkflowStageKey;
  label: string;
  description: string;
}

export const steps: StepDefinition[] = [
  {
    key: 'start',
    label: 'البدء والرفع',
    description: 'اختر مشروعًا، أدخل البيانات، وارفع الورقة',
  },
  {
    key: 'review',
    label: 'المراجعة',
    description: 'راجع الأسئلة والترجمة وما يحتاج تدخلك فقط',
  },
  {
    key: 'export',
    label: 'التصدير والجاهزية',
    description: 'افحص الجاهزية واختر النسخة والصيغ ثم نزّل ملفاتك',
  },
];

export function getWorkflowStageIndex(stepKey: StepKey | undefined) {
  if (stepKey === 'export') return 2;
  if (stepKey === 'extract' || stepKey === 'glossary' || stepKey === 'review') {
    return 1;
  }
  return 0;
}

export function getLegacyStepForStage(stageKey: WorkflowStageKey): StepKey {
  if (stageKey === 'review') return 'review';
  if (stageKey === 'export') return 'export';
  return 'upload';
}
