import { useEffect, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Cloud,
  Download,
  FileText,
  Link2,
  Loader2,
  RefreshCw,
  Trash2,
} from "lucide-react";
import {
  attachGoogleDriveCurriculumSource,
  checkProjectCurriculumSourceUpdates,
  deleteProjectCurriculumSource,
  getGoogleDriveSourceStatus,
  listGoogleDriveSourceFiles,
  listProjectCurriculumSources,
} from "../../services/api";
import type {
  CurriculumSourceAttachment,
  GoogleDriveSourceFile,
  GoogleDriveSourceStatus,
} from "../../types/project";

type GoogleDriveSourcePanelProps = {
  projectId: string | null;
  grade: number;
  scienceDomain: string;
  semesterId: string;
  subjectId: string;
  unitId: string | null;
};

function refreshLabel(
  status: CurriculumSourceAttachment["sourceRefreshStatus"],
) {
  if (status === "current") return "محدث";
  if (status === "changed") return "تغيّر المصدر";
  if (status === "missing") return "المصدر مفقود";
  if (status === "unverifiable") return "تعذر التحقق";
  return "لم يُفحص";
}

export default function GoogleDriveSourcePanel({
  projectId,
  grade,
  scienceDomain,
  semesterId,
  subjectId,
  unitId,
}: GoogleDriveSourcePanelProps) {
  const [status, setStatus] =
    useState<GoogleDriveSourceStatus | null>(null);
  const [files, setFiles] =
    useState<GoogleDriveSourceFile[]>([]);
  const [attached, setAttached] = useState<
    CurriculumSourceAttachment[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [workingId, setWorkingId] =
    useState<string | null>(null);
  const [refreshSummary, setRefreshSummary] =
    useState("");

  async function refresh() {
    setLoading(true);
    setError("");
    try {
      const currentStatus =
        await getGoogleDriveSourceStatus();
      setStatus(currentStatus);

      if (currentStatus.ready) {
        const listing =
          await listGoogleDriveSourceFiles();
        setStatus(listing.status);
        setFiles(listing.files);
      } else {
        setFiles([]);
      }

      setAttached(
        projectId
          ? await listProjectCurriculumSources(projectId)
          : [],
      );
    } catch {
      setError("تعذر قراءة المصادر المرتبطة.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, [
    projectId,
    grade,
    scienceDomain,
    semesterId,
    subjectId,
    unitId,
  ]);

  async function attachFile(fileId: string) {
    if (!projectId) {
      setError("يجب فتح مشروع قبل ربط المصدر.");
      return;
    }

    setWorkingId(fileId);
    setError("");
    try {
      await attachGoogleDriveCurriculumSource(
        projectId,
        {
          sourceFileId: fileId,
          grade,
          scienceDomain,
          semesterId,
          subjectId,
          unitId,
          sourceDocumentType: "student_book",
        },
      );
      setAttached(
        await listProjectCurriculumSources(projectId),
      );
    } catch {
      setError("تعذر حفظ المصدر وربطه بالمنهج.");
    } finally {
      setWorkingId(null);
    }
  }

  async function removeAttachment(
    attachmentId: string,
  ) {
    if (!projectId) return;

    setWorkingId(attachmentId);
    setError("");
    try {
      await deleteProjectCurriculumSource(
        projectId,
        attachmentId,
      );
      setAttached(
        await listProjectCurriculumSources(projectId),
      );
    } catch {
      setError("تعذر حذف ارتباط المصدر.");
    } finally {
      setWorkingId(null);
    }
  }

  async function checkForSourceUpdates() {
    if (!projectId) {
      setError(
        "يجب فتح مشروع قبل فحص تحديثات المصادر.",
      );
      return;
    }

    setWorkingId("refresh-check");
    setError("");
    setRefreshSummary("");

    try {
      const result =
        await checkProjectCurriculumSourceUpdates(
          projectId,
        );
      setAttached(result.items);
      setRefreshSummary(
        `تم فحص ${result.checkedCount} مصدرًا: ` +
          `${result.changedCount} متغير، ` +
          `${result.missingCount} مفقود، ` +
          `${result.unverifiableCount} غير قابل للتحقق.`,
      );
    } catch {
      setError("تعذر فحص تحديثات المصادر.");
    } finally {
      setWorkingId(null);
    }
  }

  function isAttached(file: GoogleDriveSourceFile) {
    return attached.some(
      (item) =>
        item.provider === file.provider &&
        item.sourceFileId === file.id &&
        item.checksum === file.checksum,
    );
  }

  const visibleAttachments = attached.filter(
    (item) =>
      item.grade === grade &&
      item.scienceDomain === scienceDomain &&
      item.semesterId === semesterId &&
      item.subjectId === subjectId &&
      (unitId ? item.unitId === unitId : true),
  );

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

        <div className="cloud-source-heading-actions">
          <button
            type="button"
            className="secondary-button compact"
            onClick={() => void refresh()}
            disabled={loading}
          >
            {loading ? (
              <Loader2
                size={16}
                className="spin-icon"
              />
            ) : (
              <RefreshCw size={16} />
            )}
            تحديث القائمة
          </button>

          <button
            type="button"
            className="secondary-button compact"
            onClick={() =>
              void checkForSourceUpdates()
            }
            disabled={
              !projectId ||
              workingId === "refresh-check"
            }
          >
            {workingId === "refresh-check" ? (
              <Loader2
                size={16}
                className="spin-icon"
              />
            ) : (
              <RefreshCw size={16} />
            )}
            فحص التحديثات
          </button>
        </div>
      </div>

      {!projectId ? (
        <div className="cloud-source-state is-disabled">
          <AlertTriangle size={20} />
          افتح مشروعًا قبل حفظ المصادر.
        </div>
      ) : null}

      {loading ? (
        <div className="cloud-source-state">
          <Loader2
            size={20}
            className="spin-icon"
          />
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
              status?.ready
                ? "is-ready"
                : "is-disabled"
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
            <code>
              {status?.mode ?? "disabled"}
            </code>
          </div>

          {refreshSummary ? (
            <div className="cloud-refresh-summary">
              {refreshSummary}
            </div>
          ) : null}

          {visibleAttachments.length > 0 ? (
            <div className="cloud-linked-sources">
              <h3>
                المصادر المرتبطة بهذا المنهج
              </h3>
              {visibleAttachments.map((item) => (
                <article key={item.id}>
                  <Link2 size={18} />
                  <div>
                    <strong>{item.fileName}</strong>
                    <span>
                      الصف {item.grade} ·{" "}
                      {item.sourceDocumentType}
                    </span>
                    <span
                      className={
                        `cloud-refresh-badge ` +
                        `is-${item.sourceRefreshStatus}`
                      }
                    >
                      {refreshLabel(
                        item.sourceRefreshStatus,
                      )}
                    </span>
                    {item.refreshMessage ? (
                      <small>
                        {item.refreshMessage}
                      </small>
                    ) : null}
                  </div>
                  <button
                    type="button"
                    className="secondary-button compact"
                    disabled={workingId === item.id}
                    onClick={() =>
                      void removeAttachment(item.id)
                    }
                  >
                    {workingId === item.id ? (
                      <Loader2
                        size={15}
                        className="spin-icon"
                      />
                    ) : (
                      <Trash2 size={15} />
                    )}
                    حذف الربط
                  </button>
                </article>
              ))}
            </div>
          ) : null}

          {status?.ready ? (
            <div className="cloud-source-file-list">
              {files.map((file) => {
                const linked = isAttached(file);
                return (
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
                              Math.round(
                                file.sizeBytes / 1024,
                              ),
                            )} كيلوبايت`
                          : "الحجم غير متاح"}
                      </small>
                    </div>
                    <button
                      type="button"
                      className="secondary-button compact"
                      disabled={
                        linked ||
                        !projectId ||
                        workingId === file.id
                      }
                      onClick={() =>
                        void attachFile(file.id)
                      }
                    >
                      {workingId === file.id ? (
                        <Loader2
                          size={16}
                          className="spin-icon"
                        />
                      ) : linked ? (
                        <CheckCircle2 size={16} />
                      ) : (
                        <Download size={16} />
                      )}
                      {linked
                        ? "مرتبط"
                        : "استيراد وربط"}
                    </button>
                  </article>
                );
              })}
            </div>
          ) : null}
        </>
      )}
    </section>
  );
}
