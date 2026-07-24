import {
  Activity,
  BookOpenText,
  BrainCircuit,
  ChevronDown,
  CircleUserRound,
  Cloud,
  Download,
  FileStack,
  FlaskConical,
  FolderKanban,
  Gauge,
  LibraryBig,
  Menu,
  Network,
  Plus,
  Save,
  Settings,
  Upload,
  WandSparkles,
  Wifi,
  WifiOff,
  X,
} from "lucide-react";
import { useState, type ReactNode } from "react";
import type {
  ApiConnectionStatus,
  AuthAccountPublic,
  ProjectMetadata,
} from "../types/project";

export type PlatformSection =
  | "home"
  | "quick"
  | "professional"
  | "cloud-sources"
  | "curriculum"
  | "question-bank"
  | "assessment"
  | "differentiated-activities"
  | "scientific-diagrams";

type NavigationItem = {
  key: PlatformSection;
  label: string;
  description: string;
  icon: typeof Gauge;
};

type NavigationGroup = {
  label: string;
  items: NavigationItem[];
};

const navigationGroups: NavigationGroup[] = [
  {
    label: "نظرة عامة",
    items: [
      {
        key: "home",
        label: "لوحة التحكم",
        description: "ملخص المنصة والعمل الحالي",
        icon: Gauge,
      },
      {
        key: "professional",
        label: "المشاريع والمعالجة",
        description: "استيراد الورقة ومراجعتها وتصديرها",
        icon: FolderKanban,
      },
      {
        key: "quick",
        label: "الترجمة السريعة",
        description: "رحلة مختصرة للإنجاز المباشر",
        icon: WandSparkles,
      },
    ],
  },
  {
    label: "المحتوى والمصادر",
    items: [
      {
        key: "cloud-sources",
        label: "المصادر السحابية",
        description: "Google Drive وOneDrive وسجل النسخ",
        icon: Cloud,
      },
      {
        key: "curriculum",
        label: "المناهج والدروس",
        description: "الصفوف والوحدات ونواتج التعلم",
        icon: BookOpenText,
      },
      {
        key: "question-bank",
        label: "بنك الأسئلة",
        description: "الأسئلة المعتمدة والقابلة لإعادة الاستخدام",
        icon: LibraryBig,
      },
    ],
  },
  {
    label: "البناء والإنتاج",
    items: [
      {
        key: "assessment",
        label: "منشئ الاختبارات",
        description: "خطط الاختبارات ونسخ الطلبة",
        icon: FileStack,
      },
      {
        key: "differentiated-activities",
        label: "الأنشطة التعليمية",
        description: "دعم وأساسي ومتقدم وإثرائي",
        icon: BrainCircuit,
      },
      {
        key: "scientific-diagrams",
        label: "الرسوم العلمية",
        description: "مخططات قابلة للتصدير وإعادة الاستخدام",
        icon: Network,
      },
    ],
  },
];

const sectionTitles = Object.fromEntries(
  navigationGroups.flatMap((group) =>
    group.items.map((item) => [item.key, item.label]),
  ),
) as Record<PlatformSection, string>;

interface PlatformShellProps {
  activeSection: PlatformSection;
  onNavigate: (section: PlatformSection) => void;
  metadata: ProjectMetadata;
  apiStatus: ApiConnectionStatus;
  lastSyncNote: string;
  projectId: string | null;
  authAccount: AuthAccountPublic | null;
  isAccountOpen: boolean;
  onAccountOpenChange: (open: boolean) => void;
  accountPanel: ReactNode;
  onDownloadSnapshot: () => void;
  onImportSnapshot: (file: File | null) => void;
  onNewProject: () => void;
  children: ReactNode;
}

function connectionLabel(status: ApiConnectionStatus) {
  if (status === "connected") return "متصل";
  if (status === "syncing") return "جارٍ الحفظ";
  if (status === "connecting") return "جارٍ الاتصال";
  return "وضع محلي";
}

