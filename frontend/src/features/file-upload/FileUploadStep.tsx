import type { ChangeEvent } from 'react';
import { FileUp, ShieldCheck } from 'lucide-react';
import type { UploadedFileInfo } from '../../types/project';

interface FileUploadStepProps {
  uploadedFile: UploadedFileInfo | null;
  onFileSelected: (fileInfo: UploadedFileInfo | null) => void;
}

function formatFileSize(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

export function FileUploadStep({ uploadedFile, onFileSelected }: FileUploadStepProps) {
  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      onFileSelected(null);
      return;
    }

    onFileSelected({ name: file.name, size: file.size, type: file.type || 'غير معروف' });
  }

  return (
    <div className="step-grid two-columns">
      <section className="form-card upload-zone">
        <FileUp size={42} />
        <h3>رفع ملف تجريبي</h3>
        <p>في Phase 1-A لا تتم قراءة الملف فعليًا. هذه شاشة ثابتة لاختبار تجربة الرفع فقط، حتى لا نتظاهر بأننا اخترعنا OCR ونحن بعدنا في غرفة الانتظار.</p>
        <input type="file" accept=".pdf,.png,.jpg,.jpeg,.webp" onChange={handleFileChange} />
      </section>

      <section className="form-card">
        <div className="section-heading">
          <p className="eyebrow">فحص شكلي</p>
          <h3>حالة الملف</h3>
        </div>

        {uploadedFile ? (
          <div className="file-summary">
            <strong>{uploadedFile.name}</strong>
            <span>النوع: {uploadedFile.type}</span>
            <span>الحجم: {formatFileSize(uploadedFile.size)}</span>
            <button type="button" className="secondary-button compact" onClick={() => onFileSelected(null)}>
              إزالة الملف التجريبي
            </button>
          </div>
        ) : (
          <div className="empty-state">لم يتم اختيار ملف بعد.</div>
        )}

        <div className="notice-card">
          <ShieldCheck size={22} />
          <span>لا يتم رفع الملف إلى Backend في هذه المرحلة. الاختبار هنا للواجهة وحالة الجلسة فقط.</span>
        </div>
      </section>
    </div>
  );
}
