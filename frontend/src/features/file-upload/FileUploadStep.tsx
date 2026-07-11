import type { ChangeEvent } from 'react';
import { FileSearch, FileUp, ShieldCheck } from 'lucide-react';
import type { ExtractedTextInfo, PdfLayoutAssetInfo, UploadedFileInfo } from '../../types/project';

interface FileUploadStepProps {
  uploadedFile: UploadedFileInfo | null;
  extractedText: ExtractedTextInfo | null;
  layoutAssets: PdfLayoutAssetInfo[];
  onFileSelected: (file: File | null) => void;
}

function formatFileSize(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

export function FileUploadStep({ uploadedFile, extractedText, layoutAssets, onFileSelected }: FileUploadStepProps) {
  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      onFileSelected(null);
      return;
    }

    onFileSelected(file);
  }

  return (
    <div className="step-grid two-columns">
      <section className="form-card upload-zone">
        <FileUp size={42} />
        <h3>رفع PDF نصي أو صورة</h3>
        <p>
          يدعم المسار الحالي PDF النصي، ويجرّب OCR إنجليزيًا مبدئيًا للصور وPDF المصوّر محدود الصفحات.
        </p>
        <input type="file" accept=".pdf,application/pdf,image/png,image/jpeg,image/webp" onChange={handleFileChange} />
      </section>

      <section className="form-card">
        <div className="section-heading">
          <p className="eyebrow">استخراج أولي</p>
          <h3>حالة الملف</h3>
        </div>

        {uploadedFile ? (
          <div className="file-summary">
            <strong>{uploadedFile.name}</strong>
            <span>النوع: {uploadedFile.type}</span>
            <span>الحجم: {formatFileSize(uploadedFile.size)}</span>
            <button type="button" className="secondary-button compact" onClick={() => onFileSelected(null)}>
              إزالة الملف
            </button>
          </div>
        ) : (
          <div className="empty-state">لم يتم اختيار ملف بعد.</div>
        )}

        {extractedText ? (
          <div className={`notice-card ${extractedText.isTextBased ? 'success-card' : 'warning-card'}`}>
            <FileSearch size={22} />
            <span>
              {extractedText.message} الصفحات: {extractedText.pageCount}، الأحرف: {extractedText.characterCount}.
            </span>
          </div>
        ) : (
          <div className="notice-card">
            <ShieldCheck size={22} />
            <span>OCR يعمل مبدئيًا على الصور الإنجليزية الواضحة وعلى PDF المصوّر محدود الصفحات. وعند رفع PDF تُنشأ لقطات تخطيط للمراجعة البشرية.</span>
          </div>
        )}
      {layoutAssets.length > 0 ? (
          <div className="notice-card success-card">
            <FileSearch size={22} />
            <span>تم استخراج {layoutAssets.length} لقطة تخطيط من PDF لمراجعة الرسوم والجداول في خطوة الاستخراج.</span>
          </div>
        ) : null}
      </section>
    </div>
  );
}
