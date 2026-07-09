import { CheckCircle2 } from 'lucide-react';
import type { StepDefinition } from '../constants/steps';

interface StepNavigationProps {
  steps: StepDefinition[];
  activeIndex: number;
  onSelectStep: (index: number) => void;
}

export function StepNavigation({ steps, activeIndex, onSelectStep }: StepNavigationProps) {
  return (
    <aside className="steps-panel" aria-label="خطوات العمل">
      {steps.map((step, index) => {
        const isActive = index === activeIndex;
        const isDone = index < activeIndex;

        return (
          <button
            key={step.key}
            type="button"
            className={`step-item ${isActive ? 'active' : ''} ${isDone ? 'done' : ''}`}
            onClick={() => onSelectStep(index)}
          >
            <span className="step-number" aria-hidden="true">
              {isDone ? <CheckCircle2 size={18} /> : index + 1}
            </span>
            <span>
              <strong>{step.label}</strong>
              <small>{step.description}</small>
            </span>
          </button>
        );
      })}
    </aside>
  );
}
