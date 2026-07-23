import type {
  ScientificDiagramPreview,
} from "../../types/project";

interface Props {
  preview: ScientificDiagramPreview;
  onClose: () => void;
}

export function ScientificDiagramPreviewCard({
  preview,
  onClose,
}: Props) {
  return (
    <section
      className="scientific-diagram-preview"
      dir="rtl"
    >
      <header>
        <div>
          <span>معاينة SVG</span>
          <h2>{preview.title}</h2>
        </div>
        <button
          type="button"
          className="secondary-button compact"
          onClick={onClose}
        >
          إغلاق
        </button>
      </header>

      {preview.issues.length ? (
        <ul className="scientific-diagram-preview-issues">
          {preview.issues.map((issue) => (
            <li key={issue}>{issue}</li>
          ))}
        </ul>
      ) : null}

      <div className="scientific-diagram-svg-frame">
        <img
          src={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(
            preview.svg,
          )}`}
          alt={preview.title}
        />
      </div>
    </section>
  );
}
