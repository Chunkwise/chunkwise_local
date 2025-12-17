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
    key: "precision_omega_mean",
    name: "Precision Omega",
    description: "Weighted precision metric",
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

      <div className="evaluation-header">
        <div>
          <h3 className="evaluation-title">Evaluation Results</h3>
          <p className="evaluation-subtitle">
            Performance metrics for your chunking strategy
          </p>
        </div>
      </div>

      <div className="metrics-list">
        {METRIC_CONFIG.map(({ key, name, description }) => (
          <div key={key} className="metric-item">
            <div className="metric-header">
              <span className="metric-name">{name}</span>
              <span className="metric-value">{metrics[key].toFixed(3)}</span>
            </div>
            <p className="metric-desc">{description}</p>
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
  );
};

export default Evaluation;
