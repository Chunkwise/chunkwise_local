import React, { useState } from "react";
import type { Evals, ChunkStats } from "../types/types";
import { getEvals, getVisualization } from "../services/gateway";
import { ChunkStatistics } from "./ChunkStatistics";
import Evaluations from "./Evaluations";

export default function ChunkerForm() {
  const [chunker, setChunker] = useState<string>("");
  const [chunkMaxSize, setChunkMaxSize] = useState<number>(500);
  const [chunkOverlap, setChunkOverlap] = useState<number>(500);
  const [evals, setEvals] = useState<Evals>(() => ({
    precision: 0,
    omegaPrecision: 0,
    recall: 0,
    iou: 0,
  }));
  const [chunkStats, setChunkStats] = useState<ChunkStats>(() => ({
    total: 0,
    avgSize: 0,
    largestSize: 0,
    smallestSize: 0,
    largestText: "",
    smallestText: "",
  }));

  function onChangeChunker(event: React.ChangeEvent<HTMLSelectElement>) {
    setChunker(event.target.value);
  }

  function onChangeChunkSize(event: React.ChangeEvent<HTMLInputElement>) {
    setChunkMaxSize(Number(event.target.value));
  }

  function onChangeOverlap(event: React.ChangeEvent<HTMLInputElement>) {
    setChunkOverlap(Number(event.target.value));
  }

  async function onVisualize(event: React.SyntheticEvent<Element, Event>) {
    event.preventDefault();
    const result = await getVisualization({
      chunker: chunker,
      size: chunkMaxSize,
      overlap: chunkOverlap,
    });

    setChunkStats(result.stats);
  }

  async function onEvaluate(event: React.SyntheticEvent<Element, Event>) {
    event.preventDefault();
    const result = await getEvals({
      chunker,
      size: chunkMaxSize,
      overlap: chunkOverlap,
    });
    setEvals(result);
  }

  return (
    <div id="chunking-configuration">
      <form>
        <h1>Configure Chunking Strategy</h1>
        <label htmlFor="chunker">Chunker:</label>
        <select id="chunker" onChange={onChangeChunker} value={chunker}>
          <option value="">--Choose a chunker!--</option>
          <option value="Chonkie Token">Chonkie Token</option>
          <option value="Chonkie Recursive">Chonkie Recursive</option>
          <option value="LangChain Token">LangChain Token</option>
          <option value="LangChain Recursive">LangChain Recursive</option>
        </select>
        <label htmlFor="chunk-max-size">Maximum chunk size:</label>
        <input
          id="chunk-max-size-range"
          type="range"
          step={1}
          min={0}
          max={1000}
          value={chunkMaxSize}
          onChange={onChangeChunkSize}
        />
        <input
          id="chunk-max-size"
          type="number"
          value={chunkMaxSize}
          min={0}
          max={1000}
          onChange={onChangeChunkSize}
        />
        <label htmlFor="chunk-overlap">Chunk overlap:</label>
        <input
          id="chunk-overlap-range"
          type="range"
          step={1}
          min={0}
          max={1000}
          value={chunkOverlap}
          onChange={onChangeOverlap}
        />
        <input
          id="chunk-overlap"
          type="number"
          value={chunkOverlap}
          min={0}
          max={1000}
          onChange={onChangeOverlap}
        />
        <div id="buttons">
          <button onClick={onVisualize}>Visualize</button>
          <button onClick={onEvaluate}>Evaluate</button>
        </div>
      </form>
      <ChunkStatistics {...chunkStats}></ChunkStatistics>
      <Evaluations {...evals}></Evaluations>
    </div>
  );
}
