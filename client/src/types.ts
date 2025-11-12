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

export interface Workflow {
  id: string;
  name: string;
  createdAt: string;
  stage: Stage;
  fileTitle?: string;
  chunker?: string;
  chunkingConfig?: Record<string, number>;
  stats?: ChunkStatistics;
  visualizationHtml?: string;
}
