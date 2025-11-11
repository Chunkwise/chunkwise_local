import type { Workflow, Config, ConfigOption } from "../types";

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
            {Object.keys(selectedConfig).map((key) =>
              typeof selectedConfig[key] === "string" ? (
                ""
              ) : (
                <div key={key} className="config-row">
                  <label className="label">{key}</label>
                  <input
                    type="number"
                    step={selectedConfig[key]?.type === "int" ? 1 : 0.01}
                    className="input"
                    value={
                      workflow.chunkingConfig?.[key] ??
                      selectedConfig[key]?.default
                    }
                    min={selectedConfig[key]?.min}
                    max={selectedConfig[key]?.max}
                    onChange={(e) =>
                      onConfigChange(key, Number(e.target.value))
                    }
                  />
                  <small className="hint">
                    min {selectedConfig[key]?.min} - max{" "}
                    {selectedConfig[key]?.max}
                  </small>
                </div>
              )
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
