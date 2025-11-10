export type Stage = 'draft' | 'configured' | 'evaluated';

export interface ConfigOption {
  type: string;
  min: number;
  max: number;
  default: number;
}

export interface Config {
  name: string;
  chunk_size: ConfigOption;
  chunk_overlap?: ConfigOption;
  min_characters_per_chunk?: ConfigOption;
}

export interface StoredFile {
  name: string;
  text: string;
}

export interface Workflow {
  id: string;
  name: string;
  createdAt: string;
  stage: Stage;
  file?: StoredFile;
  chunker?: string;
  chunkingConfig?: Record<string, number>;
}

// export interface Evals {
//   precision: number;
//   omega_precision: number;
//   recall: number;
//   iou: number;
// }

// export interface ChunkStats {
//   total_chunks: number;
//   avg_chars: number;
//   largest_chunk_chars: number;
//   smallest_chunk_chars: number;
//   largest_text: string;
//   smallest_text: string;
// }

// export interface RequestBody {
//   chunker_type: string;
//   provider: string;
//   chunk_size: number;
//   chunk_overlap: number;
//   tokenizer?: string;
//   min_characters_per_chunk?: number;
//   text: string;
// }
