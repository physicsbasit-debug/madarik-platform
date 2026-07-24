import type { ReactNode } from "react";

interface WorkspaceShellProps {
  sidebar: ReactNode;
  topbar: ReactNode;
  status: ReactNode;
  children: ReactNode;
}

export function WorkspaceShell({
  sidebar,
  topbar,
  status,
  children,
}: WorkspaceShellProps) {
  return (
    <section className="professional-workspace" dir="rtl">
      <div className="professional-workspace-command">{topbar}</div>
      <div className="professional-workspace-status">{status}</div>
      <div className="professional-workspace-layout">
        {sidebar}
        <section className="professional-workspace-content">{children}</section>
      </div>
    </section>
  );
}
