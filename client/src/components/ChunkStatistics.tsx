import type { ChunkStats } from "../types/types";

export function ChunkStatistics({
  total_chunks,
  avg_chars,
  largest_chunk_chars,
  smallest_chunk_chars,
  largest_text,
  smallest_text,
}: ChunkStats) {
  return (
    <div className="stats">
      <h2>Chunk Stats</h2>
      <ul>
        <li className={total_chunks > 0 ? "" : "unknown"}>
          Total Chunks: {total_chunks}
        </li>
        <li className={avg_chars > 0 ? "" : "unknown"}>
          Average Size: {avg_chars}
        </li>
        <li className={largest_chunk_chars > 0 ? "" : "unknown"}>
          Largest Size: {largest_chunk_chars}
        </li>
        <li className={largest_text.length > 0 ? "" : "unknown"}>
          Largest Chunk: {largest_text}
        </li>
        <li className={smallest_chunk_chars > 0 ? "" : "unknown"}>
          Smallest Size: {smallest_chunk_chars}
        </li>
        <li className={smallest_text.length > 0 ? "" : "unknown"}>
          Smallest Chunk: {smallest_text}
        </li>
      </ul>
    </div>
  );
}
