import type { Workflow } from "../types";

type Props = {
  workflows: Workflow[];
  onExit: () => void;
};

const WorkflowComparison = ({ workflows, onExit }: Props) => {
  const getRatingColor = (value: number): string => {
    const percentage = value * 100;
    if (percentage >= 80) return "#48bb78"; // green
    if (percentage >= 60) return "#f6ad55"; // orange
    return "#fc8181"; // red
  };

  return (
    <div className="comparison-view">
      <div className="comparison-header">
        <div>
          <h2 className="comparison-title">Workflow Comparison</h2>
          <p className="comparison-subtitle">
            Compare chunking strategies side by side
          </p>
        </div>
        <button className="btn-exit" onClick={onExit}>
          ✕ Exit Comparison
        </button>
      </div>

      {workflows.length < 2 ? (
        <div className="comparison-placeholder">
          Select at least 2 workflows to compare
        </div>
      ) : (
        <div className="comparison-grid">
          {workflows.map((workflow) => (
            <div key={workflow.id} className="comparison-card">
              <div className="comparison-card-header">
                <div>
                  <h3 className="comparison-card-title">{workflow.title}</h3>
                  <div className="comparison-card-meta">
                    <span className="comparison-badge">
                      {workflow.chunking_strategy?.chunker_type || "N/A"}
                    </span>
                    <span className="comparison-stage-badge">
                      {workflow.stage}
                    </span>
                  </div>
                </div>
              </div>

              <div className="comparison-card-body">
                <div className="comparison-section">
                  <h4 className="comparison-section-title">Configuration</h4>
                  {workflow.chunking_strategy ? (
                    <div className="comparison-config">
                      <div className="comparison-config-row">
                        <span className="comparison-config-label">
                          Chunk Size
                        </span>
                        <span className="comparison-config-value">
                          {workflow.chunking_strategy.chunk_size || "N/A"}
                        </span>
                      </div>
                      <div className="comparison-config-row">
                        <span className="comparison-config-label">Overlap</span>
                        <span className="comparison-config-value">
                          {workflow.chunking_strategy.chunk_overlap || "N/A"}
                        </span>
                      </div>
                    </div>
                  ) : (
                    <p className="comparison-empty">Not configured</p>
                  )}
                </div>

                <div className="comparison-section">
                  <h4 className="comparison-section-title">Chunking Metrics</h4>
                  {workflow.chunks_stats ? (
                    <div className="comparison-metrics">
                      <div className="comparison-metric-row">
                        <span className="comparison-metric-label">Chunks</span>
                        <span className="comparison-metric-value">
                          {workflow.chunks_stats.total_chunks}
                        </span>
                      </div>
                      <div className="comparison-metric-row">
                        <span className="comparison-metric-label">
                          Avg Size
                        </span>
                        <span className="comparison-metric-value">
                          {Math.round(workflow.chunks_stats.avg_chars)}
                        </span>
                      </div>
                      <div className="comparison-metric-row">
                        <span className="comparison-metric-label">
                          Min Size
                        </span>
                        <span className="comparison-metric-value">
                          {workflow.chunks_stats.smallest_chunk_chars}
                        </span>
                      </div>
                      <div className="comparison-metric-row">
                        <span className="comparison-metric-label">
                          Max Size
                        </span>
                        <span className="comparison-metric-value">
                          {workflow.chunks_stats.largest_chunk_chars}
                        </span>
                      </div>
                    </div>
                  ) : (
                    <p className="comparison-empty">No stats available</p>
                  )}
                </div>

                <div className="comparison-section">
                  <h4 className="comparison-section-title">
                    Evaluation Results
                  </h4>
                  {workflow.evaluation_metrics ? (
                    <div className="comparison-evaluation">
                      <div className="comparison-eval-item">
                        <div className="comparison-eval-header">
                          <span className="comparison-eval-label">
                            Precision
                          </span>
                          <span className="comparison-eval-value">
                            {(workflow.evaluation_metrics.precision_mean * 100).toFixed(
                              1
                            )}
                            %
                          </span>
                        </div>
                        <div className="comparison-progress-bar">
                          <div
                            className="comparison-progress-fill"
                            style={{
                              width: `${workflow.evaluation_metrics.precision_mean * 100}%`,
                              backgroundColor: getRatingColor(
                                workflow.evaluation_metrics.precision_mean
                              ),
                            }}
                          />
                        </div>
                      </div>

                      <div className="comparison-eval-item">
                        <div className="comparison-eval-header">
                          <span className="comparison-eval-label">Recall</span>
                          <span className="comparison-eval-value">
                            {(workflow.evaluation_metrics.recall_mean * 100).toFixed(
                              1
                            )}
                            %
                          </span>
                        </div>
                        <div className="comparison-progress-bar">
                          <div
                            className="comparison-progress-fill"
                            style={{
                              width: `${workflow.evaluation_metrics.recall_mean * 100}%`,
                              backgroundColor: getRatingColor(
                                workflow.evaluation_metrics.recall_mean
                              ),
                            }}
                          />
                        </div>
                      </div>

                      <div className="comparison-eval-item">
                        <div className="comparison-eval-header">
                          <span className="comparison-eval-label">IoU</span>
                          <span className="comparison-eval-value">
                            {(workflow.evaluation_metrics.iou_mean * 100).toFixed(
                              1
                            )}
                            %
                          </span>
                        </div>
                        <div className="comparison-progress-bar">
                          <div
                            className="comparison-progress-fill"
                            style={{
                              width: `${workflow.evaluation_metrics.iou_mean * 100}%`,
                              backgroundColor: getRatingColor(
                                workflow.evaluation_metrics.iou_mean
                              ),
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="comparison-empty">Not evaluated</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default WorkflowComparison;
