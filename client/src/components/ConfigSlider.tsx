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
  const resolveNumericValue = (key: string): number | undefined => {
    const strategyValue = workflow.chunking_strategy?.[key];
    if (strategyValue !== undefined) {
      return strategyValue as number;
    }

    const optionFromConfig = chunkerConfig[key];
    if (optionFromConfig) {
      return (optionFromConfig as ConfigOption).default;
    }
  };
  const currentChunkSize = resolveNumericValue("chunk_size");
  const currentChunkOverlap = resolveNumericValue("chunk_overlap");
  const currentMinChars = resolveNumericValue("min_characters_per_chunk");

  const needsChunkSizeBound =
    optionKey === "chunk_overlap" || optionKey === "min_characters_per_chunk";
  const affectsChunkSize = optionKey === "chunk_size";

  const computeBounds = () => {
    let min = configOption.min;
    let max = configOption.max;

    if (needsChunkSizeBound && typeof currentChunkSize === "number") {
      const limit = Math.max(0, currentChunkSize - 1);
      max = Math.min(max, limit);
      min = Math.min(min, max);
    }

    if (affectsChunkSize) {
      const overlapRequirement =
        typeof currentChunkOverlap === "number" ? currentChunkOverlap + 1 : min;
      const minCharsRequirement =
        typeof currentMinChars === "number" ? currentMinChars + 1 : min;

      min = Math.max(min, overlapRequirement, minCharsRequirement);
    }

    if (min > max) {
      min = max;
    }

    return { min, max };
  };

  const clamp = (value: number, bounds: { min: number; max: number }) =>
    Math.min(Math.max(value, bounds.min), bounds.max);

  const bounds = computeBounds();

  const initialValue =
    resolveNumericValue(optionKey) ?? configOption.default ?? bounds.min;
  const clampedValue = clamp(initialValue, bounds);

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const raw = Number(event.target.value);
    const nextValue = clamp(raw, bounds);
    onConfigChange(optionKey, nextValue);
  };

  return (
    <div className="config-row">
      <label className="label">{optionKey}</label>
      <div className="slider-container">
        <input
          type="range"
          step={configOption.type === "int" ? 1 : 0.01}
          className="slider"
          value={clampedValue}
          min={bounds.min}
          max={bounds.max}
          onChange={handleChange}
        />
        <span className="slider-value">{clampedValue}</span>
      </div>
      <small className="hint">
        min {bounds.min} - max {bounds.max}
      </small>
    </div>
  );
};

export default ConfigSlider;
