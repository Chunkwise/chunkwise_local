export interface Evals {
  precision: number;
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
