import { useState, useEffect } from "react";
import type { Workflow, Chunker, EvaluationMetrics as Metrics } from "../types";
import ChooseFile from "./ChooseFile";
import ChunkerForm from "./ChunkerForm";
import TabView from "./TabView";
import EvaluationMetrics from "./EvaluationMetrics";
import ChunkStats from "./ChunkStats";
import VisualizationDisplay from "./VisualizationDisplay";
import { getVisualization } from "../services/visualization";

type Props = {
  chunkers: Chunker[];
  availableFiles: string[];
  workflow?: Workflow;
  onUpdateWorkflow: (patch: Partial<Workflow>) => Promise<void>;
};

const WorkflowDetails = ({
  chunkers,
  availableFiles,
  workflow,
  onUpdateWorkflow,
}: Props) => {
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [evaluationEnabled, setEvaluationEnabled] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingViz, setIsLoadingViz] = useState(false);

  // Enable evaluation button when chunker is selected
  useEffect(() => {
    if (workflow?.chunking_strategy) {
      setEvaluationEnabled(true);
    } else {
      setEvaluationEnabled(false);
    }
  }, [workflow?.chunking_strategy]);

  if (!workflow) {
    return (
      <div className="placeholder">
        Select or create a workflow to upload/choose a file and configure
        chunkers.
      </div>
    );
  }

  async function handleFileChange(fileTitle: string | undefined) {
    setError(null);
    try {
      if (!fileTitle) {
        const update: Record<string, string> = {
          document_title: "",
          chunking_strategy: "",
          chunks_stats: "",
          visualization_html: "",
        };
        await onUpdateWorkflow(update as Partial<Workflow>);
      } else {
        await onUpdateWorkflow({ document_title: fileTitle });
      }
    } catch (error) {
      console.error("Failed to update file:", error);
      setError("Failed to update document selection");
    }
  }

  // Helper function to split chunker name
  const splitChunkerName = (
    name: string
  ): { provider: string; type: string } => {
    const parts = name.split(" ");
    return {
      provider: parts[0].toLowerCase(), // Lowercase for server
      type: parts[1].toLowerCase(), // Lowercase for server
    };
  };

  // Helper to capitalize first letter
  const capitalize = (str: string): string => {
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  };

  const reconstructChunkerName = (provider: string, type: string): string => {
    return `${capitalize(provider)} ${capitalize(type)}`;
  };

  const selectedChunkerConfig = chunkers.find((chunker) => {
    if (!workflow.chunking_strategy) return false;
    const fullName = reconstructChunkerName(
      workflow.chunking_strategy.provider,
      workflow.chunking_strategy.chunker_type
    );
    return chunker.name === fullName;
  });

  async function handleChunkerChange(name: string) {
    setError(null);
    try {
      const config = chunkers.find((chunker) => chunker.name === name);
      const { provider, type } = splitChunkerName(name);

      const initial: Record<string, number> = {};
      for (const [key, value] of Object.entries(config!)) {
        if (typeof value !== "string") {
          initial[key] = value.default;
        }
      }

      const update: Record<string, unknown> = {
        chunking_strategy: {
          chunker_type: type,
          provider: provider,
          ...initial,
        },
      };
      await onUpdateWorkflow(update as Partial<Workflow>);
    } catch (error) {
      console.error("Failed to update chunker:", error);
      setError("Failed to update chunker");
    }
  }

  async function handleConfigChange(key: string, value: number) {
    setError(null);
    try {
      if (!workflow?.chunking_strategy) return;

      const updated = {
        ...workflow.chunking_strategy,
        [key]: value,
      };

      const update: Record<string, unknown> = {
        chunking_strategy: updated,
      };
      await onUpdateWorkflow(update as Partial<Workflow>);
    } catch (error) {
      console.error("Failed to update config:", error);
      setError("Failed to update configuration");
    }
  }

  async function handleLoadVisualization() {
    if (!workflow?.id) return;

    setIsLoadingViz(true);
    setError(null);

    try {
      const vizData = await getVisualization(workflow.id);

      // Update workflow with visualization data
      const update: Record<string, unknown> = {
        chunks_stats: vizData.stats,
        visualization_html: vizData.html,
      };
      await onUpdateWorkflow(update as Partial<Workflow>);
    } catch (error) {
      console.error("Failed to load visualization:", error);
      setError("Failed to load visualization");
    } finally {
      setIsLoadingViz(false);
    }
  }

  async function handleRunEvaluation() {
    if (!workflow?.chunking_strategy) return;

    setIsEvaluating(true);
    setEvaluationEnabled(false);
    setError(null);

    // Simulate API call with mock data
    setTimeout(async () => {
      try {
        const mockMetrics: Metrics = {
          precision_mean: 0.708,
          recall_mean: 0.715,
          iou_mean: 0.65,
          precision_omega_mean: 0.725,
        };

        await onUpdateWorkflow({
          evaluation_metrics: mockMetrics,
        });
      } catch (error) {
        console.error("Failed to save evaluation:", error);
        setError("Failed to save evaluation results");
      } finally {
        setIsEvaluating(false);
      }
    }, 1500);
  }

  return (
    <div className="details">
      {error && (
        <div
          style={{
            padding: "1rem",
            backgroundColor: "#fee",
            color: "#c00",
            borderRadius: "4px",
            marginBottom: "1rem",
          }}
        >
          {error}
          <button
            onClick={() => setError(null)}
            style={{
              marginLeft: "1rem",
              background: "transparent",
              border: "none",
              color: "#c00",
              cursor: "pointer",
              fontWeight: "bold",
            }}
          >
            x
          </button>
        </div>
      )}

      <ChooseFile
        workflow={workflow}
        availableFiles={availableFiles}
        onFileChange={handleFileChange}
      />

      {workflow.document_title && (
        <>
          <ChunkerForm
            workflow={workflow}
            chunkers={chunkers}
            selectedChunkerConfig={selectedChunkerConfig}
            onChunkerChange={handleChunkerChange}
            onConfigChange={handleConfigChange}
          />

          {workflow.chunking_strategy && (
            <div className="details-row">
              <div className="evaluation-actions">
                <button
                  className="btn btn-primary"
                  onClick={handleLoadVisualization}
                  disabled={isLoadingViz}
                  style={{ marginRight: "1rem" }}
                >
                  {isLoadingViz ? (
                    <>
                      <span className="spinner">⟳</span> Loading
                      Visualization...
                    </>
                  ) : (
                    <>📊 Load Visualization</>
                  )}
                </button>
                <button
                  className="btn btn-evaluate"
                  onClick={handleRunEvaluation}
                  disabled={!evaluationEnabled || isEvaluating}
                >
                  {isEvaluating ? (
                    <>
                      <span className="spinner">⟳</span> Running Evaluation...
                    </>
                  ) : (
                    <>⚡ Run Evaluation</>
                  )}
                </button>
              </div>

              <TabView hasEvaluation={!!workflow.evaluation_metrics}>
                {{
                  visualization: (
                    <div className="tab-panel">
                      {isLoadingViz && (
                        <div className="muted">Loading visualization...</div>
                      )}
                      {workflow.chunks_stats &&
                      workflow.visualization_html &&
                      !isLoadingViz ? (
                        <>
                          <ChunkStats stats={workflow.chunks_stats} />
                          <VisualizationDisplay
                            html={workflow.visualization_html}
                          />
                        </>
                      ) : !isLoadingViz ? (
                        <p className="muted">
                          Click "Load Visualization" to view chunk statistics
                          and visualization
                        </p>
                      ) : null}
                    </div>
                  ),
                  evaluation: workflow.evaluation_metrics ? (
                    <EvaluationMetrics metrics={workflow.evaluation_metrics} />
                  ) : (
                    <div className="tab-panel">
                      <p className="muted">
                        Run evaluation to see performance metrics
                      </p>
                    </div>
                  ),
                }}
              </TabView>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default WorkflowDetails;
