import { z } from "zod";

export const StageSchema = z.enum(["Draft", "Configured", "Evaluated"]);

export type Stage = z.infer<typeof StageSchema>;

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

export const ChunkingStrategySchema = z
  .object({
    chunker_type: z.string(),
    provider: z.string(),
    chunk_size: z.number().optional(),
    chunk_overlap: z.number().optional(),
  })
  .catchall(z.unknown());

export type ChunkingStrategy = z.infer<typeof ChunkingStrategySchema>;

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

export const EvaluationMetricsSchema = z.object({
  iou_mean: z.number(),
  recall_mean: z.number(),
  precision_mean: z.number(),
  precision_omega_mean: z.number(),
});

export type EvaluationMetrics = z.infer<typeof EvaluationMetricsSchema>;

export const WorkflowResponseSchema = z.object({
  id: z.union([z.string(), z.number()]).transform((value) => String(value)),
  title: z.string(),
  created_at: z.string(),
  stage: z.string().optional().nullable(),
  document_title: z.string().optional().nullable(),
  chunking_strategy: z
    .union([ChunkingStrategySchema, z.string(), z.null()])
    .optional(),
  chunks_stats: z
    .union([ChunkStatisticsSchema, z.string(), z.null()])
    .optional(),
  visualization_html: z.string().optional().nullable(),
  evaluation_metrics: z
    .union([EvaluationMetricsSchema, z.string(), z.null()])
    .optional(),
});

export interface Workflow {
  id: string;
  title: string;
  created_at: string;
  stage?: Stage;
  document_title?: string | null;
  chunking_strategy?: ChunkingStrategy;
  chunks_stats?: ChunkStatistics;
  visualization_html?: string | null;
  evaluation_metrics?: EvaluationMetrics;
}
