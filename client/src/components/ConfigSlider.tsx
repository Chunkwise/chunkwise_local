import type { ChangeEvent } from "react";
import type { Workflow, Chunker, ConfigOption } from "../types";

type ConfigSliderProps = {
  optionKey: string;
  configOption: ConfigOption;
  chunkerConfig: Chunker;
  workflow: Workflow;
  onConfigChange: (option: string, value: number) => void;
};

const ConfigSlider = ({
  optionKey,
  configOption,
  chunkerConfig,
  workflow,
  onConfigChange,
}: ConfigSliderProps) => {
  const chunkSizeOption =
    typeof chunkerConfig.chunk_size === "object"
      ? (chunkerConfig.chunk_size as ConfigOption)
      : undefined;
  const currentChunkSize =
    (workflow.chunking_strategy?.chunk_size as number | undefined) ??
    chunkSizeOption?.default;

  const needsChunkSizeBound =
    optionKey === "chunk_overlap" || optionKey === "min_characters_per_chunk";

  let effectiveMax = configOption.max;
  let effectiveMin = configOption.min;
  if (needsChunkSizeBound && typeof currentChunkSize === "number") {
    const limit = Math.max(0, currentChunkSize - 1);
    effectiveMax = Math.min(configOption.max, limit);
    effectiveMin = Math.min(configOption.min, effectiveMax);
  }

  const rawValue =
    (workflow.chunking_strategy?.[optionKey] as number | undefined) ??
    configOption.default;
  const clampedValue = Math.min(Math.max(rawValue, effectiveMin), effectiveMax);

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const raw = Number(event.target.value);
    let nextValue = raw;

    if (needsChunkSizeBound && typeof currentChunkSize === "number") {
      const limit = Math.max(0, currentChunkSize - 1);
      nextValue = Math.min(nextValue, limit);
    }

    nextValue = Math.max(nextValue, effectiveMin);

    onConfigChange(optionKey, nextValue);
  };

  const step = configOption.type === "int" ? 1 : 0.01;

  return (
    <div className="config-row">
      <label className="label">{optionKey}</label>
      <div className="slider-container">
        <input
          type="range"
          step={step}
          className="slider"
          value={clampedValue}
          min={effectiveMin}
          max={effectiveMax}
          onChange={handleChange}
        />
        <span className="slider-value">{clampedValue}</span>
      </div>
      <small className="hint">
        min {effectiveMin} - max {effectiveMax}
      </small>
    </div>
  );
};

export default ConfigSlider;
