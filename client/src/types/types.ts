export interface Evals {
  precision: number;
  omegaPrecision: number;
  recall: number;
  iou: number;
}

export interface ChunkStats {
  total: number;
  avgSize: number;
  largestSize: number;
  smallestSize: number;
  largestText: string;
  smallestText: string;
}

export interface RequestBody {
  chunker_type: string;
  provider: string;
  chunk_size: number;
  chunk_overlap: number;
  text: string;
}
