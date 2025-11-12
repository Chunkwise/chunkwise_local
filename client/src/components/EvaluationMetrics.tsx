import type { EvaluationMetrics as Metrics } from "../types";

interface EvaluationMetricsProps {
  metrics: Metrics;
}

type Rating = "Bad" | "Good" | "Excellent";

const getRating = (value: number): Rating => {
  const percentage = value * 100;
  if (percentage >= 80) return "Excellent";
  if (percentage >= 60) return "Good";
  return "Bad";
};

const getRatingColor = (rating: Rating): string => {
  switch (rating) {
    case "Excellent":
      return "#48bb78"; // green
    case "Good":
      return "#f6ad55"; // orange
    case "Bad":
      return "#fc8181"; // red
  }
};

const EvaluationMetrics = ({ metrics }: EvaluationMetricsProps) => {
  const precisionPercent = (metrics.precision_mean * 100).toFixed(1);
  const recallPercent = (metrics.recall_mean * 100).toFixed(1);
  const iouPercent = (metrics.iou_mean * 100).toFixed(1);

  const overallRating = getRating(
    (metrics.precision_mean + metrics.recall_mean + metrics.iou_mean) / 3
  );

  return (
    <div className="evaluation-container">
      <div className="evaluation-header">
        <div>
          <h3 className="evaluation-title">Evaluation Results</h3>
          <p className="evaluation-subtitle">
            Performance metrics for your chunking strategy
          </p>
        </div>
        <span className={`rating-badge rating-${overallRating.toLowerCase()}`}>
          {overallRating}
        </span>
      </div>

      <div className="metrics-list">
        <div className="metric-item">
          <div className="metric-header">
            <span className="metric-name">Precision</span>
            <span className="metric-value">{precisionPercent}%</span>
          </div>
          <p className="metric-description">Accuracy of retrieved chunks</p>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{
                width: `${precisionPercent}%`,
                backgroundColor: getRatingColor(
                  getRating(metrics.precision_mean)
                ),
              }}
            />
          </div>
        </div>

        <div className="metric-item">
          <div className="metric-header">
            <span className="metric-name">Recall</span>
            <span className="metric-value">{recallPercent}%</span>
          </div>
          <p className="metric-description">Coverage of relevant information</p>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{
                width: `${recallPercent}%`,
                backgroundColor: getRatingColor(getRating(metrics.recall_mean)),
              }}
            />
          </div>
        </div>

        <div className="metric-item">
          <div className="metric-header">
            <span className="metric-name">IoU</span>
            <span className="metric-value">{iouPercent}%</span>
          </div>
          <p className="metric-description">Intersection over Union score</p>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{
                width: `${iouPercent}%`,
                backgroundColor: getRatingColor(getRating(metrics.iou_mean)),
              }}
            />
          </div>
        </div>
      </div>

      <div className="evaluation-note">
        <strong>Note:</strong> These metrics are calculated based on a test
        query set to evaluate how well your chunking strategy performs for
        retrieval tasks.
      </div>
    </div>
  );
};

export default EvaluationMetrics;
