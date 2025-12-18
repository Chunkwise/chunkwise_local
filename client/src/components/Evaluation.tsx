import type { EvaluationMetrics } from "../types";

interface EvaluationProps {
  infoMessage?: string | null;
  onDismissInfo?: () => void;
  evaluationMetrics: EvaluationMetrics;
}

const PROGRESS_BAR_COLOR = "#2563eb";

const METRIC_CONFIG: {
  key: keyof EvaluationMetrics;
  name: string;
  description: string;
}[] = [
  {
    key: "precision_mean",
    name: "Precision",
    description: "Accuracy of retrieved chunks",
  },
  {
    key: "recall_mean",
    name: "Recall",
    description: "Coverage of relevant information",
  },
  {
    key: "iou_mean",
    name: "IoU",
    description: "Intersection over Union score",
  },
  {
    key: "precision_omega_mean",
    name: "Precision Omega",
    description: "Weighted precision metric",
  },
];

const Evaluation = ({
  infoMessage,
  onDismissInfo,
  evaluationMetrics,
}: EvaluationProps) => {
  const metrics = evaluationMetrics;

  return (
    <div className="evaluation">
      {infoMessage && (
        <div className="evaluation-info-banner">
          <div className="evaluation-info-content">
            <span className="icon">check_circle</span>
            <span>{infoMessage}</span>
          </div>
          {onDismissInfo && (
            <button
              className="btn btn-icon btn-sm"
              onClick={onDismissInfo}
              aria-label="Dismiss info"
            >
              <span className="icon">close</span>
            </button>
          )}
        </div>
      )}

      <div className="section">
        <h2 className="section-header">
          <span className="title-md">Results</span>
        </h2>

        <div className="metrics-list">
        {METRIC_CONFIG.map(({ key, name, description }) => (
          <div key={key} className="metric-item">
            <div className="metric-header">
              <span className="metric-name">
                {name}
                <span className="metric-info" title={description}>
                  <span className="icon icon-sm">info</span>
                </span>
              </span>
              <span className="metric-value">{metrics[key].toFixed(3)}</span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{
                  width: `${metrics[key] * 100}%`,
                  backgroundColor: PROGRESS_BAR_COLOR,
                }}
              />
            </div>
          </div>
        ))}
      </div>
      </div>
    </div>
  );
};

export default Evaluation;
