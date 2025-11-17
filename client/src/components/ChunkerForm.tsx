import type { Workflow, Chunker, ConfigOption } from "../types";
import ConfigSlider from "./ConfigSlider";

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
            <div>{selectedChunkerConfig.description}</div>
            <div className="muted">
              Configure chunker options (defaults pre-selected)
            </div>
            {Object.keys(selectedChunkerConfig).map((key) =>
              typeof selectedChunkerConfig[key] === "string" ? null : (
                <ConfigSlider
                  key={key}
                  optionKey={key}
                  configOption={selectedChunkerConfig[key] as ConfigOption}
                  chunkerConfig={selectedChunkerConfig}
                  workflow={workflow}
                  onConfigChange={onConfigChange}
                />
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
