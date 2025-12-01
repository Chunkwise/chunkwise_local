import type { EvaluationResponse, EvaluationMetrics } from "../types";

interface EvaluationProps {
  evaluationResponse: EvaluationResponse;
}

const PROGRESS_BAR_COLOR = "#2563eb";

const METRIC_CONFIG: { key: keyof EvaluationMetrics; name: string; description: string; icon: string }[] = [
  { key: "precision_mean", name: "Precision", description: "Accuracy of retrieved chunks", icon: "target" },
  { key: "precision_omega_mean", name: "Precision Omega", description: "Weighted precision metric", icon: "speed" },
  { key: "recall_mean", name: "Recall", description: "Coverage of relevant information", icon: "search" },
  { key: "iou_mean", name: "IoU", description: "Intersection over Union score", icon: "join_inner" },
];

const Evaluation = ({ evaluationResponse }: EvaluationProps) => {
  const metrics = evaluationResponse.results[0];

  if (!metrics) {
    return (
      <div className="evaluation">
        <p className="text-muted">
          <span className="icon icon-sm">info</span>
          No evaluation results available
        </p>
      </div>
    );
  }

  return (
    <div className="evaluation">
      <div className="evaluation-header">
        <div>
          <h3 className="evaluation-title">
            <span className="icon">analytics</span>
            Evaluation Results
          </h3>
          <p className="evaluation-subtitle">
            Performance metrics for your chunking strategy
          </p>
        </div>
      </div>

      <div className="queries-info">
        <p className="queries-status">
          <span className="icon icon-sm">check_circle</span>
          {evaluationResponse.queries_generated
            ? `New queries were generated (${evaluationResponse.num_queries ?? 0} queries)`
            : "Existing queries were used"}
        </p>
        <p>
          <strong>Queries Path:</strong>{" "}
          <code>{evaluationResponse.queries_s3_key}</code>
        </p>
      </div>

      <div className="metrics-list">
        {METRIC_CONFIG.map(({ key, name, description, icon }) => (
          <div key={key} className="metric-item">
            <div className="metric-header">
              <span className="metric-name">
                <span className="icon icon-sm">{icon}</span>
                {name}
              </span>
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
