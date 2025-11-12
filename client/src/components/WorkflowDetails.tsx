import { useEffect, useState } from "react";
import type { Workflow, Config, VisualizationResponse } from "../types";
import ChooseFile from "./ChooseFile";
import ChunkerForm from "./ChunkerForm";
import ChunkStats from "./ChunkStats";
import VisualizationDisplay from "./VisualizationDisplay";
import { getVisualization } from "../services/visualization";
import { useThrottle } from "../hooks/useThrottle";

type Props = {
  configs: Config[];
  workflow?: Workflow;
  onUpdateWorkflow: (patch: Partial<Workflow>) => void;
};

const WorkflowDetails = ({ configs, workflow, onUpdateWorkflow }: Props) => {
  // const [error, setError] = useState<string | null>(null);
  const [visualization, setVisualization] =
    useState<VisualizationResponse | null>(null);
  const [isLoadingViz, setIsLoadingViz] = useState(false);

  // Throttling to avoid excessive API calls
  const throttledConfig = useThrottle(workflow?.chunkingConfig, 1000);

  useEffect(() => {
    // setError(null);
    if (workflow?.stats && workflow?.visualizationHtml) {
      setVisualization({
        stats: workflow.stats,
        html: workflow.visualizationHtml,
      });
    } else {
      setVisualization(null);
    }
  }, [workflow?.id, workflow?.stats, workflow?.visualizationHtml]);

  useEffect(() => {
    const fetchVisualization = async () => {
      if (
        !workflow?.fileId ||
        !workflow?.chunker ||
        !workflow?.chunkingConfig
      ) {
        setVisualization(null);
        onUpdateWorkflow({ stats: undefined, visualizationHtml: undefined });
        return;
      }

      setIsLoadingViz(true);
      try {
        const chunkerConfig = {
          chunker_type: workflow.chunker.split(" ")[1].toLowerCase(),
          provider: workflow.chunker.split(" ")[0].toLowerCase(),
          ...workflow.chunkingConfig,
        };
        const result = await getVisualization(workflow.fileId, chunkerConfig);
        setVisualization(result);
        // Save to workflow state
        onUpdateWorkflow({
          stats: result.stats,
          visualizationHtml: result.html,
        });
      } catch (err) {
        console.error("Failed to fetch visualization:", err);
        // setError("Failed to load visualization");
        onUpdateWorkflow({ stats: undefined, visualizationHtml: undefined });
      } finally {
        setIsLoadingViz(false);
      }
    };

    fetchVisualization();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workflow?.fileId, workflow?.chunker, throttledConfig]);

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

  const selectedConfig = configs.find(
    (config) => config.name === workflow.chunker
  );

  function handleChunkerChange(name: string) {
    const config = configs.find((config) => config.name === name);
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
          configs={configs}
          selectedConfig={selectedConfig}
          onChunkerChange={handleChunkerChange}
          onConfigChange={handleConfigChange}
        />
      )}

      {isLoadingViz && (
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
      )}
    </div>
  );
};

export default WorkflowDetails;
