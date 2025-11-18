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

export const ChunkerSchema = z
  .object({
    name: z.string(),
    description: z.string(),
  })
  .catchall(z.union([z.string(), ConfigOptionSchema]));

export type Chunker = z.infer<typeof ChunkerSchema>;

export interface ChunkingStrategy {
  chunker_type: string;
  provider: string;
  chunk_size?: number;
  chunk_overlap?: number;
  [key: string]: string | number | undefined;
}

export const ChunkStatisticsSchema = z.object({
  total_chunks: z.number(),
  largest_chunk_chars: z.number(),
  largest_text: z.string(),
  smallest_chunk_chars: z.number(),
  smallest_text: z.string(),
  avg_chars: z.number(),
});

export type ChunkStatistics = z.infer<typeof ChunkStatisticsSchema>;

export const VisualizationResponseSchema = z.object({
  stats: ChunkStatisticsSchema,
  html: z.string(),
});

export type VisualizationResponse = z.infer<typeof VisualizationResponseSchema>;

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
