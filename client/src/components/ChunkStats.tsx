import type { ChunkStatistics } from "../types";

interface ChunkStatsProps {
  stats: ChunkStatistics;
}

const ChunkStats = ({ stats }: ChunkStatsProps) => {
  return (
    <div className="details-row">
      <h2 className="section-title">Chunk Statistics</h2>
      <div className="box">
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-label">Total Chunks</div>
            <div className="stat-value">{stats.total_chunks}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Average Characters</div>
            <div className="stat-value">{Math.round(stats.avg_chars)}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Largest Chunk</div>
            <div className="stat-value">{stats.largest_chunk_chars} chars</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Smallest Chunk</div>
            <div className="stat-value">{stats.smallest_chunk_chars} chars</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChunkStats;
