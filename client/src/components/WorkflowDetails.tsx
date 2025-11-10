import { useEffect, useState } from "react";
import type { Workflow, Config } from "../types";
import ChooseDocument from "./ChooseDocument";
import ChunkerForm from "./ChunkerForm";

type Props = {
  workflow?: Workflow;
  configs: Config[];
  sampleDoc: { name: string; text: string };
  onUpdate: (patch: Partial<Workflow>) => void;
};

const MAX_BYTES = 50 * 1024; // 50kb

const WorkflowDetails = ({
  workflow,
  configs,
  sampleDoc,
  onUpdate,
}: Props) => {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
  }, [workflow?.id]);

  if (!workflow) {
    return (
      <div className="placeholder">
        Select or create a workflow to configure documents and chunkers.
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

  function setSampleDocument() {
    onUpdate({ file: { name: sampleDoc.name, text: sampleDoc.text } });
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
    initial["chunk_size"] = config.chunk_size.default;
    if (config.chunk_overlap)
      initial["chunk_overlap"] = config.chunk_overlap.default;
    if (config.min_characters_per_chunk)
      initial["min_characters_per_chunk"] =
        config.min_characters_per_chunk.default;
    onUpdate({ chunker: name, chunkingConfig: initial });
  }

  function handleConfigChange(key: string, value: number) {
    const updated = { ...workflow!.chunkingConfig };
    updated[key] = value;
    onUpdate({ chunkingConfig: updated });
  }

  return (
    <div className="details">
      <ChooseDocument
        workflow={workflow}
        onFileUpload={handleFileUpload}
        onSetSample={setSampleDocument}
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
