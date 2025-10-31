import React, { useState } from "react";

export default function ChunkerForm() {
  const [chunker, setChunker] = useState("");
  const [chunkMaxSize, setChunkMaxSize] = useState(500);
  const [chunkOverlap, setChunkOverlap] = useState(500);

  function onChangeChunker(event: React.ChangeEvent<HTMLSelectElement>) {
    setChunker(event.target.value);
  }

  function onChangeChunkSize(event: React.ChangeEvent<HTMLInputElement>) {
    setChunkMaxSize(Number(event.target.value));
  }

  function onChangeOverlap(event: React.ChangeEvent<HTMLInputElement>) {
    setChunkOverlap(Number(event.target.value));
  }

  return (
    <div id="chunking-configuration">
      <form>
        <h1>Configure Chunking Strategy</h1>
        <label htmlFor="chunker">Chunker:</label>
        <select id="chunker" onChange={onChangeChunker} value={chunker}>
          <option value="">--Choose a chunker!--</option>
          <option value="example1">example1</option>
          <option value="example2">example2</option>
          <option value="example3">example3</option>
          <option value="example4">example4</option>
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
          <button>Visualize</button>
          <button>Evaluate</button>
        </div>
      </form>
    </div>
  );
}
