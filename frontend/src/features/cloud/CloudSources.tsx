import { useEffect, useState } from "react";
import {
  ArrowRight,
  Cloud,
  Link2,
  Plus,
  RefreshCw,
  Trash2,
} from "lucide-react";
import {
  createOneDriveSourceFromUrl,
  deleteCloudSource,
  getOneDriveProviderStatus,
  listCloudSources,
  syncCloudSource,
} from "../../services/api";
import type {
  CloudSource,
  CloudSourceType,
  OneDriveProviderStatus,
} from "../../types/project";

interface Props {
  projectId: string | null;
  onReturnHome: () => void;
}

const providerLabels = {
  google_drive: "Google Drive",
  onedrive: "OneDrive",
} as const;

export default function CloudSources({
  projectId,
  onReturnHome,
}: Props) {
  const [items, setItems] = useState<CloudSource[]>([]);
  const [displayName, setDisplayName] = useState("");
  const [webUrl, setWebUrl] = useState("");
  const [sourceType, setSourceType] =
    useState<CloudSourceType>("file");
  const [providerStatus, setProviderStatus] =
    useState<OneDriveProviderStatus | null>(null);
  const [workingSourceId, setWorkingSourceId] =
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

  async function add() {
    if (!displayName.trim() || !webUrl.trim()) {
      setError("الاسم والرابط مطلوبان.");
      return;
    }
    setError("");
    setMessage("");
    try {
      const created =
        await createOneDriveSourceFromUrl({
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

  async function synchronize(
    sourceId: string,
    download: boolean,
  ) {
    setWorkingSourceId(sourceId);
    setError("");
    setMessage("");
    try {
      const result = await syncCloudSource(
        sourceId,
        download,
      );
      setItems((current) =>
        current.map((item) =>
          item.id === sourceId
            ? result.source
            : item,
        ),
      );
      setMessage(result.message);
    } catch (syncError) {
      setError(
        syncError instanceof Error
          ? syncError.message
          : "تعذر مزامنة المصدر.",
      );
    } finally {
      setWorkingSourceId(null);
    }
  }

  async function remove(sourceId: string) {
    try {
      await deleteCloudSource(sourceId);
      setItems((current) =>
        current.filter(
          (item) => item.id !== sourceId,
        ),
      );
    } catch {
      setError("تعذر حذف المصدر.");
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
          <h1>
            ربط مصادر Google Drive وOneDrive
          </h1>
          <p>
            Microsoft Graph معطل افتراضيًا حتى
            تضاف بيانات التطبيق في متغيرات البيئة.
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
            لا تُعرض مفاتيح أو أسرار في الواجهة.
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
                event.target
                  .value as CloudSourceType,
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
          items.map((item) => (
            <article key={item.id}>
              <div>
                <span>
                  {providerLabels[item.provider]}
                </span>
                <h3>{item.displayName}</h3>
              </div>
              <p>
                النوع:{" "}
                {item.sourceType === "file"
                  ? "ملف"
                  : "مجلد"}
              </p>
              <p>
                الحالة: {item.syncStatus}
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
                  className="secondary-button compact"
                  disabled={
                    workingSourceId === item.id ||
                    item.provider !== "onedrive"
                  }
                  onClick={() =>
                    void synchronize(
                      item.id,
                      false,
                    )
                  }
                >
                  <RefreshCw size={15} />
                  فحص المزامنة
                </button>
                <button
                  type="button"
                  className="secondary-button compact"
                  disabled={
                    workingSourceId === item.id ||
                    item.provider !== "onedrive"
                  }
                  onClick={() =>
                    void synchronize(
                      item.id,
                      true,
                    )
                  }
                >
                  تنزيل الملف
                </button>
                <button
                  type="button"
                  className="secondary-button compact"
                  disabled={
                    workingSourceId === item.id
                  }
                  onClick={() =>
                    void remove(item.id)
                  }
                >
                  <Trash2 size={15} />
                  حذف
                </button>
              </div>
            </article>
          ))
        ) : (
          <p>لا توجد مصادر سحابية محفوظة.</p>
        )}
      </section>
    </main>
  );
}
