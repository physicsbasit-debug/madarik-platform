import type { ChangeEvent } from 'react';
import type { ExportFormat, OutputMode, ProjectMetadata, SchoolLogoInfo } from '../../types/project';

interface ProjectSetupStepProps {
  metadata: ProjectMetadata;
  schoolLogo: SchoolLogoInfo | null;
  onChange: (metadata: ProjectMetadata) => void;
  onLogoSelected: (file: File | null) => void;
  onLogoRemove: () => void;
}

const subjects = ['العلوم العامة', 'الفيزياء', 'الكيمياء', 'الأحياء'];
const grades = ['السابع', 'الثامن', 'التاسع', 'العاشر', 'الحادي عشر', 'الثاني عشر'];
const semesters = ['الفصل الدراسي الأول', 'الفصل الدراسي الثاني'];

function formatFileSize(size: number) {
  if (size < 1024) return `${size} بايت`;
  if (size < 1024 * 1024) return `${Math.round(size / 1024)} كيلوبايت`;
  return `${(size / (1024 * 1024)).toFixed(1)} ميجابايت`;
}

export function ProjectSetupStep({ metadata, schoolLogo, onChange, onLogoSelected, onLogoRemove }: ProjectSetupStepProps) {
  function updateField(field: keyof ProjectMetadata, value: string) {
    onChange({ ...metadata, [field]: value });
  }

  function setOutputMode(outputMode: OutputMode) {
    onChange({ ...metadata, outputMode });
  }

  function toggleFormat(format: ExportFormat) {
    const exists = metadata.exportFormats.includes(format);
    const exportFormats = exists
      ? metadata.exportFormats.filter((item) => item !== format)
      : [...metadata.exportFormats, format];

    onChange({ ...metadata, exportFormats });
  }

  function handleLogoInput(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    onLogoSelected(file);
    event.target.value = '';
  }

  const logoPreview = schoolLogo ? `data:${schoolLogo.type};base64,${schoolLogo.dataBase64}` : null;

  return (
    <div className="step-grid">
      <section className="form-card wide-card">
        <div className="section-heading">
          <p className="eyebrow">بيانات المشروع</p>
          <h3>رأس الورقة والإعدادات العامة</h3>
          <p>هذه البيانات محفوظة أثناء الجلسة فقط. أضف شعار المدرسة اختياريًا ليظهر في ملفات Word وPDF.</p>
        </div>

        <div className="form-grid">
          <label>
            اسم المدرسة
            <input value={metadata.schoolName} onChange={(event) => updateField('schoolName', event.target.value)} />
          </label>

          <label>
            المديرية / المحافظة
            <input value={metadata.directorate} onChange={(event) => updateField('directorate', event.target.value)} />
          </label>

          <label>
            المادة
            <select value={metadata.subject} onChange={(event) => updateField('subject', event.target.value)}>
              {subjects.map((subject) => (
                <option key={subject} value={subject}>
                  {subject}
                </option>
              ))}
            </select>
          </label>

          <label>
            الصف
            <select value={metadata.grade} onChange={(event) => updateField('grade', event.target.value)}>
              {grades.map((grade) => (
                <option key={grade} value={grade}>
                  {grade}
                </option>
              ))}
            </select>
          </label>

          <label>
            الفصل الدراسي
            <select value={metadata.semester} onChange={(event) => updateField('semester', event.target.value)}>
              {semesters.map((semester) => (
                <option key={semester} value={semester}>
                  {semester}
                </option>
              ))}
            </select>
          </label>

          <label>
            عنوان الورقة
            <input value={metadata.paperTitle} onChange={(event) => updateField('paperTitle', event.target.value)} />
          </label>

          <label>
            الزمن
            <input value={metadata.duration} onChange={(event) => updateField('duration', event.target.value)} />
          </label>

          <label>
            الدرجة الكلية
            <input value={metadata.totalMarks} onChange={(event) => updateField('totalMarks', event.target.value)} />
          </label>

          <label>
            اسم المعلم
            <input value={metadata.teacherName} onChange={(event) => updateField('teacherName', event.target.value)} />
          </label>

          <label>
            التاريخ
            <input type="date" value={metadata.date} onChange={(event) => updateField('date', event.target.value)} />
          </label>
        </div>
      </section>

      <section className="form-card wide-card">
        <div className="section-heading">
          <p className="eyebrow">هوية المدرسة</p>
          <h3>شعار اختياري للتصدير</h3>
          <p>يدعم Phase 1-F3 رفع شعار PNG أو JPG مؤقتًا داخل جلسة المشروع. لا يوجد حفظ دائم للشعار بعد.</p>
        </div>

        <div className="logo-manager">
          <div className="logo-preview-box">
            {logoPreview ? <img src={logoPreview} alt="شعار المدرسة" /> : <span>لا يوجد شعار</span>}
          </div>
          <div className="logo-actions">
            <label className="file-picker-button">
              رفع شعار المدرسة
              <input type="file" accept="image/png,image/jpeg" onChange={handleLogoInput} />
            </label>
            {schoolLogo ? (
              <button type="button" className="secondary-button" onClick={onLogoRemove}>
                حذف الشعار
              </button>
            ) : null}
            {schoolLogo ? (
              <p className="logo-meta">
                {schoolLogo.name} · {formatFileSize(schoolLogo.size)}
              </p>
            ) : (
              <p className="logo-meta">سيظهر الشعار في أعلى ملفات DOCX وPDF عند التصدير.</p>
            )}
          </div>
        </div>
      </section>

      <section className="form-card">
        <div className="section-heading">
          <p className="eyebrow">نوع النسخة</p>
          <h3>اختيار المخرج النهائي</h3>
        </div>

        <div className="choice-stack">
          <button
            type="button"
            className={`choice-button ${metadata.outputMode === 'arabic' ? 'selected' : ''}`}
            onClick={() => setOutputMode('arabic')}
          >
            <strong>نسخة عربية نظيفة</strong>
            <span>للطلاب عند الحاجة إلى ورقة عربية مباشرة.</span>
          </button>

          <button
            type="button"
            className={`choice-button ${metadata.outputMode === 'bilingual' ? 'selected' : ''}`}
            onClick={() => setOutputMode('bilingual')}
          >
            <strong>نسخة ثنائية اللغة</strong>
            <span>الإنجليزي ثم العربي تحت كل سؤال.</span>
          </button>
        </div>
      </section>

      <section className="form-card">
        <div className="section-heading">
          <p className="eyebrow">صيغ التصدير</p>
          <h3>اختيار الملفات المطلوبة</h3>
        </div>

        <label className="checkbox-row">
          <input type="checkbox" checked={metadata.exportFormats.includes('docx')} onChange={() => toggleFormat('docx')} />
          Word DOCX للتعديل
        </label>
        <label className="checkbox-row">
          <input type="checkbox" checked={metadata.exportFormats.includes('pdf')} onChange={() => toggleFormat('pdf')} />
          PDF للطباعة
        </label>
      </section>
    </div>
  );
}
