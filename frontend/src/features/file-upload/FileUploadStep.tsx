import {
  useEffect,
  useState,
  type ChangeEvent,
  type DragEvent,
} from 'react';
import {
  CheckCircle2,
  FileSearch,
  FileUp,
  Loader2,
  RefreshCw,
  ShieldCheck,
  Trash2,
} from 'lucide-react';
import type {
  ExtractedTextInfo,
  InitialExtractionStatus,
  PdfLayoutAssetInfo,
  UploadedFileInfo,
} from '../../types/project';

interface FileUploadStepProps {
  uploadedFile: UploadedFileInfo | null;
  extractedText: ExtractedTextInfo | null;
  layoutAssets: PdfLayoutAssetInfo[];
  onFileSelected: (file: File | null) => void;
  canParseQuestions: boolean;
  isBusy: boolean;
  initialExtractionStatus: InitialExtractionStatus;
  onRetryInitialExtraction: () => void;
  onParseQuestions: () => void;
}

function formatFileSize(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function phaseLabel(status: InitialExtractionStatus) {
  switch (status.phase) {
    case 'uploading':
      return 'رفع الملف';
    case 'reading':
      return 'قراءة PDF';
    case 'ocr':
      return 'التعرّف الضوئي OCR';
    case 'success':
      return 'اكتملت القراءة';
    case 'error':
      return 'تعذرت القراءة';
    default:
      return 'بانتظار الملف';
  }
}

export function FileUploadStep({
  uploadedFile,
  extractedText,
  layoutAssets,
  onFileSelected,
  canParseQuestions,
  isBusy,
  initialExtractionStatus,
  onRetryInitialExtraction,
  onParseQuestions,
}: FileUploadStepProps) {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [isDragActive, setIsDragActive] = useState(false);

  useEffect(() => {
    if (!initialExtractionStatus.startedAt) {
      setElapsedSeconds(0);
      return;
    }

    const updateElapsed = () => {
      setElapsedSeconds(
        Math.max(
          0,
          Math.round((Date.now() - initialExtractionStatus.startedAt!) / 1000),
        ),
      );
    };

    updateElapsed();
    if (!['uploading', 'reading', 'ocr'].includes(initialExtractionStatus.phase)) {
      return;
    }

    const timer = window.setInterval(updateElapsed, 1000);
    return () => window.clearInterval(timer);
  }, [initialExtractionStatus.phase, initialExtractionStatus.startedAt]);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    onFileSelected(file);
    event.target.value = '';
  }

  function handleDragOver(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    if (!extractionIsRunning) {
      event.dataTransfer.dropEffect = 'copy';
      setIsDragActive(true);
    }
  }

  function handleDragLeave(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
      setIsDragActive(false);
    }
  }

  function handleDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    setIsDragActive(false);

    if (extractionIsRunning) return;

    const file = event.dataTransfer.files?.[0] ?? null;
    if (file) {
      onFileSelected(file);
    }
  }

  const extractionIsRunning = ['uploading', 'reading', 'ocr'].includes(
    initialExtractionStatus.phase,
  );

  return (
    <section className="start-column-card start-upload-card">
      <div className="section-heading">
        <p className="eyebrow">رفع الورقة</p>
        <h3>اختر ملف الاختبار</h3>
        <p>PDF نصي أو مصوّر، أو صورة واضحة بصيغة PNG أو JPG.</p>
      </div>

      <label
        className={`start-upload-zone ${isDragActive ? 'is-drag-active' : ''}`}
        onDragEnter={handleDragOver}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <FileUp size={44} />
        <strong>
          {uploadedFile ? 'استبدال الملف الحالي' : 'اسحب الملف هنا أو اختره'}
        </strong>
        <span>PDF · PNG · JPG · WEBP</span>
        <span className="start-upload-button">اختيار ملف</span>
        <input
          type="file"
          accept=".pdf,application/pdf,image/png,image/jpeg,image/webp"
          onChange={handleFileChange}
          disabled={extractionIsRunning}
        />
      </label>

      {uploadedFile ? (
        <div className="start-file-summary">
          <CheckCircle2 size={22} />
          <div>
            <strong>{uploadedFile.name}</strong>
            <span>
              {uploadedFile.type || 'نوع غير محدد'} ·{' '}
              {formatFileSize(uploadedFile.size)}
            </span>
          </div>
          <button
            type="button"
            className="icon-button danger-icon-button"
            onClick={() => onFileSelected(null)}
            aria-label="إزالة الملف"
            disabled={extractionIsRunning}
          >
            <Trash2 size={18} />
          </button>
        </div>
      ) : null}

      {uploadedFile ? (
        <div
          className={`initial-extraction-progress phase-${initialExtractionStatus.phase}`}
          aria-live="polite"
        >
          <div className="initial-extraction-progress-head">
            <div>
              <span>الاستخراج الأولي</span>
              <strong>{phaseLabel(initialExtractionStatus)}</strong>
            </div>
            {extractionIsRunning ? (
              <Loader2 size={22} className="spin-icon" />
            ) : initialExtractionStatus.phase === 'success' ? (
              <CheckCircle2 size={22} />
            ) : initialExtractionStatus.phase === 'error' ? (
              <RefreshCw size={22} />
            ) : (
              <ShieldCheck size={22} />
            )}
          </div>
          <p>{initialExtractionStatus.message}</p>
          {initialExtractionStatus.startedAt ? (
            <small>الزمن المنقضي: {elapsedSeconds} ثانية</small>
          ) : null}
          {initialExtractionStatus.canRetry ? (
            <button
              type="button"
              className="secondary-button initial-extraction-retry"
              onClick={onRetryInitialExtraction}
              disabled={isBusy}
            >
              <RefreshCw size={17} />
              إعادة المحاولة
            </button>
          ) : null}
        </div>
      ) : null}

      {uploadedFile ? (
        <div className="start-upload-inline-action">
          <button
            type="button"
            className="primary-button start-upload-parse-button"
            onClick={onParseQuestions}
            disabled={!canParseQuestions}
          >
            {isBusy ? (
              <Loader2 size={18} className="spin-icon" />
            ) : (
              <FileSearch size={18} />
            )}
            استخراج الأسئلة
          </button>
          <small>
            {canParseQuestions
              ? 'النص جاهز للاستخراج.'
              : extractionIsRunning
                ? 'القراءة الأولية جارية الآن.'
                : 'سيُفعّل الزر بعد اكتمال قراءة النص.'}
          </small>
        </div>
      ) : null}

      <div className="start-upload-notices">
        {extractedText ? (
          <div
            className={`start-upload-notice ${
              extractedText.isTextBased ? 'is-success' : 'is-warning'
            }`}
          >
            <FileSearch size={20} />
            <div>
              <strong>{extractedText.message}</strong>
              <span>
                {extractedText.pageCount} صفحة ·{' '}
                {extractedText.characterCount} حرفًا
              </span>
            </div>
          </div>
        ) : (
          <div className="start-upload-notice">
            <ShieldCheck size={20} />
            <div>
              <strong>استخراج أولي منفصل</strong>
              <span>
                يقرأ النظام النص أولًا. تحليل الرسوم والقص مؤجل إلى المراجعة.
              </span>
            </div>
          </div>
        )}

        {layoutAssets.length > 0 ? (
          <div className="start-upload-notice is-success">
            <FileSearch size={20} />
            <div>
              <strong>عناصر بصرية محفوظة</strong>
              <span>{layoutAssets.length} لقطة جاهزة للمراجعة.</span>
            </div>
          </div>
        ) : null}
      </div>
    </section>
  );
}
