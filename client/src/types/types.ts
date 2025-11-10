export interface Config {
  name: string;
  chunk_size: {
    min: number;
    max: number;
    default: number;
  };
  chunk_overlap?: {
    min: number;
    max: number;
    default: number;
  };
  min_characters_per_chunk?: {
    min: number;
    max: number;
    default: number;
  };
  min_characters_per_sentence?: {
    min: number;
    max: number;
    default: number;
  };
}

export interface Evals {
  precision: number;
  omega_precision: number;
  recall: number;
  iou: number;
}

export interface ChunkStats {
  total_chunks: number;
  avg_chars: number;
  largest_chunk_chars: number;
  smallest_chunk_chars: number;
  largest_text: string;
  smallest_text: string;
}

export interface RequestBody {
  chunker_type: string;
  provider: string;
  chunk_size: number;
  chunk_overlap: number;
  tokenizer?: string;
  min_characters_per_chunk?: number;
  text: string;
}

export type ChunkerSelection =
  | "Chonkie Token"
  | "Chonkie Recursive"
  | "Chonkie Sentence"
  | "Chonkie Semantic"
  | "Chonkie Slumber"
  | "LangChain Token"
  | "LangChain Recursive"
  | "LangChain Character";