export function PlatformShell({
  activeSection,
  onNavigate,
  metadata,
  apiStatus,
  lastSyncNote,
  projectId,
  authAccount,
  isAccountOpen,
  onAccountOpenChange,
  accountPanel,
  onDownloadSnapshot,
  onImportSnapshot,
  onNewProject,
  children,
}: PlatformShellProps) {
  const [mobileNavigationOpen, setMobileNavigationOpen] = useState(false);
  const isOffline = apiStatus === "offline";

  function navigate(section: PlatformSection) {
    onNavigate(section);
    setMobileNavigationOpen(false);
  }

  return (
    <main className="platform-shell" dir="rtl">
      <button
        type="button"
        className={`platform-nav-backdrop ${mobileNavigationOpen ? "is-visible" : ""}`}
        aria-label="إغلاق قائمة التنقل"
        onClick={() => setMobileNavigationOpen(false)}
      />

      <aside className={`platform-sidebar ${mobileNavigationOpen ? "is-open" : ""}`}>
        <div className="platform-brand-row">
          <div className="platform-brand-mark" aria-hidden="true">
            <FlaskConical size={23} />
          </div>
          <div className="platform-brand-copy">
            <strong>منصة مدارك</strong>
            <small>بناء المحتوى العلمي والتقويم</small>
          </div>
          <button
            type="button"
            className="platform-sidebar-close"
            aria-label="إغلاق القائمة"
            onClick={() => setMobileNavigationOpen(false)}
          >
            <X size={20} />
          </button>
        </div>

        <button
          type="button"
          className="platform-create-button"
          onClick={() => navigate("professional")}
        >
          <Plus size={19} />
          <span>
            <strong>مشروع ورقة جديد</strong>
            <small>استيراد، ترجمة، مراجعة وتصدير</small>
          </span>
        </button>

        <nav className="platform-navigation" aria-label="أقسام منصة مدارك">
          {navigationGroups.map((group) => (
            <section className="platform-nav-group" key={group.label}>
              <p>{group.label}</p>
              {group.items.map((item) => {
                const Icon = item.icon;
                const active = item.key === activeSection;
                return (
                  <button
                    type="button"
                    key={item.key}
                    className={`platform-nav-item ${active ? "is-active" : ""}`}
                    aria-current={active ? "page" : undefined}
                    onClick={() => navigate(item.key)}
                  >
                    <span className="platform-nav-icon">
                      <Icon size={19} />
                    </span>
                    <span>
                      <strong>{item.label}</strong>
                      <small>{item.description}</small>
                    </span>
                  </button>
                );
              })}
            </section>
          ))}
        </nav>

        <div className="platform-sidebar-footer">
          <div className="platform-connection-card" title={lastSyncNote}>
            {isOffline ? <WifiOff size={18} /> : <Wifi size={18} />}
            <span>
              <small>حالة المنصة</small>
              <strong>{connectionLabel(apiStatus)}</strong>
            </span>
            <i className={`platform-connection-dot is-${apiStatus}`} />
          </div>
          <button
            type="button"
            className="platform-account-card"
            onClick={() => onAccountOpenChange(true)}
          >
            <CircleUserRound size={21} />
            <span>
              <strong>{authAccount?.displayName ?? "الحساب والصلاحيات"}</strong>
              <small>{authAccount?.role ?? "إدارة الدخول والحسابات"}</small>
            </span>
            <Settings size={17} />
          </button>
        </div>
      </aside>

      <section className="platform-main">
        <header className="platform-topbar">
          <div className="platform-topbar-title">
            <button
              type="button"
              className="platform-mobile-menu"
              aria-label="فتح قائمة التنقل"
              onClick={() => setMobileNavigationOpen(true)}
            >
              <Menu size={21} />
            </button>
            <div>
              <small>مدارك / مساحة العمل</small>
              <strong>{sectionTitles[activeSection]}</strong>
            </div>
          </div>

          <div className="platform-project-pill" title={metadata.paperTitle || "مشروع جديد"}>
            <Activity size={18} />
            <span>
              <small>المشروع النشط</small>
              <strong>{metadata.paperTitle || "مشروع جديد"}</strong>
            </span>
            <em>{metadata.subject || "علوم"} · {metadata.grade || "الصف"}</em>
          </div>

          <div className="platform-topbar-actions">
            <button
              type="button"
              className="platform-action-button is-quiet"
              onClick={onDownloadSnapshot}
              disabled={!projectId || isOffline}
              title="تصدير نسخة JSON للمشروع"
            >
              <Save size={18} />
              <span>حفظ نسخة</span>
            </button>
            <button
              type="button"
              className="platform-action-button is-primary"
              onClick={onNewProject}
            >
              <Plus size={18} />
              <span>مشروع جديد</span>
            </button>
            <details className="platform-more-menu">
              <summary aria-label="إجراءات المشروع الإضافية">
                <ChevronDown size={19} />
              </summary>
              <div>
                <label>
                  <Upload size={17} />
                  استيراد نسخة JSON
                  <input
                    type="file"
                    accept="application/json,.json"
                    onChange={(event) =>
                      onImportSnapshot(event.target.files?.[0] ?? null)
                    }
                  />
                </label>
                <button
                  type="button"
                  onClick={onDownloadSnapshot}
                  disabled={!projectId || isOffline}
                >
                  <Download size={17} />
                  تنزيل نسخة المشروع
                </button>
              </div>
            </details>
          </div>
        </header>

        <section className="platform-content">{children}</section>
      </section>

      <button
        type="button"
        className={`platform-drawer-backdrop ${isAccountOpen ? "is-visible" : ""}`}
        aria-label="إغلاق لوحة الحساب"
        onClick={() => onAccountOpenChange(false)}
      />
      <aside className={`platform-account-drawer ${isAccountOpen ? "is-open" : ""}`}>
        <header>
          <div>
            <small>إدارة المنصة</small>
            <strong>الحساب والصلاحيات</strong>
          </div>
          <button
            type="button"
            aria-label="إغلاق لوحة الحساب"
            onClick={() => onAccountOpenChange(false)}
          >
            <X size={20} />
          </button>
        </header>
        <div className="platform-account-drawer-content">{accountPanel}</div>
      </aside>
    </main>
  );
}
