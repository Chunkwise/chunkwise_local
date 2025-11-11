import { useEffect, useState } from "react";
import type { Workflow, Config } from "../types";
import ChooseFile from "./ChooseFile";
import ChunkerForm from "./ChunkerForm";

type Props = {
  workflow?: Workflow;
  configs: Config[];
  onUpdate: (patch: Partial<Workflow>) => void;
};

const WorkflowDetails = ({ workflow, configs, onUpdate }: Props) => {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
  }, [workflow?.id]);

  if (!workflow) {
    return (
      <div className="placeholder">
        Select or create a workflow to upload/choose a file and configure
        chunkers.
      </div>
    );
  }

  function handleFileChange(fileId: string | undefined) {
    setError(null);
    if (!fileId) {
      onUpdate({
        fileId: undefined,
        chunker: undefined,
        chunkingConfig: undefined,
      });
    } else {
      onUpdate({ fileId: fileId });
    }
  }

  const selectedConfig = configs.find(
    (config) => config.name === workflow.chunker
  );

  function handleChunkerChange(name: string) {
    const config = configs.find((config) => config.name === name);
    if (!config) {
      onUpdate({ chunker: name, chunkingConfig: undefined });
      return;
    }

    const initial: Record<string, number> = {};
    for (const [key, value] of Object.entries(config)) {
      if (typeof value !== "string") {
        initial[key] = value.default;
      }
    }
    onUpdate({ chunker: name, chunkingConfig: initial });
  }

  function handleConfigChange(key: string, value: number) {
    const updated = { ...workflow!.chunkingConfig };
    updated[key] = value;
    onUpdate({ chunkingConfig: updated });
  }

  return (
    <div className="details">
      <ChooseFile
        workflow={workflow}
        onFileChange={handleFileChange}
        error={error}
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
    </div>
  );
};

export default WorkflowDetails;
