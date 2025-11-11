import { useEffect, useState } from "react";
import type { Workflow, Config } from "../types";
import ChooseFile from "./ChooseFile";
import ChunkerForm from "./ChunkerForm";

type Props = {
  workflow?: Workflow;
  configs: Config[];
  sampleFile: { name: string; text: string };
  onUpdate: (patch: Partial<Workflow>) => void;
};

const MAX_BYTES = 50 * 1024; // 50kb

const WorkflowDetails = ({ workflow, configs, sampleFile, onUpdate }: Props) => {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
  }, [workflow?.id]);

  if (!workflow) {
    return (
      <div className="placeholder">
        Select or create a workflow to upload/choose a file and configure chunkers.
      </div>
    );
  }

  function handleFileUpload(file: File | null) {
    setError(null);
    if (!file) {
      onUpdate({ file: undefined });
      return;
    }
    if (!file.name.toLowerCase().endsWith(".txt")) {
      setError("Only .txt files are allowed!");
      return;
    }
    if (file.size > MAX_BYTES) {
      setError("File too large! Max 50KB allowed.");
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      const text = String(reader.result);
      onUpdate({ file: { name: file.name, text } });
    };
    reader.readAsText(file);
  }

  function setSampleFile() {
    onUpdate({ file: { name: sampleFile.name, text: sampleFile.text } });
  }

  function removeFile() {
    onUpdate({
      file: undefined,
      chunker: undefined,
      chunkingConfig: undefined,
    });
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
        onFileUpload={handleFileUpload}
        onSetSampleFile={setSampleFile}
        onRemoveFile={removeFile}
        error={error}
      />

      {workflow.file && (
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
