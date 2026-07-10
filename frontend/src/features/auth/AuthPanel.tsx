import { LogIn, LogOut, RefreshCw, ShieldCheck, UserPlus } from 'lucide-react';
import { useState } from 'react';
import type { AccountRole, AuthAccountPublic, AuthStatus } from '../../types/project';

interface AuthPanelProps {
  status: AuthStatus | null;
  account: AuthAccountPublic | null;
  accounts: AuthAccountPublic[];
  accountsLoading: boolean;
  message: string;
  onBootstrap: (username: string, displayName: string, password: string) => Promise<void>;
  onLogin: (username: string, password: string) => Promise<void>;
  onLogout: () => Promise<void>;
  onRefreshAccounts: () => Promise<void>;
  onCreateAccount: (username: string, displayName: string, password: string, role: AccountRole) => Promise<void>;
  onToggleAccount: (accountId: string, isActive: boolean) => Promise<void>;
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

export function AuthPanel({
  status,
  account,
  accounts,
  accountsLoading,
  message,
  onBootstrap,
  onLogin,
  onLogout,
  onRefreshAccounts,
  onCreateAccount,
  onToggleAccount,
}: AuthPanelProps) {
  const [username, setUsername] = useState('owner');
  const [displayName, setDisplayName] = useState('مالك منصة مدارك');
  const [password, setPassword] = useState('');
  const [newUsername, setNewUsername] = useState('');
  const [newDisplayName, setNewDisplayName] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newRole, setNewRole] = useState<AccountRole>('teacher');
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

  async function submitCreateAccount() {
    setBusy(true);
    try {
      await onCreateAccount(newUsername, newDisplayName, newPassword, newRole);
      setNewUsername('');
      setNewDisplayName('');
      setNewPassword('');
      setNewRole('teacher');
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="auth-panel">
      <div className="auth-panel-header">
        <div>
          <p className="eyebrow">Phase 2-B3</p>
          <h3>إدارة الحسابات الخفيفة</h3>
          <p>
            إنشاء حسابات أساسية وتفعيلها أو تعطيلها من حساب المالك. إدارة كاملة؟ لاحقًا. لا نستدعي بيروقراطية رقمية قبل وقتها.
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

      {account?.role === 'owner' ? (
        <div className="account-management-card">
          <div className="account-management-header">
            <div>
              <h4>إدارة الحسابات</h4>
              <p>متاحة للمالك فقط: إنشاء حساب، عرض الحسابات، تفعيل أو تعطيل.</p>
            </div>
            <button type="button" className="secondary-button compact" onClick={() => void onRefreshAccounts()} disabled={accountsLoading}>
              <RefreshCw size={16} className={accountsLoading ? 'spin-icon' : undefined} />
              تحديث
            </button>
          </div>

          <div className="account-create-grid">
            <label>
              اسم المستخدم الجديد
              <input value={newUsername} onChange={(event) => setNewUsername(event.target.value)} dir="ltr" placeholder="teacher1" />
            </label>
            <label>
              الاسم الظاهر
              <input value={newDisplayName} onChange={(event) => setNewDisplayName(event.target.value)} placeholder="أ. معلم العلوم" />
            </label>
            <label>
              كلمة المرور
              <input value={newPassword} onChange={(event) => setNewPassword(event.target.value)} type="password" placeholder="6 خانات أو أكثر" />
            </label>
            <label>
              الدور
              <select value={newRole} onChange={(event) => setNewRole(event.target.value as AccountRole)}>
                <option value="teacher">معلم</option>
                <option value="reviewer">مراجع</option>
                <option value="owner">مالك</option>
              </select>
            </label>
            <button
              type="button"
              className="primary-button"
              onClick={() => void submitCreateAccount()}
              disabled={busy || newUsername.trim().length < 3 || newDisplayName.trim().length < 2 || newPassword.length < 6}
            >
              <UserPlus size={18} />
              إضافة حساب
            </button>
          </div>

          <div className="account-list">
            {accounts.map((managedAccount) => (
              <article key={managedAccount.id} className={`account-row ${managedAccount.isActive ? '' : 'inactive-account'}`}>
                <div>
                  <strong>{managedAccount.displayName}</strong>
                  <span>@{managedAccount.username} · {roleLabel(managedAccount.role)}</span>
                </div>
                <button
                  type="button"
                  className={managedAccount.isActive ? 'danger-button compact' : 'secondary-button compact'}
                  onClick={() => void onToggleAccount(managedAccount.id, !managedAccount.isActive)}
                  disabled={managedAccount.id === account.id}
                >
                  {managedAccount.isActive ? 'تعطيل' : 'تفعيل'}
                </button>
              </article>
            ))}
          </div>
        </div>
      ) : null}

      <div className="notice-card auth-message">
        <span>{message || 'الحسابات اختيارية في هذه المرحلة، وستصبح أساس ربط المشاريع بالمستخدمين في المرحلة التالية.'}</span>
      </div>
    </section>
  );
}
