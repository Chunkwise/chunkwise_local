import { useState } from "react";
import type { Workflow, Chunker, VisualizationResponse } from "../types";
import ChooseFile from "./ChooseFile";
import ChunkerForm from "./ChunkerForm";
// import ChunkStats from "./ChunkStats";
// import VisualizationDisplay from "./VisualizationDisplay";
// import { getVisualization } from "../services/visualization";
// import { useThrottle } from "../hooks/useThrottle";

type Props = {
  chunkers: Chunker[];
  workflow?: Workflow;
  onUpdateWorkflow: (patch: Partial<Workflow>) => void;
};

const WorkflowDetails = ({ chunkers, workflow, onUpdateWorkflow }: Props) => {
  // const [error, setError] = useState<string | null>(null);
  // const [visualization, setVisualization] =
    useState<VisualizationResponse | null>(null);
  // const [isLoadingViz, setIsLoadingViz] = useState(false);

  // Throttling to avoid excessive API calls
  // const throttledConfig = useThrottle(workflow?.chunkingConfig, 1000);

  if (!workflow) {
    return (
      <div className="placeholder">
        Select or create a workflow to upload/choose a file and configure
        chunkers.
      </div>
    );
  }

  function handleFileChange(fileId: string | undefined) {
    if (!fileId) {
      onUpdateWorkflow({
        fileId: undefined,
        chunker: undefined,
        chunkingConfig: undefined,
        stats: undefined,
        visualizationHtml: undefined,
      });
    } else {
      onUpdateWorkflow({ fileId: fileId });
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
    onUpdateWorkflow({ chunker: name, chunkingConfig: initial });
  }

  function handleConfigChange(key: string, value: number) {
    const updated = { ...workflow!.chunkingConfig };
    updated[key] = value;
    onUpdateWorkflow({ chunkingConfig: updated });
  }

  return (
    <div className="details">
      <ChooseFile
        workflow={workflow}
        onFileChange={handleFileChange}
      />

      {workflow.fileId && (
        <ChunkerForm
          workflow={workflow}
          chunkers={chunkers}
          selectedChunkerConfig={selectedChunkerConfig}
          onChunkerChange={handleChunkerChange}
          onConfigChange={handleConfigChange}
        />
      )}

      {/* {isLoadingViz && (
        <div className="details-row">
          <div className="box">
            <div className="muted">Loading visualization...</div>
          </div>
        </div>
      )}

      {visualization && !isLoadingViz && (
        <>
          <ChunkStats stats={visualization.stats} />
          <VisualizationDisplay html={visualization.html} />
        </>
      )} */}
    </div>
  );
};

export default WorkflowDetails;
