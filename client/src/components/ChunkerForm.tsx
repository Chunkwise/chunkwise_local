import React, { useState, useEffect } from "react";
import type {
  Evals,
  ChunkStats,
  ChunkerSelection,
  Config,
} from "../types/types";
import { getEvals, getVisualization, getConfigs } from "../services/gateway";
import { ChunkStatistics } from "./ChunkStatistics";
import Evaluations from "./Evaluations";

export default function ChunkerForm() {
  const [configs, setConfigs] = useState<Config[]>([]);
  const [selectedConfig, setSelectedConfig] = useState<Config | undefined>(
    undefined
  );
  // const [chunker, setChunker] = useState<ChunkerSelection>("Chonkie Token");
  const [chunkMaxSize, setChunkMaxSize] = useState<number>(500);
  const [chunkOverlapOrMinChars, setChunkOverlapOrMinChars] =
    useState<number>(500);
  const [evals, setEvals] = useState<Evals>(() => ({
    precision: 0,
    omega_precision: 0,
    recall: 0,
    iou: 0,
  }));
  const [chunkStats, setChunkStats] = useState<ChunkStats>(() => ({
    total_chunks: 0,
    avg_chars: 0,
    largest_chunk_chars: 0,
    smallest_chunk_chars: 0,
    largest_text: "",
    smallest_text: "",
  }));

  useEffect(() => {
    const fetchConfigs = async () => {
      try {
        const configs = await getConfigs();
        console.log("Configs: ", configs);
        setConfigs(configs);
        if (configs.length > 0) {
          setSelectedConfig(configs[0]);
          setChunkMaxSize(configs[0].chunk_size.default);
          setChunkOverlapOrMinChars(
            configs[0].chunk_overlap
              ? configs[0].chunk_overlap.default
              : configs[0].min_characters_per_chunk
              ? configs[0].min_characters_per_chunk.default
              : 0
          );
        }
      } catch (error: unknown) {
        throw new Error("Unknown error: " + error);
      }
    };

    fetchConfigs();
  }, []);

  function onChangeChunker(event: React.ChangeEvent<HTMLSelectElement>) {
    // setChunker(event.target.value as ChunkerSelection);
    setSelectedConfig(
      configs.find((config) => config.name === event.target.value)
    );
  }

  function onChangeChunkSize(event: React.ChangeEvent<HTMLInputElement>) {
    setChunkMaxSize(Number(event.target.value));
  }

  function onChangeOverlap(event: React.ChangeEvent<HTMLInputElement>) {
    setChunkOverlapOrMinChars(Number(event.target.value));
  }

  async function onVisualize(event: React.SyntheticEvent<Element, Event>) {
    event.preventDefault();
    const result = await getVisualization({
      chunker: (selectedConfig?.name as ChunkerSelection) ?? "Chonkie Token",
      size: chunkMaxSize,
      overlap: chunkOverlapOrMinChars,
    });

    setChunkStats(result.stats);
  }

  async function onEvaluate(event: React.SyntheticEvent<Element, Event>) {
    event.preventDefault();
    const result = await getEvals({
      chunker: (selectedConfig?.name as ChunkerSelection) ?? "Chonkie Token",
      size: chunkMaxSize,
      overlap: chunkOverlapOrMinChars,
    });
    setEvals(result);
  }

  return (
    <div id="chunking-configuration">
      {selectedConfig ? (
        <form>
          <h1>Configure Chunking Strategy</h1>
          <label htmlFor="chunker">Chunker:</label>
          <select
            id="chunker"
            onChange={onChangeChunker}
            value={selectedConfig.name}
          >
            {configs.map((config) => (
              <option value={config.name} key={config.name}>
                {config.name}
              </option>
            ))}
          </select>
          <label htmlFor="chunk-max-size">Maximum Chunk Size:</label>
          <input
            id="chunk-max-size-range"
            type="range"
            step={1}
            min={selectedConfig.chunk_size.min}
            max={selectedConfig.chunk_size.max}
            value={chunkMaxSize}
            onChange={onChangeChunkSize}
          />
          <input
            id="chunk-max-size"
            type="number"
            value={chunkMaxSize}
            min={selectedConfig.chunk_size.min}
            max={selectedConfig.chunk_size.max}
            onChange={onChangeChunkSize}
          />
          {selectedConfig.chunk_overlap ? (
            <label htmlFor="chunk-overlap">Chunk Overlap:</label>
          ) : (
            <label htmlFor="chunk-overlap">Minimum Chunk Size :</label>
          )}
          <input
            id="chunk-overlap-range"
            type="range"
            step={1}
            min={
              selectedConfig.chunk_overlap
                ? selectedConfig.chunk_overlap.min
                : selectedConfig.min_characters_per_chunk
                ? selectedConfig.min_characters_per_chunk.min
                : 0
            }
            max={
              selectedConfig.chunk_overlap
                ? selectedConfig.chunk_overlap.max
                : selectedConfig.min_characters_per_chunk
                ? selectedConfig.min_characters_per_chunk.max
                : 1000
            }
            value={chunkOverlapOrMinChars}
            onChange={onChangeOverlap}
          />
          <input
            id="chunk-overlap"
            type="number"
            value={chunkOverlapOrMinChars}
            min={
              selectedConfig.chunk_overlap
                ? selectedConfig.chunk_overlap.min
                : selectedConfig.min_characters_per_chunk
                ? selectedConfig.min_characters_per_chunk.min
                : 0
            }
            max={
              selectedConfig.chunk_overlap
                ? selectedConfig.chunk_overlap.max
                : selectedConfig.min_characters_per_chunk
                ? selectedConfig.min_characters_per_chunk.max
                : 1000
            }
            onChange={onChangeOverlap}
          />
          <div id="buttons">
            <button onClick={onVisualize}>Visualize</button>
            <button onClick={onEvaluate}>Evaluate</button>
          </div>
        </form>
      ) : (
        <div>Loading configs...</div>
      )}
      <ChunkStatistics {...chunkStats}></ChunkStatistics>
      <Evaluations {...evals}></Evaluations>
    </div>
  );
}
