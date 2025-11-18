import { useState, useEffect } from "react";
import { ZodError } from "zod";
import type { Workflow, Chunker } from "../types";
import ChooseFile from "./ChooseFile";
import ChunkerForm from "./ChunkerForm";
import TabView from "./TabView";
import EvaluationMetrics from "./EvaluationMetrics";
import ChunkStats from "./ChunkStats";
import VisualizationDisplay from "./VisualizationDisplay";
import { getVisualization } from "../services/visualization";
import { getEvaluationMetrics } from "../services/evaluation";

type Props = {
  chunkers: Chunker[];
  availableFiles: string[];
  workflow?: Workflow;
  onUpdateWorkflow: (patch: Partial<Workflow>) => Promise<void>;
  onPatchWorkflow: (patch: Partial<Workflow>) => Promise<void>;
};

const WorkflowDetails = ({
  chunkers,
  availableFiles,
  workflow,
  onUpdateWorkflow,
  onPatchWorkflow,
}: Props) => {
  const [evaluationEnabled, setEvaluationEnabled] = useState(false);
  const [localConfig, setLocalConfig] = useState(workflow?.chunking_strategy);
  const [configChangeTimer, setConfigChangeTimer] = useState<number | null>(
    null
  );
  const [isLoadingViz, setIsLoadingViz] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (configChangeTimer) {
        clearTimeout(configChangeTimer);
      }
    };
  }, [configChangeTimer]);

  // Sync local config with workflow changes
  useEffect(() => {
    setLocalConfig(workflow?.chunking_strategy);
  }, [workflow?.chunking_strategy]);

  // Enable evaluation button when chunker is selected
  useEffect(() => {
    if (workflow?.chunking_strategy) {
      setEvaluationEnabled(true);
    } else {
      setEvaluationEnabled(false);
    }
  }, [workflow?.chunking_strategy]);

  // Placeholder when no workflow is selected
  if (!workflow) {
    return (
      <div className="placeholder">
        Select or create a workflow to upload/choose a file and configure
        chunkers.
      </div>
    );
  }

  // Determine selected chunker config
  const selectedChunkerConfig = chunkers.find((chunker) => {
    if (!workflow.chunking_strategy) return false;
    const fullName = `${workflow.chunking_strategy.provider} ${workflow.chunking_strategy.chunker_type}`;
    return chunker.name.toLowerCase() === fullName;
  });

  // Helper function to split and format chunker name
  const splitAndFormatChunkerName = (
    name: string
  ): { provider: string; type: string } => {
    const parts = name.split(" ");
    return {
      provider: parts[0].toLowerCase(),
      type: parts[1].toLowerCase(),
    };
  };

  // Handler for file change
  async function handleFileChange(fileTitle: string | undefined) {
    setError(null);
    try {
      if (!fileTitle) {
        const update: Record<string, string> = {
          document_title: "",
        };
        await onUpdateWorkflow(update as Partial<Workflow>);
      } else {
        await onUpdateWorkflow({ document_title: fileTitle });
        if (workflow?.chunking_strategy) {
          await loadVisualization();
        }
      }
    } catch (error) {
      console.error("Failed to update file:", error);
      setError("Failed to update document selection");
    }
  }

  // Load visualization data
  async function loadVisualization() {
    if (!workflow?.id) return;

    setIsLoadingViz(true);
    setError(null);

    try {
      const vizData = await getVisualization(workflow.id);
      const update: Record<string, unknown> = {
        chunks_stats: vizData.stats,
        visualization_html: vizData.html,
      };
      await onPatchWorkflow(update as Partial<Workflow>);
    } catch (error: unknown) {
      console.error("Failed to load visualization:", error);
      if (error instanceof ZodError) {
        setError("The server returned visualization data in an unexpected format");
      } else {
        setError("Failed to load visualization");
      }
    } finally {
      setIsLoadingViz(false);
    }
  }

  // Handlers for chunker and config change
  async function handleChunkerChange(name: string) {
    setError(null);
    try {
      const config = chunkers.find((chunker) => chunker.name === name);
      const { provider, type } = splitAndFormatChunkerName(name);

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
      await loadVisualization();
    } catch (error) {
      console.error("Failed to update chunker:", error);
      setError("Failed to update chunker");
    }
  }

  async function handleConfigChange(key: string, value: number) {
    if (!workflow?.chunking_strategy) return;
    setError(null);

    const updated = {
      ...workflow.chunking_strategy,
      [key]: value,
    };
    setLocalConfig(updated);

    // Clear existing timer
    if (configChangeTimer) {
      clearTimeout(configChangeTimer);
    }

    try {
      const update: Record<string, unknown> = {
        chunking_strategy: updated,
      };

      // Debounce request for update and visualization
      const timer = setTimeout(async () => {
        await onUpdateWorkflow(update as Partial<Workflow>);
        await loadVisualization();
      }, 800) as unknown as number;
      setConfigChangeTimer(timer);
    } catch (error) {
      console.error("Failed to update config:", error);
      setError("Failed to update configuration");
    }
  }

  // Handler for running evaluation
  async function handleRunEvaluation() {
    if (!workflow?.chunking_strategy) return;
    setIsEvaluating(true);
    setEvaluationEnabled(false);
    setError(null);

    try {
      const metrics = await getEvaluationMetrics(workflow.id);
      await onPatchWorkflow({
        evaluation_metrics: metrics,
      });
    } catch (error: unknown) {
      console.error("Failed to run evaluation:", error);
      if (error instanceof ZodError) {
        setError("The server returned evaluation data in an unexpected format");
      } else {
        setError("Failed to run evaluation");
      }
    } finally {
      setIsEvaluating(false);
    }
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

      <ChunkerForm
        workflow={{ ...workflow, chunking_strategy: localConfig }}
        chunkers={chunkers}
        selectedChunkerConfig={selectedChunkerConfig}
        onChunkerChange={handleChunkerChange}
        onConfigChange={handleConfigChange}
      />

      {workflow.document_title && workflow.chunking_strategy && (
        <div className="details-row">
          <div className="evaluation-actions">
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
                    <div className="muted">
                      <span className="spinner">⟳</span> Loading
                      visualization...
                    </div>
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
                      Select a chunker to see visualization
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
    </div>
  );
};

export default WorkflowDetails;
