import { z } from "zod";

export type Stage = "Draft" | "Configured" | "Evaluated";

export interface File {
  document_title: string;
  document_content: string;
}

export const ConfigOptionSchema = z.object({
  type: z.string(),
  min: z.number(),
  max: z.number(),
  default: z.number(),
});

export type ConfigOption = z.infer<typeof ConfigOptionSchema>;

export const ChunkerSchema = z.object({
  name: z.string(),
  description: z.string(),
}).catchall(z.union([z.string(), ConfigOptionSchema]));

export type Chunker = z.infer<typeof ChunkerSchema>;

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
