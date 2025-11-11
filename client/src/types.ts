export type Stage = "Draft" | "Configured" | "Evaluated";

export interface ConfigOption {
  type: string;
  min: number;
  max: number;
  default: number;
}

export interface Config {
  name: string;
  [key: string]: string | ConfigOption;
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
  fileId?: string;
  chunker?: string;
  chunkingConfig?: Record<string, number>;
}
