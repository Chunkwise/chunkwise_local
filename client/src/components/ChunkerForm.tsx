import type { Workflow, Config } from "../types";

interface ChunkerFormProps {
  workflow: Workflow;
  configs: Config[];
  selectedConfig?: Config;
  onChunkerChange: (chunker: string) => void;
  onConfigChange: (option: string, value: number) => void;
}

const ChunkerForm = ({
  workflow,
  configs,
  selectedConfig,
  onChunkerChange,
  onConfigChange,
}: ChunkerFormProps) => {
  return (
    <div className="details-row">
      <h2 className="section-title">Chunker & configuration</h2>
      <div className="box">
        <div className="field">
          <label className="label">Chunker</label>
          <select
            className="select"
            value={workflow.chunker ?? ""}
            onChange={(event) => onChunkerChange(event.target.value)}
          >
            <option value="">-- choose chunker --</option>
            {configs.map((config) => (
              <option key={config.name} value={config.name}>
                {config.name}
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
                  onConfigChange("chunk_size", Number(e.target.value))
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
                    onConfigChange("chunk_overlap", Number(e.target.value))
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
                    onConfigChange(
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
  );
};

export default ChunkerForm;
