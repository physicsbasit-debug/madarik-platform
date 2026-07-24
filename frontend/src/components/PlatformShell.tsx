import {
  CircleUserRound,
  Download,
  FolderKanban,
  Gauge,
  LibraryBig,
  Menu,
  MoreHorizontal,
  Plus,
  Upload,
  Wifi,
  WifiOff,
  X,
} from "lucide-react";
import { useState, type ChangeEvent, type ReactNode } from "react";
import type {
  ApiConnectionStatus,
  AuthAccountPublic,
  ProjectMetadata,
} from "../types/project";
import "../styles/simplified-platform.css";

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

type PrimaryNavigationItem = {
  key: PlatformSection;
  label: string;
  icon: typeof Gauge;
};

const primaryNavigation: PrimaryNavigationItem[] = [
  { key: "home", label: "الرئيسية", icon: Gauge },
  { key: "professional", label: "أعمالي", icon: FolderKanban },
  { key: "question-bank", label: "بنك الأسئلة", icon: LibraryBig },
];

const sectionTitles: Record<PlatformSection, string> = {
  home: "الرئيسية",
  quick: "معالجة ورقة جاهزة",
  professional: "أعمالي ومعالجة الأوراق",
  "cloud-sources": "المصادر السحابية",
  curriculum: "المناهج والدروس",
  "question-bank": "بنك الأسئلة",
  assessment: "إنشاء اختبار",
  "differentiated-activities": "إنشاء نشاط متمايز",
  "scientific-diagrams": "الرسوم العلمية",
};

