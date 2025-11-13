export type Stage = "Draft" | "Configured" | "Evaluated";

export interface File {
  document_title: string;
  document_content: string;
}

export interface ConfigOption {
  type: string;
  min: number;
  max: number;
  default: number;
}

export interface Chunker {
  name: string;
  [key: string]: string | ConfigOption;
}

export interface ChunkingStrategy {
  chunker_type: string;
  provider: string;
  chunk_size?: number;
  chunk_overlap?: number;
  [key: string]: string | number | undefined;
}

export interface ChunkStatistics {
  total_chunks: number;
  largest_chunk_chars: number;
  largest_text: string;
  smallest_chunk_chars: number;
  smallest_text: string;
  avg_chars: number;
}

export interface VisualizationResponse {
  stats: ChunkStatistics;
  html: string;
}

export interface EvaluationMetrics {
  iou_mean: number;
  recall_mean: number;
  precision_mean: number;
  precision_omega_mean: number;
}

export interface Workflow {
  // Database schema fields
  id: string;
  title: string;
  created_at: string;

  // Client-side computed field
  stage?: Stage;

  // Optional workflow data
  document_title?: string;
  chunking_strategy?: ChunkingStrategy;
  chunks_stats?: ChunkStatistics;
  visualization_html?: string;
  evaluation_metrics?: EvaluationMetrics;
}
