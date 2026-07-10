import { LogIn, LogOut, ShieldCheck, UserPlus } from 'lucide-react';
import { useState } from 'react';
import type { AuthAccountPublic, AuthStatus } from '../../types/project';

interface AuthPanelProps {
  status: AuthStatus | null;
  account: AuthAccountPublic | null;
  message: string;
  onBootstrap: (username: string, displayName: string, password: string) => Promise<void>;
  onLogin: (username: string, password: string) => Promise<void>;
  onLogout: () => Promise<void>;
}

function roleLabel(role: AuthAccountPublic['role']) {
  switch (role) {
    case 'owner':
      return 'مالك المنصة';
    case 'teacher':
      return 'معلم';
    case 'reviewer':
      return 'مراجع';
  }
}

export function AuthPanel({ status, account, message, onBootstrap, onLogin, onLogout }: AuthPanelProps) {
  const [username, setUsername] = useState('owner');
  const [displayName, setDisplayName] = useState('مالك منصة مدارك');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);

  async function submitBootstrap() {
    setBusy(true);
    try {
      await onBootstrap(username, displayName, password);
      setPassword('');
    } finally {
      setBusy(false);
    }
  }

  async function submitLogin() {
    setBusy(true);
    try {
      await onLogin(username, password);
      setPassword('');
    } finally {
      setBusy(false);
    }
  }

  async function submitLogout() {
    setBusy(true);
    try {
      await onLogout();
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="auth-panel">
      <div className="auth-panel-header">
        <div>
          <p className="eyebrow">Phase 2-B1</p>
          <h3>الحسابات والصلاحيات الأولية</h3>
          <p>
            هذه طبقة دخول مبدئية فوق SQLite. لا تربط المشاريع بالمستخدمين بعد، لأننا نحاول بناء المنصة لا استدعاء وحش الصلاحيات كاملًا في لقطة واحدة.
          </p>
        </div>
        <ShieldCheck size={30} aria-hidden="true" />
      </div>

      {account ? (
        <div className="auth-current-card">
          <div>
            <strong>{account.displayName}</strong>
            <span>@{account.username} · {roleLabel(account.role)}</span>
          </div>
          <button type="button" className="secondary-button compact" onClick={() => void submitLogout()} disabled={busy}>
            <LogOut size={16} />
            خروج
          </button>
        </div>
      ) : (
        <div className="auth-form-grid">
          <label>
            اسم المستخدم
            <input value={username} onChange={(event) => setUsername(event.target.value)} placeholder="owner" dir="ltr" />
          </label>
          {status?.requiresBootstrap ? (
            <label>
              الاسم الظاهر
              <input value={displayName} onChange={(event) => setDisplayName(event.target.value)} placeholder="مالك منصة مدارك" />
            </label>
          ) : null}
          <label>
            كلمة المرور
            <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" placeholder="6 خانات أو أكثر" />
          </label>
          {status?.requiresBootstrap ? (
            <button type="button" className="primary-button" onClick={() => void submitBootstrap()} disabled={busy || password.length < 6}>
              <UserPlus size={18} />
              إنشاء حساب المالك
            </button>
          ) : (
            <button type="button" className="primary-button" onClick={() => void submitLogin()} disabled={busy || password.length < 6}>
              <LogIn size={18} />
              دخول
            </button>
          )}
        </div>
      )}

      <div className="notice-card auth-message">
        <span>{message || 'الحسابات اختيارية في هذه المرحلة، وستصبح أساس ربط المشاريع بالمستخدمين في المرحلة التالية.'}</span>
      </div>
    </section>
  );
}
