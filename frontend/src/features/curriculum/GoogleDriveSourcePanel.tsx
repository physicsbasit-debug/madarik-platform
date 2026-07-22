import { useEffect, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Cloud,
  Download,
  FileText,
  Loader2,
  RefreshCw,
} from "lucide-react";
import {
  getGoogleDriveSourceStatus,
  importGoogleDriveSourceFile,
  listGoogleDriveSourceFiles,
} from "../../services/api";
import type {
  GoogleDriveImportResult,
  GoogleDriveSourceFile,
  GoogleDriveSourceStatus,
} from "../../types/project";

export default function GoogleDriveSourcePanel() {
  const [status, setStatus] =
    useState<GoogleDriveSourceStatus | null>(null);
  const [files, setFiles] = useState<GoogleDriveSourceFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [importingId, setImportingId] = useState<string | null>(null);
  const [importResult, setImportResult] =
    useState<GoogleDriveImportResult | null>(null);

  async function refresh() {
    setLoading(true);
    setError("");
    try {
      const currentStatus = await getGoogleDriveSourceStatus();
      setStatus(currentStatus);
      if (currentStatus.ready) {
        const listing = await listGoogleDriveSourceFiles();
        setStatus(listing.status);
        setFiles(listing.files);
      } else {
        setFiles([]);
      }
    } catch {
      setError("تعذر قراءة حالة Google Drive من الخادم.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function importFile(fileId: string) {
    setImportingId(fileId);
    setImportResult(null);
    setError("");
    try {
      setImportResult(await importGoogleDriveSourceFile(fileId));
    } catch {
      setError("تعذر استيراد الملف المحدد.");
    } finally {
      setImportingId(null);
    }
  }

  return (
    <section className="google-drive-source-panel">
      <div className="google-drive-panel-heading">
        <div>
          <Cloud size={23} />
          <div>
            <span>مصدر سحابي</span>
            <h2>Google Drive</h2>
          </div>
        </div>
        <button
          type="button"
          className="secondary-button compact"
          onClick={() => void refresh()}
          disabled={loading}
        >
          {loading ? (
            <Loader2 size={16} className="spin-icon" />
          ) : (
            <RefreshCw size={16} />
          )}
          تحديث
        </button>
      </div>

      {loading ? (
        <div className="cloud-source-state">
          <Loader2 size={20} className="spin-icon" />
          جارٍ قراءة حالة المصدر...
        </div>
      ) : error ? (
        <div className="cloud-source-state is-error">
          <AlertTriangle size={20} />
          {error}
        </div>
      ) : (
        <>
          <div
            className={`cloud-source-state ${
              status?.ready ? "is-ready" : "is-disabled"
            }`}
          >
            {status?.ready ? (
              <CheckCircle2 size={20} />
            ) : (
              <AlertTriangle size={20} />
            )}
            <div>
              <strong>
                {status?.ready
                  ? "المصدر جاهز للقراءة"
                  : "المصدر غير مفعل"}
              </strong>
              <span>{status?.reason}</span>
            </div>
            <code>{status?.mode ?? "disabled"}</code>
          </div>

          {status?.ready ? (
            <div className="cloud-source-file-list">
              {files.length > 0 ? (
                files.map((file) => (
                  <article key={file.id}>
                    <div className="cloud-source-file-icon">
                      <FileText size={21} />
                    </div>
                    <div className="cloud-source-file-copy">
                      <strong>{file.fileName}</strong>
                      <span>{file.mimeType}</span>
                      <small>
                        {file.sizeBytes
                          ? `${Math.max(
                              1,
                              Math.round(file.sizeBytes / 1024),
                            )} كيلوبايت`
                          : "الحجم غير متاح"}
                      </small>
                    </div>
                    <button
                      type="button"
                      className="secondary-button compact"
                      disabled={importingId === file.id}
                      onClick={() => void importFile(file.id)}
                    >
                      {importingId === file.id ? (
                        <Loader2 size={16} className="spin-icon" />
                      ) : (
                        <Download size={16} />
                      )}
                      استيراد
                    </button>
                  </article>
                ))
              ) : (
                <div className="cloud-source-empty">
                  لا توجد ملفات مدعومة في المجلد المحدد.
                </div>
              )}
            </div>
          ) : null}
        </>
      )}

      {importResult ? (
        <div className="cloud-source-import-result">
          <CheckCircle2 size={19} />
          <div>
            <strong>
              تم استيراد {importResult.source.fileName}
            </strong>
            <span>
              {importResult.byteCount.toLocaleString("ar")} بايت
            </span>
          </div>
        </div>
      ) : null}
    </section>
  );
}
