import {
  CheckCircle2,
  FileOutput,
  HelpCircle,
  LogOut,
  Settings,
  UploadCloud,
  ScanSearch,
} from 'lucide-react';
import type { StepDefinition } from '../constants/steps';

interface WorkspaceSidebarProps {
  steps: StepDefinition[];
  activeIndex: number;
  onSelectStep: (index: number) => void;
  onOpenSettings: () => void;
}

const stageIcons = [UploadCloud, ScanSearch, FileOutput];

export function WorkspaceSidebar({
  steps,
  activeIndex,
  onSelectStep,
  onOpenSettings,
}: WorkspaceSidebarProps) {
  return (
    <aside className="workspace-sidebar" aria-label="مراحل منصة مدارك">
      <div className="workspace-brand">
        <span className="workspace-brand-mark" aria-hidden="true">م</span>
        <span>
          <strong>منصة مدارك</strong>
          <small>ارفع، راجع، صدّر</small>
        </span>
      </div>

      <nav className="workspace-stage-list" aria-label="خطوات العمل">
        {steps.map((step, index) => {
          const Icon = stageIcons[index];
          const isActive = index === activeIndex;
          const isDone = index < activeIndex;

          return (
            <button
              key={step.key}
              type="button"
              className={`workspace-stage-button ${isActive ? 'is-active' : ''} ${isDone ? 'is-done' : ''}`}
              onClick={() => onSelectStep(index)}
              aria-current={isActive ? 'step' : undefined}
            >
              <span className="workspace-stage-number">
                {isDone ? <CheckCircle2 size={19} /> : index + 1}
              </span>
              <span className="workspace-stage-copy">
                <strong>{step.label}</strong>
                <small>{step.description}</small>
              </span>
              <Icon className="workspace-stage-icon" size={21} aria-hidden="true" />
            </button>
          );
        })}
      </nav>

      <div className="workspace-sidebar-footer">
        <button type="button" className="workspace-sidebar-link" onClick={onOpenSettings}>
          <Settings size={19} />
          الإعدادات والحساب
        </button>
        <button type="button" className="workspace-sidebar-link" disabled>
          <HelpCircle size={19} />
          المساعدة
        </button>
        <button type="button" className="workspace-sidebar-link" disabled>
          <LogOut size={19} />
          تسجيل الخروج
        </button>
      </div>
    </aside>
  );
}
