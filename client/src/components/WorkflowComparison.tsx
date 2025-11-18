import type {
  Chunker,
  Workflow,
  ChunkStatistics,
  EvaluationMetrics,
} from "../types";

const CHUNK_METRIC_KEYS: Record<
  keyof Omit<ChunkStatistics, "largest_text" | "smallest_text">,
  string
> = {
  total_chunks: "Total chunks",
  avg_chars: "Average characters",
  smallest_chunk_chars: "Smallest chunk characters",
  largest_chunk_chars: "Largest chunk characters",
};

const EVALUATION_METRIC_KEYS: Record<keyof EvaluationMetrics, string> = {
  precision_mean: "Precision mean",
  recall_mean: "Recall mean",
  iou_mean: "IoU mean",
  precision_omega_mean: "Precision omega mean",
};

type Props = {
  chunkers: Chunker[];
  workflows: Workflow[];
};

const WorkflowComparison = ({ workflows, chunkers }: Props) => {
  const findChunkerConfig = (
    strategy: Workflow["chunking_strategy"]
  ): Chunker | undefined => {
    if (!strategy) return undefined;

    const fullName =
      `${strategy.provider} ${strategy.chunker_type}`.toLowerCase();
    return chunkers.find((chunker) => chunker.name.toLowerCase() === fullName);
  };

  const getChunkerName = (
    strategy: Workflow["chunking_strategy"]
  ): string | undefined => {
    if (!strategy) return undefined;
    return findChunkerConfig(strategy)!.name;
  };

  const getConfigSummary = (workflow: Workflow): string => {
    const strategy = workflow.chunking_strategy;
    if (!strategy) return "";

    const chunkerConfig = findChunkerConfig(strategy)!;

    const configPairs = Object.entries(chunkerConfig)
      .filter(([, value]) => typeof value !== "string")
      .map(([key]) => {
        const configValue = (strategy as Record<string, unknown>)[key];
        if (configValue === undefined || configValue === null) return null;
        return `${key}: ${configValue}`;
      })
      .filter((value): value is string => Boolean(value));

    return configPairs.join(", ");
  };

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
      </div>

      {workflows.length < 2 ? (
        <div className="comparison-placeholder">
          Select at least 2 workflows to compare
        </div>
      ) : (
        <div className="comparison-grid">
          {workflows.map((workflow) => {
            const configSummary = workflow.chunking_strategy
              ? getConfigSummary(workflow)
              : "";

            return (
              <div key={workflow.id} className="comparison-card">
                <div className="comparison-card-header">
                  <div>
                    <h3 className="comparison-card-title">{workflow.title}</h3>
                    <div className="comparison-card-meta">
                      <span className="comparison-badge">
                        {getChunkerName(workflow.chunking_strategy)}
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
                        <pre className="comparison-config-code">
                          <code>{configSummary}</code>
                        </pre>
                      </div>
                    ) : (
                      <p className="comparison-empty">Not configured</p>
                    )}
                  </div>

                  <div className="comparison-section">
                    <h4 className="comparison-section-title">
                      Chunking Metrics
                    </h4>
                    {workflow.chunks_stats ? (
                      (() => {
                        const stats = workflow.chunks_stats as ChunkStatistics;
                        return (
                          <div className="comparison-metrics">
                            {(
                              Object.keys(CHUNK_METRIC_KEYS) as Array<
                                keyof typeof CHUNK_METRIC_KEYS
                              >
                            ).map((key) => {
                              const statsTyped = stats as unknown as Record<
                                keyof typeof CHUNK_METRIC_KEYS,
                                number
                              >;
                              return (
                                <div
                                  key={String(key)}
                                  className="comparison-metric-row"
                                >
                                  <span className="comparison-metric-label">
                                    {CHUNK_METRIC_KEYS[key]}
                                  </span>
                                  <span className="comparison-metric-value">
                                    {Number(statsTyped[key]).toFixed(0)}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        );
                      })()
                    ) : (
                      <p className="comparison-empty">No stats available</p>
                    )}
                  </div>

                  <div className="comparison-section">
                    <h4 className="comparison-section-title">
                      Evaluation Results
                    </h4>
                    {workflow.evaluation_metrics ? (
                      (() => {
                        const metrics =
                          workflow.evaluation_metrics as EvaluationMetrics;
                        return (
                          <div className="comparison-evaluation">
                            {(
                              Object.keys(EVALUATION_METRIC_KEYS) as Array<
                                keyof EvaluationMetrics
                              >
                            ).map((key) => {
                              const value = metrics[key];
                              const width = Math.max(
                                0,
                                Math.min(100, value * 100)
                              );

                              return (
                                <div key={key} className="comparison-eval-item">
                                  <div className="comparison-eval-header">
                                    <span className="comparison-eval-label">
                                      {EVALUATION_METRIC_KEYS[key]}
                                    </span>
                                    <span className="comparison-eval-value">
                                      {Number(value).toFixed(3)}
                                    </span>
                                  </div>
                                  <div className="comparison-progress-bar">
                                    <div
                                      className="comparison-progress-fill"
                                      style={{
                                        width: `${width}%`,
                                        backgroundColor: getRatingColor(value),
                                      }}
                                    />
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        );
                      })()
                    ) : (
                      <p className="comparison-empty">Not evaluated</p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default WorkflowComparison;
