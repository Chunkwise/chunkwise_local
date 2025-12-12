import { z } from "zod";

export type Stage = "Draft" | "Configured" | "Evaluated";

export type Tab = "visualization" | "evaluation" | "deploy";

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

export const EvaluationResponseSchema = z.object({
  embedding_model: z.string(),
  corpus_id: z.string(),
  document_s3_key: z.string(),
  queries_s3_key: z.string(),
  queries_generated: z.boolean(),
  num_queries: z.number().nullable().optional(),
  chunkers_evaluated: z.array(z.string()),
  results: z.array(EvaluationMetricsSchema),
});

export type EvaluationResponse = z.infer<typeof EvaluationResponseSchema>;

export interface S3Credentials {
  access_key: string;
  secret_key: string;
  bucket_name: string;
}

export const JobsStatusSchema = z.object({
  succeeded: z.number(),
  failed: z.number(),
  total: z.number(),
});

export type JobsStatus = z.infer<typeof JobsStatusSchema>;

export const DeploySummarySchema = z.object({
  database: z.string(),
  table: z.string(),
  documents_processed: z.number(),
  message: z.string(),
});

export type DeploySummary = z.infer<typeof DeploySummarySchema>;

export const RDSReadyPayloadSchema = z.object({
  ok: z.literal(true),
  stage: z.literal("rds-ready"),
  endpoint: z.string(),
  port: z.number(),
  database: z.string(),
  table_name: z.string(),
  secret_arn: z.string(),
  db_instance_identifier: z.string(),
});

export type RDSReadyPayload = z.infer<typeof RDSReadyPayloadSchema>;

export const S3ConnectedPayloadSchema = z.object({
  ok: z.literal(true),
  stage: z.literal("s3-connected"),
  bucket: z.string(),
});

export type S3ConnectedPayload = z.infer<typeof S3ConnectedPayloadSchema>;

export const NoDocumentsPayloadSchema = z.object({
  ok: z.literal(true),
  stage: z.literal("no-documents"),
  message: z.string(),
});

export type NoDocumentsPayload = z.infer<typeof NoDocumentsPayloadSchema>;

export const JobsUpdatedPayloadSchema = z.object({
  ok: z.literal(true),
  stage: z.literal("jobs-updated"),
  statuses: JobsStatusSchema,
});

export type JobsUpdatedPayload = z.infer<typeof JobsUpdatedPayloadSchema>;

export const DeployDonePayloadSchema = z.object({
  ok: z.literal(true),
  stage: z.literal("done"),
  summary: DeploySummarySchema.optional(),
});

export type DeployDonePayload = z.infer<typeof DeployDonePayloadSchema>;

export const DeployErrorPayloadSchema = z.object({
  ok: z.literal(false),
  stage: z.string(),
  error: z.string(),
  trace: z.string().optional(),
});

export type DeployErrorPayload = z.infer<typeof DeployErrorPayloadSchema>;

export type DeployEventType =
  | "rds-ready"
  | "s3-connected"
  | "s3-error"
  | "no-documents"
  | "batch-error"
  | "jobs-updated"
  | "error"
  | "done"
  | "message";

export type DeployWorkflowEvent =
  | { type: "rds-ready"; data: RDSReadyPayload }
  | { type: "s3-connected"; data: S3ConnectedPayload }
  | { type: "no-documents"; data: NoDocumentsPayload }
  | { type: "jobs-updated"; data: JobsUpdatedPayload }
  | { type: "done"; data: DeployDonePayload }
  | { type: "s3-error"; data: DeployErrorPayload }
  | { type: "batch-error"; data: DeployErrorPayload }
  | { type: "error"; data: DeployErrorPayload }
  | { type: "message"; data: unknown };

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
  deploy_table_name: z.string().optional().nullable(),
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
  deploy_table_name?: string | null;
}
