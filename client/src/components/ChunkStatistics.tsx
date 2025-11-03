import type { ChunkStats } from "../types/types";

export function ChunkStatistics({
  total,
  avgSize,
  largestSize,
  smallestSize,
  largestText,
  smallestText,
}: ChunkStats) {
  return (
    <div className="stats">
      <h2>Chunk Stats</h2>
      <ul>
        <li className={total > 0 ? "" : "unknown"}>Total Chunks: {total}</li>
        <li className={avgSize > 0 ? "" : "unknown"}>
          Average Size: {avgSize}
        </li>
        <li className={largestSize > 0 ? "" : "unknown"}>
          Largest Size: {largestSize}
        </li>
        <li className={largestText.length > 0 ? "" : "unknown"}>
          Largest Chunk: {largestText}
        </li>
        <li className={smallestSize > 0 ? "" : "unknown"}>
          Smallest Size: {smallestSize}
        </li>
        <li className={smallestText.length > 0 ? "" : "unknown"}>
          Smallest Chunk: {smallestText}
        </li>
      </ul>
    </div>
  );
}
