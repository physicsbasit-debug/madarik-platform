import type { ChangeEvent } from 'react';
import { ChevronDown, ImagePlus } from 'lucide-react';
import type {
  ExportFormat,
  OutputMode,
  ProjectMetadata,
  SchoolLogoInfo,
} from '../../types/project';

interface ProjectSetupStepProps {
  metadata: ProjectMetadata;
  schoolLogo: SchoolLogoInfo | null;
  onChange: (metadata: ProjectMetadata) => void;
  onLogoSelected: (file: File | null) => void;
  onLogoRemove: () => void;
}

const subjects = ['العلوم العامة', 'الفيزياء', 'الكيمياء', 'الأحياء'];
const grades = [
  'السابع',
  'الثامن',
  'التاسع',
  'العاشر',
  'الحادي عشر',
  'الثاني عشر',
];
const semesters = ['الفصل الدراسي الأول', 'الفصل الدراسي الثاني'];

function formatFileSize(size: number) {
  if (size < 1024) return `${size} بايت`;
  if (size < 1024 * 1024) return `${Math.round(size / 1024)} كيلوبايت`;
  return `${(size / (1024 * 1024)).toFixed(1)} ميجابايت`;
}

export function ProjectSetupStep({
  metadata,
  schoolLogo,
  onChange,
  onLogoSelected,
  onLogoRemove,
}: ProjectSetupStepProps) {
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

  const logoPreview = schoolLogo
    ? `data:${schoolLogo.type};base64,${schoolLogo.dataBase64}`
    : null;

  return (
    <section className="start-column-card project-details-card">
      <div className="section-heading">
        <p className="eyebrow">بيانات الورقة</p>
        <h3>البيانات الأساسية</h3>
        <p>أدخل المعلومات التي ستظهر في رأس الورقة وملفات التصدير.</p>
      </div>

      <div className="start-details-form">
        <label>
          اسم المدرسة
          <input
            value={metadata.schoolName}
            onChange={(event) =>
              updateField('schoolName', event.target.value)
            }
          />
        </label>

        <label>
          المادة
          <select
            value={metadata.subject}
            onChange={(event) => updateField('subject', event.target.value)}
          >
            {subjects.map((subject) => (
              <option key={subject} value={subject}>
                {subject}
              </option>
            ))}
          </select>
        </label>

        <label>
          الصف
          <select
            value={metadata.grade}
            onChange={(event) => updateField('grade', event.target.value)}
          >
            {grades.map((grade) => (
              <option key={grade} value={grade}>
                {grade}
              </option>
            ))}
          </select>
        </label>

        <label>
          الفصل الدراسي
          <select
            value={metadata.semester}
            onChange={(event) => updateField('semester', event.target.value)}
          >
            {semesters.map((semester) => (
              <option key={semester} value={semester}>
                {semester}
              </option>
            ))}
          </select>
        </label>

        <label className="start-field-wide">
          عنوان الورقة
          <input
            value={metadata.paperTitle}
            onChange={(event) =>
              updateField('paperTitle', event.target.value)
            }
          />
        </label>
      </div>

      <details className="start-advanced-details">
        <summary>
          <span>
            <ChevronDown size={18} />
            بيانات إضافية وهوية التصدير
          </span>
          <small>اختياري</small>
        </summary>

        <div className="start-details-form start-details-expanded">
          <label>
            المديرية / المحافظة
            <input
              value={metadata.directorate}
              onChange={(event) =>
                updateField('directorate', event.target.value)
              }
            />
          </label>

          <label>
            اسم المعلم
            <input
              value={metadata.teacherName}
              onChange={(event) =>
                updateField('teacherName', event.target.value)
              }
            />
          </label>

          <label>
            الزمن
            <input
              value={metadata.duration}
              onChange={(event) =>
                updateField('duration', event.target.value)
              }
            />
          </label>

          <label>
            الدرجة الكلية
            <input
              value={metadata.totalMarks}
              onChange={(event) =>
                updateField('totalMarks', event.target.value)
              }
            />
          </label>

          <label className="start-field-wide">
            التاريخ
            <input
              type="date"
              value={metadata.date}
              onChange={(event) => updateField('date', event.target.value)}
            />
          </label>
        </div>

        <div className="start-logo-row">
          <div className="start-logo-preview">
            {logoPreview ? (
              <img src={logoPreview} alt="شعار المدرسة" />
            ) : (
              <ImagePlus size={28} />
            )}
          </div>
          <div>
            <strong>شعار المدرسة</strong>
            <p>
              {schoolLogo
                ? `${schoolLogo.name} · ${formatFileSize(schoolLogo.size)}`
                : 'اختياري، ويظهر في ملفات DOCX وPDF.'}
            </p>
            <div className="inline-actions">
              <label className="file-picker-button compact">
                رفع شعار
                <input
                  type="file"
                  accept="image/png,image/jpeg"
                  onChange={handleLogoInput}
                />
              </label>
              {schoolLogo ? (
                <button
                  type="button"
                  className="secondary-button compact"
                  onClick={onLogoRemove}
                >
                  إزالة
                </button>
              ) : null}
            </div>
          </div>
        </div>

        <div className="start-export-preferences">
          <div>
            <strong>نوع النسخة</strong>
            <div className="choice-stack compact-choice-stack">
              <button
                type="button"
                className={`choice-button ${
                  metadata.outputMode === 'arabic' ? 'selected' : ''
                }`}
                onClick={() => setOutputMode('arabic')}
              >
                <strong>عربية</strong>
              </button>
              <button
                type="button"
                className={`choice-button ${
                  metadata.outputMode === 'bilingual' ? 'selected' : ''
                }`}
                onClick={() => setOutputMode('bilingual')}
              >
                <strong>ثنائية اللغة</strong>
              </button>
            </div>
          </div>

          <div>
            <strong>صيغ التصدير</strong>
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={metadata.exportFormats.includes('docx')}
                onChange={() => toggleFormat('docx')}
              />
              Word
            </label>
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={metadata.exportFormats.includes('pdf')}
                onChange={() => toggleFormat('pdf')}
              />
              PDF
            </label>
          </div>
        </div>
      </details>
    </section>
  );
}
