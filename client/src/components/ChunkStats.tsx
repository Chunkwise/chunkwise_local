import type { ChunkStatistics } from "../types";

interface ChunkStatsProps {
  stats: ChunkStatistics;
}

const ChunkStats = ({ stats }: ChunkStatsProps) => {
  return (
    <div className="section mb-4">
      <h3 className="section-header">
        <span className="icon">insights</span>
        <span className="title-sm">Chunk Statistics</span>
      </h3>
      <div className="card">
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-label">
              <span className="icon icon-sm">tag</span>
              Total Chunks
            </div>
            <div className="stat-value">{stats.total_chunks}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">
              <span className="icon icon-sm">straighten</span>
              Average Characters
            </div>
            <div className="stat-value">{Math.round(stats.avg_chars)}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">
              <span className="icon icon-sm">expand</span>
              Largest Chunk
            </div>
            <div className="stat-value">{stats.largest_chunk_chars} chars</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">
              <span className="icon icon-sm">compress</span>
              Smallest Chunk
            </div>
            <div className="stat-value">{stats.smallest_chunk_chars} chars</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChunkStats;
