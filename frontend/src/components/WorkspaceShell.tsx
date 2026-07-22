import type { ReactNode } from 'react';

interface WorkspaceShellProps {
  sidebar: ReactNode;
  topbar: ReactNode;
  status: ReactNode;
  children: ReactNode;
}

export function WorkspaceShell({ sidebar, topbar, status, children }: WorkspaceShellProps) {
  return (
    <main className="rtl-workspace-shell" dir="rtl">
      {sidebar}
      <section className="rtl-workspace-main">
        {topbar}
        {status}
        <section className="rtl-workspace-content">{children}</section>
      </section>
    </main>
  );
}
