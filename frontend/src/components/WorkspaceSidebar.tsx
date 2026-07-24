import {
  CheckCircle2,
  FileOutput,
  ScanSearch,
  UploadCloud,
} from "lucide-react";
import type { StepDefinition } from "../constants/steps";

interface WorkspaceSidebarProps {
  steps: StepDefinition[];
  activeIndex: number;
  onSelectStep: (index: number) => void;
}

const stageIcons = [UploadCloud, ScanSearch, FileOutput];

export function WorkspaceSidebar({
  steps,
  activeIndex,
  onSelectStep,
}: WorkspaceSidebarProps) {
  return (
    <aside className="workflow-rail" aria-label="مراحل معالجة الورقة">
      <div className="workflow-rail-heading">
        <small>مساحة معالجة الورقة</small>
        <strong>رحلة المشروع</strong>
        <p>انتقل بين الاستيراد والمراجعة والتصدير دون مغادرة المنصة.</p>
      </div>

      <nav className="workflow-rail-list" aria-label="خطوات العمل">
        {steps.map((step, index) => {
          const Icon = stageIcons[index];
          const isActive = index === activeIndex;
          const isDone = index < activeIndex;

          return (
            <button
              key={step.key}
              type="button"
              className={`workflow-rail-item ${isActive ? "is-active" : ""} ${isDone ? "is-done" : ""}`}
              onClick={() => onSelectStep(index)}
              aria-current={isActive ? "step" : undefined}
            >
              <span className="workflow-rail-number">
                {isDone ? <CheckCircle2 size={18} /> : index + 1}
              </span>
              <span className="workflow-rail-copy">
                <strong>{step.label}</strong>
                <small>{step.description}</small>
              </span>
              <Icon className="workflow-rail-icon" size={20} aria-hidden="true" />
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
