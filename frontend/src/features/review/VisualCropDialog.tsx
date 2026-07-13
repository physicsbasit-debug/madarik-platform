import { Crop, X } from "lucide-react";
import { useMemo, useState } from "react";
import type { PointerEvent as ReactPointerEvent } from "react";
import type {
  PdfLayoutAssetInfo,
  VisualCropRequest,
} from "../../types/project";

interface VisualCropDialogProps {
  asset: PdfLayoutAssetInfo;
  isSaving: boolean;
  onCancel: () => void;
  onSave: (crop: VisualCropRequest) => Promise<void>;
}

interface CropPoint {
  x: number;
  y: number;
}

interface CropSelection {
  x: number;
  y: number;
  width: number;
  height: number;
}

const MIN_SELECTION_RATIO = 0.005;

function clampRatio(value: number) {
  return Math.max(0, Math.min(1, value));
}

function buildSelection(
  start: CropPoint,
  end: CropPoint,
): CropSelection {
  return {
    x: Math.min(start.x, end.x),
    y: Math.min(start.y, end.y),
    width: Math.abs(end.x - start.x),
    height: Math.abs(end.y - start.y),
  };
}

export function VisualCropDialog({
  asset,
  isSaving,
  onCancel,
  onSave,
}: VisualCropDialogProps) {
  const [dragStart, setDragStart] = useState<CropPoint | null>(null);
  const [selection, setSelection] =
    useState<CropSelection | null>(null);
  const [assetName, setAssetName] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const selectionIsValid = Boolean(
    selection &&
      selection.width >= MIN_SELECTION_RATIO &&
      selection.height >= MIN_SELECTION_RATIO,
  );

  const selectionLabel = useMemo(() => {
    if (!selection || !selectionIsValid) {
      return "لم تُحدّد منطقة قص صالحة بعد.";
    }

    return `العرض ${Math.round(
      selection.width * 100,
    )}% × الارتفاع ${Math.round(
      selection.height * 100,
    )}%`;
  }, [selection, selectionIsValid]);

  function getPointerPoint(
    event: ReactPointerEvent<HTMLDivElement>,
  ): CropPoint {
    const bounds =
      event.currentTarget.getBoundingClientRect();

    return {
      x: clampRatio(
        (event.clientX - bounds.left) / bounds.width,
      ),
      y: clampRatio(
        (event.clientY - bounds.top) / bounds.height,
      ),
    };
  }

  function handlePointerDown(
    event: ReactPointerEvent<HTMLDivElement>,
  ) {
    if (isSaving) return;

    event.preventDefault();
    event.currentTarget.setPointerCapture(event.pointerId);

    const point = getPointerPoint(event);

    setErrorMessage("");
    setDragStart(point);
    setSelection({
      x: point.x,
      y: point.y,
      width: 0,
      height: 0,
    });
  }

  function handlePointerMove(
    event: ReactPointerEvent<HTMLDivElement>,
  ) {
    if (!dragStart || isSaving) return;

    event.preventDefault();

    setSelection(
      buildSelection(
        dragStart,
        getPointerPoint(event),
      ),
    );
  }

  function handlePointerUp(
    event: ReactPointerEvent<HTMLDivElement>,
  ) {
    if (!dragStart) return;

    event.preventDefault();

    const completedSelection = buildSelection(
      dragStart,
      getPointerPoint(event),
    );

    setSelection(completedSelection);
    setDragStart(null);

    if (
      event.currentTarget.hasPointerCapture(
        event.pointerId,
      )
    ) {
      event.currentTarget.releasePointerCapture(
        event.pointerId,
      );
    }

    if (
      completedSelection.width < MIN_SELECTION_RATIO ||
      completedSelection.height < MIN_SELECTION_RATIO
    ) {
      setErrorMessage(
        "منطقة القص صغيرة جدًا. اسحب مستطيلًا أوضح حول الرسم أو الجدول.",
      );
    }
  }

  async function handleSave() {
    if (!selection || !selectionIsValid) {
      setErrorMessage(
        "حدّد الرسم أو الجدول أولًا بالسحب فوق الصفحة.",
      );
      return;
    }

    setErrorMessage("");

    try {
      await onSave({
        ...selection,
        name: assetName.trim() || null,
      });
    } catch (error) {
      console.error(error);
      setErrorMessage(
        "تعذر حفظ الجزء المقصوص. بقيت الصفحة الأصلية دون تغيير.",
      );
    }
  }

  return (
    <div className="visual-crop-backdrop">
      <section
        className="visual-crop-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="visual-crop-title"
      >
        <header className="visual-crop-header">
          <div>
            <p className="eyebrow">قص عنصر بصري</p>
            <h3 id="visual-crop-title">
              حدّد الرسم أو الجدول من صفحة{" "}
              {asset.pageNumber}
            </h3>
            <p>
              اسحب مستطيلًا حول العنصر المطلوب فقط.
              نص السؤال وبقية الصفحة لن يدخلا في الصورة.
            </p>
          </div>

          <button
            type="button"
            className="secondary-button compact"
            onClick={onCancel}
            disabled={isSaving}
          >
            <X size={17} />
            إغلاق
          </button>
        </header>

        <div className="visual-crop-workspace">
          <div
            className="visual-crop-stage"
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerCancel={() => setDragStart(null)}
          >
            <img
              src={`data:${asset.type};base64,${asset.dataBase64}`}
              alt={`صفحة PDF رقم ${asset.pageNumber}`}
              draggable={false}
            />

            {selection ? (
              <span
                className="visual-crop-selection"
                style={{
                  left: `${selection.x * 100}%`,
                  top: `${selection.y * 100}%`,
                  width: `${selection.width * 100}%`,
                  height: `${selection.height * 100}%`,
                }}
              />
            ) : null}
          </div>
        </div>

        <div className="visual-crop-controls">
          <label>
            اسم الصورة المقصوصة
            <input
              type="text"
              value={assetName}
              onChange={(event) =>
                setAssetName(event.target.value)
              }
              placeholder="مثال: شكل الكرة ومضرب الجولف"
              maxLength={120}
              disabled={isSaving}
            />
          </label>

          <div className="visual-crop-selection-status">
            <strong>المنطقة المحددة</strong>
            <span>{selectionLabel}</span>
          </div>
        </div>

        {errorMessage ? (
          <div className="visual-crop-error">
            {errorMessage}
          </div>
        ) : null}

        <footer className="visual-crop-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={onCancel}
            disabled={isSaving}
          >
            إلغاء
          </button>

          <button
            type="button"
            className="primary-button"
            onClick={handleSave}
            disabled={!selectionIsValid || isSaving}
          >
            <Crop size={17} />
            {isSaving
              ? "جارٍ حفظ القص..."
              : "حفظ القص داخل السؤال"}
          </button>
        </footer>
      </section>
    </div>
  );
}
