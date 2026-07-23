import { useEffect, useState } from "react";
import {
  ArrowRight,
  CheckCircle2,
  Cloud,
  Download,
  History,
  Link2,
  Plus,
  RefreshCw,
  Trash2,
} from "lucide-react";
import {
  acceptCloudSourceVersion,
  createOneDriveSourceFromUrl,
  deleteCloudSource,
  getOneDriveProviderStatus,
  intakeCloudSourceVersion,
  listCloudSources,
  listCloudSourceVersions,
  refreshCloudSourceVersion,
} from "../../services/api";
import type {
  CloudSource,
  CloudSourceType,
  CloudSourceVersion,
  OneDriveProviderStatus,
  ProjectSession,
} from "../../types/project";

interface Props {
  projectId: string | null;
  onReturnHome: () => void;
  onProjectIntake: (project: ProjectSession) => void;
}

const providerLabels = {
  google_drive: "Google Drive",
  onedrive: "OneDrive",
} as const;

const versionStateLabels = {
  detected: "بانتظار الاعتماد",
  accepted: "معتمدة",
  superseded: "سابقة",
} as const;

function formatBytes(value: number | null): string {
  if (value === null) return "غير معروف";
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`;
  }
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

export default function CloudSources({
  projectId,
  onReturnHome,
  onProjectIntake,
}: Props) {
  const [items, setItems] = useState<CloudSource[]>([]);
  const [displayName, setDisplayName] = useState("");
  const [webUrl, setWebUrl] = useState("");
  const [sourceType, setSourceType] =
    useState<CloudSourceType>("file");
  const [providerStatus, setProviderStatus] =
    useState<OneDriveProviderStatus | null>(null);
  const [versionsBySource, setVersionsBySource] = useState<
    Record<string, CloudSourceVersion[]>
  >({});
  const [expandedSourceId, setExpandedSourceId] =
    useState<string | null>(null);
  const [workingKey, setWorkingKey] =
    useState<string | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    void Promise.all([
      listCloudSources(),
      getOneDriveProviderStatus(),
    ])
      .then(([sources, status]) => {
        setItems(sources);
        setProviderStatus(status);
      })
      .catch(() =>
        setError("تعذر تحميل مصادر السحابة."),
      );
  }, []);

  function updateSource(source: CloudSource) {
    setItems((current) =>
      current.map((item) =>
        item.id === source.id ? source : item,
      ),
    );
  }

  async function loadVersions(sourceId: string) {
    const result = await listCloudSourceVersions(sourceId);
    setVersionsBySource((current) => ({
      ...current,
      [sourceId]: result.items,
    }));
  }

  async function add() {
    if (!displayName.trim() || !webUrl.trim()) {
      setError("الاسم والرابط مطلوبان.");
      return;
    }
    setError("");
    setMessage("");
    try {
      const created = await createOneDriveSourceFromUrl({
        displayName: displayName.trim(),
        webUrl: webUrl.trim(),
        sourceProjectId: projectId,
        sourceType,
      });
      setItems((current) => [created, ...current]);
      setDisplayName("");
      setWebUrl("");
      setMessage("تم حفظ مصدر OneDrive.");
    } catch {
      setError(
        "تعذر حفظ الرابط. تأكد أنه رابط OneDrive أو SharePoint صالح.",
      );
    }
  }

  async function refreshVersion(sourceId: string) {
    setWorkingKey(`refresh:${sourceId}`);
    setError("");
    setMessage("");
    try {
      const result = await refreshCloudSourceVersion(
        sourceId,
        true,
      );
      updateSource(result.source);
      await loadVersions(sourceId);
      setExpandedSourceId(sourceId);
      setMessage(result.message);
    } catch (refreshError) {
      setError(
        refreshError instanceof Error
          ? refreshError.message
          : "تعذر تحديث المصدر.",
      );
    } finally {
      setWorkingKey(null);
    }
  }

  async function toggleVersions(sourceId: string) {
    if (expandedSourceId === sourceId) {
      setExpandedSourceId(null);
      return;
    }
    setWorkingKey(`versions:${sourceId}`);
    setError("");
    try {
      await loadVersions(sourceId);
      setExpandedSourceId(sourceId);
    } catch {
      setError("تعذر تحميل سجل النسخ.");
    } finally {
      setWorkingKey(null);
    }
  }

  async function acceptVersion(
    sourceId: string,
    versionId: string,
  ) {
    setWorkingKey(`accept:${versionId}`);
    setError("");
    try {
      const result = await acceptCloudSourceVersion(
        sourceId,
        versionId,
      );
      updateSource(result.source);
      await loadVersions(sourceId);
      setMessage(result.message);
    } catch (acceptError) {
      setError(
        acceptError instanceof Error
          ? acceptError.message
          : "تعذر اعتماد النسخة.",
      );
    } finally {
      setWorkingKey(null);
    }
  }

  async function intakeVersion(
    sourceId: string,
    versionId: string,
  ) {
    setWorkingKey(`intake:${versionId}`);
    setError("");
    try {
      const result = await intakeCloudSourceVersion(
        sourceId,
        versionId,
        projectId,
      );
      updateSource(result.source);
      await loadVersions(sourceId);
      setMessage(result.message);
      onProjectIntake(result.project);
    } catch (intakeError) {
      setError(
        intakeError instanceof Error
          ? intakeError.message
          : "تعذر إدخال النسخة إلى المشروع.",
      );
    } finally {
      setWorkingKey(null);
    }
  }

  async function remove(sourceId: string) {
    setWorkingKey(`delete:${sourceId}`);
    try {
      await deleteCloudSource(sourceId);
      setItems((current) =>
        current.filter((item) => item.id !== sourceId),
      );
      setVersionsBySource((current) => {
        const next = { ...current };
        delete next[sourceId];
        return next;
      });
    } catch {
      setError("تعذر حذف المصدر.");
    } finally {
      setWorkingKey(null);
    }
  }

  return (
    <main className="cloud-sources" dir="rtl">
      <header className="cloud-sources-header">
        <div>
          <span>
            <Cloud size={18} />
            مصادر السحابة
          </span>
          <h1>تحديث المصادر وإدارة النسخ</h1>
          <p>
            تُحفظ النسخ الجديدة منفصلة، ولا تدخل المشروع
            حتى تعتمدها أنت. فكرة جريئة: ألّا يستبدل النظام
            ملفاتك في صمت.
          </p>
        </div>
        <button
          type="button"
          className="secondary-button"
          onClick={onReturnHome}
        >
          <ArrowRight size={18} />
          العودة
        </button>
      </header>

      {providerStatus ? (
        <section
          className={`cloud-provider-status ${
            providerStatus.configured
              ? "is-ready"
              : "is-disabled"
          }`}
        >
          <div>
            <strong>Microsoft Graph</strong>
            <span>
              {providerStatus.configured
                ? "مهيأ"
                : "غير مهيأ"}
            </span>
          </div>
          <p>{providerStatus.message}</p>
          <small>
            سجل النسخ لا يعرض مفاتيح أو روابط تنزيل مؤقتة.
          </small>
        </section>
      ) : null}

      <section className="cloud-source-form">
        <h2>إضافة مصدر OneDrive</h2>
        <div>
          <input
            placeholder="اسم المصدر"
            value={displayName}
            onChange={(event) =>
              setDisplayName(event.target.value)
            }
          />
          <select
            value={sourceType}
            onChange={(event) =>
              setSourceType(
                event.target.value as CloudSourceType,
              )
            }
          >
            <option value="file">ملف</option>
            <option value="folder">مجلد</option>
          </select>
          <input
            className="cloud-source-url"
            placeholder="رابط OneDrive أو SharePoint"
            value={webUrl}
            onChange={(event) =>
              setWebUrl(event.target.value)
            }
          />
        </div>
        <button
          type="button"
          className="primary-button"
          onClick={() => void add()}
        >
          <Plus size={17} />
          حفظ المصدر
        </button>
      </section>

      {message ? (
        <div className="cloud-source-message">
          {message}
        </div>
      ) : null}
      {error ? (
        <div className="cloud-source-error">
          {error}
        </div>
      ) : null}

      <section className="cloud-source-list">
        <h2>المصادر المحفوظة</h2>
        {items.length ? (
          items.map((item) => {
            const versions =
              versionsBySource[item.id] ?? [];
            const expanded =
              expandedSourceId === item.id;

            return (
              <article key={item.id}>
                <div className="cloud-source-heading">
                  <div>
                    <span>
                      {providerLabels[item.provider]}
                    </span>
                    <h3>{item.displayName}</h3>
                  </div>
                  <span
                    className={`cloud-sync-status ${item.syncStatus}`}
                  >
                    {item.syncStatus}
                  </span>
                </div>
                <p>
                  النوع:{" "}
                  {item.sourceType === "file"
                    ? "ملف"
                    : "مجلد"}
                </p>
                <a
                  href={item.webUrl}
                  target="_blank"
                  rel="noreferrer"
                >
                  <Link2 size={15} />
                  فتح المصدر
                </a>
                <div className="cloud-source-actions">
                  <button
                    type="button"
                    className="primary-button compact"
                    disabled={
                      workingKey !== null ||
                      item.provider !== "onedrive"
                    }
                    onClick={() =>
                      void refreshVersion(item.id)
                    }
                  >
                    <RefreshCw size={15} />
                    تحديث وحفظ نسخة
                  </button>
                  <span className="cloud-refresh-note">
                    فحص المزامنة وتنزيل الملف
                  </span>
                  <button
                    type="button"
                    className="secondary-button compact"
                    disabled={workingKey !== null}
                    onClick={() =>
                      void toggleVersions(item.id)
                    }
                  >
                    <History size={15} />
                    سجل النسخ
                  </button>
                  <button
                    type="button"
                    className="secondary-button compact"
                    disabled={workingKey !== null}
                    onClick={() => void remove(item.id)}
                  >
                    <Trash2 size={15} />
                    حذف
                  </button>
                </div>

                {expanded ? (
                  <section className="cloud-version-history">
                    <h4>سجل النسخ</h4>
                    {versions.length ? (
                      versions.map((version) => (
                        <div
                          key={version.id}
                          className={`cloud-version-card ${version.state}`}
                        >
                          <div>
                            <strong>
                              {versionStateLabels[
                                version.state
                              ]}
                            </strong>
                            <span>
                              {new Date(
                                version.detectedAt,
                              ).toLocaleString("ar-OM")}
                            </span>
                          </div>
                          <p>
                            الحجم: {formatBytes(
                              version.sizeBytes,
                            )}
                          </p>
                          <p>
                            الملف المحلي:{" "}
                            {version.localPath
                              ? "جاهز"
                              : "غير مُنزّل"}
                          </p>
                          <div className="cloud-version-actions">
                            {version.state === "detected" ? (
                              <button
                                type="button"
                                className="primary-button compact"
                                disabled={workingKey !== null}
                                onClick={() =>
                                  void acceptVersion(
                                    item.id,
                                    version.id,
                                  )
                                }
                              >
                                <CheckCircle2 size={15} />
                                اعتماد النسخة
                              </button>
                            ) : null}
                            {version.state === "accepted" ? (
                              <button
                                type="button"
                                className="secondary-button compact"
                                disabled={
                                  workingKey !== null ||
                                  !version.localPath
                                }
                                onClick={() =>
                                  void intakeVersion(
                                    item.id,
                                    version.id,
                                  )
                                }
                              >
                                <Download size={15} />
                                {projectId
                                  ? "إدخال إلى المشروع"
                                  : "إنشاء مشروع من النسخة"}
                              </button>
                            ) : null}
                            {version.intakeProjectId ? (
                              <span className="cloud-version-intake-note">
                                أُدخلت إلى مشروع
                              </span>
                            ) : null}
                          </div>
                        </div>
                      ))
                    ) : (
                      <p>
                        لم تُحفظ نسخة بعد. شغّل التحديث
                        الأول لتثبيت النسخة الأساسية.
                      </p>
                    )}
                  </section>
                ) : null}
              </article>
            );
          })
        ) : (
          <p>لا توجد مصادر سحابية محفوظة.</p>
        )}
      </section>
    </main>
  );
}
