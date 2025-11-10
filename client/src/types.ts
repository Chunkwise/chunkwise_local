export type Stage = "Draft" | "Configured" | "Evaluated";

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
