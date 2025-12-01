import type { EvaluationResponse } from "../types";

interface EvaluationMetricsProps {
  evaluationResponse: EvaluationResponse;
}

// Blue color palette for progress bars
const PROGRESS_BAR_COLOR = "#3b82f6"; // Primary blue

const Evaluation = ({ evaluationResponse }: EvaluationMetricsProps) => {
  const metrics = evaluationResponse.results[0];
  
  if (!metrics) {
    return (
      <div className="evaluation-container">
        <p className="muted">No evaluation results available</p>
      </div>
    );
  }

  const precisionValue = metrics.precision_mean.toFixed(3);
  const recallValue = metrics.recall_mean.toFixed(3);
  const iouValue = metrics.iou_mean.toFixed(3);
  const precisionOmegaValue = metrics.precision_omega_mean.toFixed(3);

  // For progress bar width, convert to percentage
  const precisionPercent = metrics.precision_mean * 100;
  const recallPercent = metrics.recall_mean * 100;
  const iouPercent = metrics.iou_mean * 100;
  const precisionOmegaPercent = metrics.precision_omega_mean * 100;

  return (
    <div className="evaluation-container">
      <div className="evaluation-header">
        <div>
          <h3 className="evaluation-title">Evaluation Results</h3>
          <p className="evaluation-subtitle">
            Performance metrics for your chunking strategy
          </p>
        </div>
      </div>

      <div className="queries-info">
        <p>
          <strong>Queries S3 Path:</strong>{" "}
          <code>{evaluationResponse.queries_s3_key}</code>
        </p>
        <p className="queries-status">
          {evaluationResponse.queries_generated
            ? `✓ New queries were generated${evaluationResponse.num_queries ? ` (${evaluationResponse.num_queries} queries)` : ""}`
            : "✓ Existing queries were used"}
        </p>
      </div>

      <div className="metrics-list">
        <div className="metric-item">
          <div className="metric-header">
            <span className="metric-name">Precision</span>
            <span className="metric-value">{precisionValue}</span>
          </div>
          <p className="metric-description">Accuracy of retrieved chunks</p>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{
                width: `${precisionPercent}%`,
                backgroundColor: PROGRESS_BAR_COLOR,
              }}
            />
          </div>
        </div>

        <div className="metric-item">
          <div className="metric-header">
            <span className="metric-name">Precision Omega</span>
            <span className="metric-value">{precisionOmegaValue}</span>
          </div>
          <p className="metric-description">Weighted precision metric</p>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{
                width: `${precisionOmegaPercent}%`,
                backgroundColor: PROGRESS_BAR_COLOR,
              }}
            />
          </div>
        </div>

        <div className="metric-item">
          <div className="metric-header">
            <span className="metric-name">Recall</span>
            <span className="metric-value">{recallValue}</span>
          </div>
          <p className="metric-description">Coverage of relevant information</p>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{
                width: `${recallPercent}%`,
                backgroundColor: PROGRESS_BAR_COLOR,
              }}
            />
          </div>
        </div>

        <div className="metric-item">
          <div className="metric-header">
            <span className="metric-name">IoU</span>
            <span className="metric-value">{iouValue}</span>
          </div>
          <p className="metric-description">Intersection over Union score</p>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{
                width: `${iouPercent}%`,
                backgroundColor: PROGRESS_BAR_COLOR,
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

export default Evaluation;
