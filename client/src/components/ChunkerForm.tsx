import type { Workflow, Chunker } from "../types";

interface ChunkerFormProps {
  workflow: Workflow;
  chunkers: Chunker[];
  selectedChunkerConfig?: Chunker;
  onChunkerChange: (chunker: string) => void;
  onConfigChange: (option: string, value: number) => void;
}

const ChunkerForm = ({
  workflow,
  chunkers,
  selectedChunkerConfig,
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
            value={selectedChunkerConfig ? selectedChunkerConfig.name : ""}
            onChange={(event) => onChunkerChange(event.target.value)}
          >
            <option value="" disabled={!!workflow.chunking_strategy}>
              -- choose chunker --
            </option>
            {chunkers.map((chunker) => (
              <option key={chunker.name} value={chunker.name}>
                {chunker.name}
              </option>
            ))}
          </select>
        </div>

        {workflow.chunking_strategy && selectedChunkerConfig ? (
          <div className="config-area">
            <div>
              {selectedConfig.description}
            </div>
            <div className="muted">
              Configure chunker options (defaults pre-selected)
            </div>
            {Object.keys(selectedChunkerConfig).map((key) =>
              typeof selectedChunkerConfig[key] === "string" ? (
                ""
              ) : (
                <div key={key} className="config-row">
                  <label className="label">{key}</label>
                  <div className="slider-container">
                    <input
                      type="range"
                      step={
                        selectedChunkerConfig[key]?.type === "int" ? 1 : 0.01
                      }
                      className="slider"
                      value={
                        (workflow.chunking_strategy?.[key] as number) ??
                        selectedChunkerConfig[key]?.default
                      }
                      min={selectedChunkerConfig[key]?.min}
                      max={selectedChunkerConfig[key]?.max}
                      onChange={(event) =>
                        onConfigChange(key, Number(event.target.value))
                      }
                    />
                    <span className="slider-value">
                      {(workflow.chunking_strategy?.[key] as number) ??
                        selectedChunkerConfig[key]?.default}
                    </span>
                  </div>
                  <small className="hint">
                    min {selectedChunkerConfig[key]?.min} - max{" "}
                    {selectedChunkerConfig[key]?.max}
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
