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
    <div className="section">
      <h2 className="section-header">
        <span className="icon">tune</span>
        <span className="title-md">Chunker & configuration</span>
      </h2>
      <div className="card">
        <div className="field">
          <label className="label">Chunker</label>
          <select
            className="select"
            value={selectedChunkerConfig ? selectedChunkerConfig.name : ""}
            onChange={(event) => onChunkerChange(event.target.value)}
          >
            <option value="" disabled={!!workflow.chunking_strategy}>
              -- Choose chunker --
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
            <div className="chunker-description">
              {selectedChunkerConfig.description}
            </div>
            <label className="label">Configuration</label>
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
          <div className="text-muted mt-2">
            <span className="icon icon-sm">info</span>
            Choose a chunker to preview its config options.
          </div>
        )}
      </div>
    </div>
  );
};

export default ChunkerForm;