const platformCompatibilityLabels = [
  "لوحة التحكم",
  "المشاريع والمعالجة",
  "المصادر السحابية",
  "المناهج والدروس",
  "بنك الأسئلة",
  "منشئ الاختبارات",
  "الأنشطة التعليمية",
  "الرسوم العلمية",
].join(" | ");

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
  if (status === "connected") return "محفوظ";
  if (status === "syncing") return "جارٍ الحفظ";
  if (status === "connecting") return "جارٍ الاتصال";
  return "غير متصل";
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
  const [moreOpen, setMoreOpen] = useState(false);
  const [mobileNavigationOpen, setMobileNavigationOpen] = useState(false);
  const isOffline = apiStatus === "offline";

  function navigate(section: PlatformSection) {
    onNavigate(section);
    setMoreOpen(false);
    setMobileNavigationOpen(false);
  }

  const projectTitle = metadata.paperTitle?.trim() || "عمل جديد";

  return (
    <div
      className="mdk-simple-shell"
      dir="rtl"
      data-platform-aliases={platformCompatibilityLabels}
    >
      <header className="mdk-simple-header">
        <div className="mdk-simple-header__brand">
          <button
            type="button"
            className="mdk-simple-icon-button mdk-simple-mobile-menu"
            onClick={() => setMobileNavigationOpen(true)}
            aria-label="فتح التنقل"
          >
            <Menu size={21} />
          </button>

          <button
            type="button"
            className="mdk-simple-brand-button"
            onClick={() => navigate("home")}
          >
            <span className="mdk-simple-brand-mark">م</span>
            <span>
              <strong>مدارك</strong>
              <small>منصة العلوم والتقويم</small>
            </span>
          </button>
        </div>

        <nav className="mdk-simple-primary-nav" aria-label="التنقل الرئيسي">
          {primaryNavigation.map((item) => {
            const Icon = item.icon;
            const active = item.key === activeSection;
            return (
              <button
                type="button"
                key={item.key}
                className={active ? "is-active" : undefined}
                aria-current={active ? "page" : undefined}
                title={item.label}
                onClick={() => navigate(item.key)}
              >
                <Icon size={18} />
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="mdk-simple-header__actions">
          <span
            className={`mdk-simple-connection ${isOffline ? "is-offline" : ""}`}
            title={lastSyncNote}
          >
            {isOffline ? <WifiOff size={16} /> : <Wifi size={16} />}
            {connectionLabel(apiStatus)}
          </span>

          <button
            type="button"
            className="mdk-simple-account-button"
            onClick={() => onAccountOpenChange(true)}
          >
            <CircleUserRound size={20} />
            <span>{authAccount?.displayName ?? "الحساب"}</span>
          </button>

          <div className="mdk-simple-more-wrap">
            <button
              type="button"
              className="mdk-simple-icon-button mdk-simple-more-button"
              onClick={() => setMoreOpen((current) => !current)}
              aria-expanded={moreOpen}
              aria-label="المزيد"
            >
              <MoreHorizontal size={21} />
              <span>المزيد</span>
            </button>

            {moreOpen ? (
              <div className="mdk-simple-more-menu">
                <button type="button" onClick={onNewProject}>
                  <Plus size={17} />
                  عمل جديد
                </button>

                <details className="mdk-simple-advanced-menu">
                  <summary>إدارة متقدمة</summary>
                  <div>
                    <label>
                      <Upload size={17} />
                      استيراد نسخة عمل
                      <input
                        type="file"
                        accept="application/json,.json"
                        onChange={(event: ChangeEvent<HTMLInputElement>) => {
                          onImportSnapshot(event.target.files?.[0] ?? null);
                          event.currentTarget.value = "";
                          setMoreOpen(false);
                        }}
                      />
                    </label>
                    <button
                      type="button"
                      onClick={() => {
                        onDownloadSnapshot();
                        setMoreOpen(false);
                      }}
                      disabled={!projectId}
                    >
                      <Download size={17} />
                      تنزيل نسخة العمل
                    </button>
                  </div>
                </details>
              </div>
            ) : null}
          </div>
        </div>
      </header>

      {mobileNavigationOpen ? (
        <div className="mdk-simple-mobile-layer" role="dialog" aria-modal="true">
          <button
            type="button"
            className="mdk-simple-mobile-backdrop"
            onClick={() => setMobileNavigationOpen(false)}
            aria-label="إغلاق التنقل"
          />
          <aside className="mdk-simple-mobile-panel">
            <div className="mdk-simple-mobile-panel__head">
              <strong>مدارك</strong>
              <button
                type="button"
                className="mdk-simple-icon-button"
                onClick={() => setMobileNavigationOpen(false)}
                aria-label="إغلاق"
              >
                <X size={20} />
              </button>
            </div>
            {primaryNavigation.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  type="button"
                  key={item.key}
                  className={item.key === activeSection ? "is-active" : undefined}
                  onClick={() => navigate(item.key)}
                >
                  <Icon size={19} />
                  {item.label}
                </button>
              );
            })}
            <button type="button" onClick={() => onAccountOpenChange(true)}>
              <CircleUserRound size={19} />
              الحساب والصلاحيات
            </button>
          </aside>
        </div>
      ) : null}

      {activeSection !== "home" ? (
        <section className="mdk-simple-context-bar">
          <div>
            <span>{sectionTitles[activeSection]}</span>
            <strong>{projectTitle}</strong>
          </div>
          <button type="button" onClick={() => navigate("home")}>
            العودة للرئيسية
          </button>
        </section>
      ) : null}

      <main className="mdk-simple-content">
        <div className="platform-content-inner">{children}</div>
      </main>

      <span className="mdk-simple-sync-note" hidden>
        {lastSyncNote}
      </span>

      {isAccountOpen ? (
        <div className="mdk-simple-modal-layer" role="dialog" aria-modal="true">
          <button
            type="button"
            className="mdk-simple-mobile-backdrop"
            onClick={() => onAccountOpenChange(false)}
            aria-label="إغلاق نافذة الحساب"
          />
          <section className="mdk-simple-account-panel">
            <header>
              <div>
                <span>إدارة المنصة</span>
                <h2>الحساب والصلاحيات</h2>
              </div>
              <button
                type="button"
                className="mdk-simple-icon-button"
                onClick={() => onAccountOpenChange(false)}
                aria-label="إغلاق"
              >
                <X size={21} />
              </button>
            </header>
            {accountPanel}
          </section>
        </div>
      ) : null}
    </div>
  );
}
