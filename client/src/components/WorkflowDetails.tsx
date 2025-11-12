import { useState, useEffect } from "react";
import type { Workflow, Chunker, EvaluationMetrics as Metrics } from "../types";
import ChooseFile from "./ChooseFile";
import ChunkerForm from "./ChunkerForm";
import TabView from "./TabView";
import EvaluationMetrics from "./EvaluationMetrics";
// import ChunkStats from "./ChunkStats";
// import VisualizationDisplay from "./VisualizationDisplay";
// import { getVisualization } from "../services/visualization";
// import { useThrottle } from "../hooks/useThrottle";

type Props = {
  chunkers: Chunker[];
  availableFiles: string[];
  workflow?: Workflow;
  onUpdateWorkflow: (patch: Partial<Workflow>) => void;
};

const WorkflowDetails = ({
  chunkers,
  availableFiles,
  workflow,
  onUpdateWorkflow,
}: Props) => {
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [evaluationEnabled, setEvaluationEnabled] = useState(false);
  // const [visualization, setVisualization] = useState<VisualizationResponse | null>(null);
  // const [isLoadingViz, setIsLoadingViz] = useState(false);

  // Throttling to avoid excessive API calls
  // const throttledConfig = useThrottle(workflow?.chunkingConfig, 1000);

  // Enable evaluation button when chunker is selected
  useEffect(() => {
    if (workflow?.chunker && workflow?.chunkingConfig) {
      setEvaluationEnabled(true);
    } else {
      setEvaluationEnabled(false);
    }
  }, [workflow?.chunker, workflow?.chunkingConfig]);

  if (!workflow) {
    return (
      <div className="placeholder">
        Select or create a workflow to upload/choose a file and configure
        chunkers.
      </div>
    );
  }

  function handleFileChange(fileTitle: string | undefined) {
    if (!fileTitle) {
      onUpdateWorkflow({
        fileTitle: undefined,
        chunker: undefined,
        chunkingConfig: undefined,
        stats: undefined,
        visualizationHtml: undefined,
      });
    } else {
      onUpdateWorkflow({ fileTitle: fileTitle });
    }
  }

  const selectedChunkerConfig = chunkers.find(
    (chunker) => chunker.name === workflow.chunker
  );

  function handleChunkerChange(name: string) {
    const config = chunkers.find((chunker) => chunker.name === name);
    if (!config) {
      onUpdateWorkflow({ chunker: name, chunkingConfig: undefined });
      return;
    }

    const initial: Record<string, number> = {};
    for (const [key, value] of Object.entries(config)) {
      if (typeof value !== "string") {
        initial[key] = value.default;
      }
    }
    // Clear evaluation when chunker changes
    onUpdateWorkflow({
      chunker: name,
      chunkingConfig: initial,
      evaluationMetrics: undefined,
    });
  }

  function handleConfigChange(key: string, value: number) {
    const updated = { ...workflow!.chunkingConfig };
    updated[key] = value;
    // Clear evaluation when config changes
    onUpdateWorkflow({
      chunkingConfig: updated,
      evaluationMetrics: undefined,
    });
  }

  async function handleRunEvaluation() {
    if (!workflow?.chunker || !workflow?.chunkingConfig) return;

    setIsEvaluating(true);
    setEvaluationEnabled(false);

    // Simulate API call with mock data
    setTimeout(() => {
      const mockMetrics: Metrics = {
        precision_mean: 0.708,
        recall_mean: 0.715,
        iou_mean: 0.65,
        precision_omega_mean: 0.725,
      };

      onUpdateWorkflow({
        evaluationMetrics: mockMetrics,
        stage: "Evaluated",
      });
      setIsEvaluating(false);
    }, 1500);
  }

  return (
    <div className="details">
      <ChooseFile
        workflow={workflow}
        availableFiles={availableFiles}
        onFileChange={handleFileChange}
      />

      {workflow.fileTitle && (
        <>
          <ChunkerForm
            workflow={workflow}
            chunkers={chunkers}
            selectedChunkerConfig={selectedChunkerConfig}
            onChunkerChange={handleChunkerChange}
            onConfigChange={handleConfigChange}
          />

          {workflow.chunker && (
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

              <TabView hasEvaluation={!!workflow.evaluationMetrics}>
                {{
                  visualization: (
                    <div className="tab-panel">
                      <p className="muted">
                        Chunk visualization will be displayed here
                      </p>
                      {/* {isLoadingViz && (
                        <div className="muted">Loading visualization...</div>
                      )}
                      {visualization && !isLoadingViz && (
                        <>
                          <ChunkStats stats={visualization.stats} />
                          <VisualizationDisplay html={visualization.html} />
                        </>
                      )} */}
                    </div>
                  ),
                  evaluation: workflow.evaluationMetrics ? (
                    <EvaluationMetrics metrics={workflow.evaluationMetrics} />
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
