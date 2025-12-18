import { useState, useEffect } from "react";
import { ZodError } from "zod";
import type { Workflow, Chunker, DeploymentState } from "../types";
import type { DeploymentAction } from "../reducers/deploymentReducer";
import ChooseFile from "./ChooseFile";
import ChunkerForm from "./ChunkerForm";
import TabView from "./TabView";
import ChunkStats from "./ChunkStats";
import VisualizationDisplay from "./VisualizationDisplay";
import Evaluation from "./Evaluation";
import DeployConnector from "./DeployConnector";
import ErrorMessage from "./ErrorMessage";
import { getVisualization } from "../services/visualization";
import { getEvaluation } from "../services/evaluation";

type Props = {
  chunkers: Chunker[];
  isLoadingFiles: boolean;
  availableFiles: string[];
  workflow?: Workflow;
  onUpdateWorkflow: (patch: Partial<Workflow>) => Promise<void>;
  onPatchWorkflow: (patch: Partial<Workflow>) => Promise<void>;
  deploymentState?: DeploymentState;
  deploymentDispatch: React.Dispatch<DeploymentAction>;
  isAnyDeploying: boolean;
};

const WorkflowDetails = ({
  chunkers,
  isLoadingFiles,
  availableFiles,
  workflow,
  onUpdateWorkflow,
  onPatchWorkflow,
  deploymentState,
  deploymentDispatch,
  isAnyDeploying,
}: Props) => {
  const LLM_CHUNKERS = ["chonkie slumber", "chonkie semantic"];
  const [evaluationEnabled, setEvaluationEnabled] = useState(false);
  const [localConfig, setLocalConfig] = useState(workflow?.chunking_strategy);
  const [configChangeTimer, setConfigChangeTimer] = useState<number | null>(
    null
  );
  const [isLoadingViz, setIsLoadingViz] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [switchToEvaluation, setSwitchToEvaluation] = useState(false);
  const [switchToVisualization, setSwitchToVisualization] = useState(false);
  const [evaluationInfoMessage, setEvaluationInfoMessage] = useState<
    string | null
  >(null);
  const isSlumberChunker =
    workflow?.chunking_strategy?.chunker_type === "slumber";
  const [error, setError] = useState<string | null>(null);

  // Helper to get current chunker name
  const getCurrentChunkerName = (): string | undefined => {
    if (!workflow?.chunking_strategy) return undefined;
    return `${workflow.chunking_strategy.provider} ${workflow.chunking_strategy.chunker_type}`;
  };

  // Helper to check if chunker is an LLM chunker
  const isLLMChunker = (chunkerName?: string): boolean => {
    if (!chunkerName) return false;
    return LLM_CHUNKERS.includes(chunkerName.toLowerCase());
  };

  // Helper to confirm LLM chunker usage
  const confirmLLMChunkerUsage = (chunkerName?: string): boolean => {
    if (!isLLMChunker(chunkerName)) return true;
    return window.confirm(
      "This chunker uses the OpenAI API to create chunks. Do you want to proceed?"
    );
  };

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
        <span className="icon icon-lg">touch_app</span>
        <span>Select or create a workflow to get started</span>
      </div>
    );
  }

  // Determine selected chunker config
  const selectedChunkerConfig = chunkers.find((chunker) => {
    const currentName = getCurrentChunkerName();
    if (!currentName) return false;
    return chunker.name.toLowerCase() === currentName;
  });

  // Handler for file change
  async function handleFileChange(fileTitle: string | undefined) {
    setError(null);
    if (fileTitle && workflow?.chunking_strategy) {
      if (!confirmLLMChunkerUsage(getCurrentChunkerName())) {
        return;
      }
    }

    if (fileTitle && workflow?.chunking_strategy) {
      setIsLoadingViz(true);
      setSwitchToVisualization(true);
    }
    const previousDocumentTitle = workflow?.document_title;
    await onPatchWorkflow({ document_title: fileTitle || null });

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
          setSwitchToVisualization(false);
        }
      }
    } catch (error) {
      setIsLoadingViz(false);
      setSwitchToVisualization(false);
      await onPatchWorkflow({ document_title: previousDocumentTitle });
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
        setError(
          "The server returned visualization data in an unexpected format"
        );
      } else {
        setError("Failed to load visualization");
      }
    } finally {
      setIsLoadingViz(false);
      setSwitchToVisualization(false);
    }
  }

  // Handler for chunker change
  async function handleChunkerChange(name: string) {
    if (!confirmLLMChunkerUsage(name)) {
      return;
    }

    setError(null);
    setSwitchToVisualization(true);
    setIsLoadingViz(true);

    const previousChunkingStrategy = workflow?.chunking_strategy;
    const config = chunkers.find((chunker) => chunker.name === name);
    const { provider, type } = splitAndFormatChunkerName(name);

    const initial: Record<string, number> = {};
    for (const [key, value] of Object.entries(config!)) {
      if (typeof value !== "string") {
        initial[key] = value.default;
      }
    }
    const newChunkingStrategy = {
      chunker_type: type,
      provider: provider,
      ...initial,
    };
    await onPatchWorkflow({ chunking_strategy: newChunkingStrategy });

    try {
      const update: Record<string, unknown> = {
        chunking_strategy: newChunkingStrategy,
      };

      await onUpdateWorkflow(update as Partial<Workflow>);
      await loadVisualization();
    } catch (error) {
      setIsLoadingViz(false);
      await onPatchWorkflow({ chunking_strategy: previousChunkingStrategy });
      console.error("Failed to update chunker:", error);
      setError("Failed to update chunker");
    }
  }

  // Handler for config change
  async function handleConfigChange(key: string, value: number) {
    if (!workflow?.chunking_strategy) return;
    if (!confirmLLMChunkerUsage(getCurrentChunkerName())) {
      return;
    }

    setError(null);
    setSwitchToVisualization(true);
    setIsLoadingViz(true);

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
      setIsLoadingViz(false);
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
    setEvaluationInfoMessage(null);

    try {
      const evaluationResponse = await getEvaluation(workflow.id);
      const evaluationMetrics = evaluationResponse.results[0];
      await onPatchWorkflow({
        evaluation_metrics: evaluationMetrics,
      });
      const queriesInfoMessage = evaluationResponse.queries_generated
        ? `Evaluation complete! New queries were generated (${
            evaluationResponse.num_queries ?? 0
          } queries.)`
        : "Evaluation complete! Existing queries were used.";
      setEvaluationInfoMessage(queriesInfoMessage);
      setSwitchToEvaluation(true);
    } catch (error: unknown) {
      console.error("Failed to run evaluation:", error);
      if (error instanceof ZodError) {
        setError("The server returned evaluation data in an unexpected format");
      } else {
        setError("Failed to run evaluation");
      }
    } finally {
      setIsEvaluating(false);
      setTimeout(() => setSwitchToEvaluation(false), 0);
    }
  }

  return (
    <div className="details">
      {error && (
        <ErrorMessage
          message={error}
          variant="banner"
          onDismiss={() => setError(null)}
        />
      )}

      <ChooseFile
        workflow={workflow}
        isLoadingFiles={isLoadingFiles}
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
        <div className="section">
          <div className="evaluation-actions">
            <button
              className="btn-evaluate"
              onClick={handleRunEvaluation}
              disabled={!evaluationEnabled || isEvaluating}
            >
              {isEvaluating ? (
                <>
                  <span className="icon spinner">sync</span>
                  Running evaluation...
                </>
              ) : (
                <>
                  <span className="icon">bolt</span>
                  Run evaluation
                </>
              )}
            </button>
          </div>

          <TabView
            workflowId={workflow.id}
            hasEvaluation={!!workflow.evaluation_metrics}
            switchToEvaluation={switchToEvaluation}
            switchToVisualization={switchToVisualization}
            isDeployDisabled={isSlumberChunker}
          >
            {{
              visualization: (
                <div className="tab-panel">
                  {isLoadingViz && (
                    <div className="text-muted flex items-center gap-2">
                      <span className="icon spinner">sync</span>
                      Loading visualization...
                    </div>
                  )}
                  {!isLoadingViz &&
                    workflow.chunks_stats &&
                    workflow.visualization_html && (
                      <>
                        <ChunkStats stats={workflow.chunks_stats} />
                        <VisualizationDisplay
                          html={workflow.visualization_html}
                        />
                      </>
                    )}
                </div>
              ),
              evaluation: (
                <>
                  {workflow.evaluation_metrics && (
                    <Evaluation
                      infoMessage={evaluationInfoMessage}
                      onDismissInfo={() => setEvaluationInfoMessage(null)}
                      evaluationMetrics={workflow.evaluation_metrics}
                    />
                  )}
                </>
              ),
              deploy: (
                <div className="tab-panel">
                  <DeployConnector
                    workflow={workflow}
                    onWorkflowUpdate={onPatchWorkflow}
                    deploymentState={deploymentState}
                    deploymentDispatch={deploymentDispatch}
                    isAnyDeploying={isAnyDeploying}
                  />
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
