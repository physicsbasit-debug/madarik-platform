import type { ChangeEvent } from 'react';
import { FileSearch, FileUp, ShieldCheck } from 'lucide-react';
import type { ExtractedTextInfo, UploadedFileInfo } from '../../types/project';

interface FileUploadStepProps {
  uploadedFile: UploadedFileInfo | null;
  extractedText: ExtractedTextInfo | null;
  onFileSelected: (file: File | null) => void;
}

function formatFileSize(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

export function FileUploadStep({ uploadedFile, extractedText, onFileSelected }: FileUploadStepProps) {
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
        <h3>رفع PDF نصي</h3>
        <p>
          في Phase 1-C يتم رفع ملف PDF حقيقي إلى Backend لاستخراج النص القابل للتحديد فقط. ملفات PDF المصوّرة ستحتاج OCR لاحقًا، فلا نكذب على الورق.
        </p>
        <input type="file" accept=".pdf,application/pdf" onChange={handleFileChange} />
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
            <span>لا يتم تشغيل OCR في هذه المرحلة. المطلوب الآن إثبات قراءة PDF النصي فقط، خطوة خطوة بلا بهلوانيات.</span>
          </div>
        )}
      </section>
    </div>
  );
}
