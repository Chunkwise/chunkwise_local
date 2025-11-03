import type { Evals } from "../types/types";

export default function Evaluations({
  recall,
  precision,
  iou,
  omegaPrecision,
}: Evals) {
  return (
    <div className="evals">
      <h2>Evaluations</h2>
      <ul>
        <li className={recall > 0 ? "" : "unknown"}>Recall: {recall}</li>
        <li className={precision > 0 ? "" : "unknown"}>
          Precision: {precision}
        </li>
        <li className={precision > 0 ? "" : "unknown"}>
          Ω Precision: {omegaPrecision}
        </li>
        <li className={iou > 0 ? "" : "unknown"}>IoU: {iou}</li>
      </ul>
    </div>
  );
}
