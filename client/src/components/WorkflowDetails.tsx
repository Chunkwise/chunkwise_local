import { useEffect, useState } from "react";
import type { Workflow, Config } from "../types";

type Props = {
  workflow?: Workflow;
  configs: Config[];
  configsError?: string | null;
  sampleDoc: { name: string; text: string };
  onUpdate: (patch: Partial<Workflow>) => void;
};

const MAX_BYTES = 50 * 1024; // 50kb

export default function WorkflowDetails({
  workflow,
  configs,
  configsError,
  sampleDoc,
  onUpdate,
}: Props) {
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

  const selectedConfig = configs.find((c) => c.name === workflow?.chunker);

  // When the user chooses a chunker, preselect defaults for configs
  function handleChunkerChange(name: string) {
    const cfg = configs.find((c) => c.name === name);
    if (!cfg) {
      onUpdate({ chunker: name, chunkingConfig: undefined });
      return;
    }
    const initial: Record<string, number> = {};
    initial["chunk_size"] = cfg.chunk_size.default;
    if (cfg.chunk_overlap) initial["chunk_overlap"] = cfg.chunk_overlap.default;
    if (cfg.min_characters_per_chunk)
      initial["min_characters_per_chunk"] =
        cfg.min_characters_per_chunk.default;
    onUpdate({ chunker: name, chunkingConfig: initial });
  }

  function handleConfigChange(key: string, value: number) {
    const updated = { ...(workflow?.chunkingConfig ?? {}) };
    updated[key] = value;
    onUpdate({ chunkingConfig: updated });
  }

  function handleFileUpload(file: File | null) {
    setError(null);
    if (!file) {
      onUpdate({ file: undefined });
      return;
    }
    if (!file.name.toLowerCase().endsWith(".txt")) {
      setError("Only .txt files are allowed.");
      return;
    }
    if (file.size > MAX_BYTES) {
      setError("File too large. Max 50KB allowed.");
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const text = String(reader.result ?? "");
      onUpdate({ file: { name: file.name, text } });
    };
    reader.readAsText(file);
  }

  function setSampleDocument() {
    onUpdate({ file: { name: sampleDoc.name, text: sampleDoc.text } });
  }

  function removeFile() {
    onUpdate({ file: undefined });
  }

  return (
    <div className="details">
      <div className="details-row">
        <h2 className="section-title">Document</h2>
        <div className="box">
          <div className="file-controls">
            <label className="file-label">
              Upload .txt (max 50KB)
              <input
                className="file-input"
                type="file"
                accept=".txt"
                onChange={(e) => {
                  const f = e.target.files?.[0] ?? null;
                  handleFileUpload(f);
                  // reset input value to allow re-upload of same file if removed
                  if (e.target) (e.target as HTMLInputElement).value = "";
                }}
              />
            </label>

            <button className="btn" onClick={setSampleDocument}>
              Use sample document
            </button>
          </div>

          {error && <div className="error">{error}</div>}
          {workflow.file ? (
            <div className="file-preview">
              <div className="file-name">{workflow.file.name}</div>
              <button
                className="btn btn-sm"
                onClick={() => {
                  removeFile();
                }}
                title="Remove file"
              >
                x
              </button>
            </div>
          ) : (
            <div className="muted">
              No document attached. Upload or accept the sample.
            </div>
          )}
        </div>
      </div>

      <div className="details-row">
        <h2 className="section-title">Chunker & Config</h2>
        <div className="box">
          {configsError && <div className="error">{configsError}</div>}
          <div className="field">
            <label className="label">Chunker</label>
            <select
              className="select"
              value={workflow.chunker ?? ""}
              onChange={(e) => handleChunkerChange(e.target.value)}
            >
              <option value="">-- choose chunker --</option>
              {configs.map((c) => (
                <option key={c.name} value={c.name}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          {workflow.chunker && selectedConfig ? (
            <div className="config-area">
              <div className="muted">
                Configure chunker options (defaults pre-selected)
              </div>

              <div className="config-row">
                <label className="label">Chunk size</label>
                <input
                  type="number"
                  className="input"
                  value={
                    workflow.chunkingConfig?.chunk_size ??
                    selectedConfig.chunk_size.default
                  }
                  min={selectedConfig.chunk_size.min}
                  max={selectedConfig.chunk_size.max}
                  onChange={(e) =>
                    handleConfigChange("chunk_size", Number(e.target.value))
                  }
                />
                <small className="hint">
                  min {selectedConfig.chunk_size.min} — max{" "}
                  {selectedConfig.chunk_size.max}
                </small>
              </div>

              {selectedConfig.chunk_overlap && (
                <div className="config-row">
                  <label className="label">Chunk overlap</label>
                  <input
                    type="number"
                    className="input"
                    value={
                      workflow.chunkingConfig?.chunk_overlap ??
                      selectedConfig.chunk_overlap.default
                    }
                    min={selectedConfig.chunk_overlap.min}
                    max={selectedConfig.chunk_overlap.max}
                    onChange={(e) =>
                      handleConfigChange(
                        "chunk_overlap",
                        Number(e.target.value)
                      )
                    }
                  />
                  <small className="hint">
                    min {selectedConfig.chunk_overlap.min} — max{" "}
                    {selectedConfig.chunk_overlap.max}
                  </small>
                </div>
              )}

              {selectedConfig.min_characters_per_chunk && (
                <div className="config-row">
                  <label className="label">Min chars per chunk</label>
                  <input
                    type="number"
                    className="input"
                    value={
                      workflow.chunkingConfig?.min_characters_per_chunk ??
                      selectedConfig.min_characters_per_chunk.default
                    }
                    min={selectedConfig.min_characters_per_chunk.min}
                    max={selectedConfig.min_characters_per_chunk.max}
                    onChange={(e) =>
                      handleConfigChange(
                        "min_characters_per_chunk",
                        Number(e.target.value)
                      )
                    }
                  />
                  <small className="hint">
                    min {selectedConfig.min_characters_per_chunk.min} — max{" "}
                    {selectedConfig.min_characters_per_chunk.max}
                  </small>
                </div>
              )}
            </div>
          ) : (
            <div className="muted">
              Choose a chunker to preview its config options.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
