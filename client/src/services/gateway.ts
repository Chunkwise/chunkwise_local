import type { ChunkStats, Evals } from "../types/types";

type Args = {
  chunker: string;
  maxSize: number;
  overlap: number;
};

export async function getVisualizer({
  chunker,
  maxSize,
  overlap,
}: Args): Promise<{
  stats: ChunkStats;
  html: string;
}> {
  //  Get visualizer and/or stats
  return {
    stats: {
      total: 100,
      avgSize: 10,
      largestSize: 20,
      smallestSize: 1,
      largestText: "example of largest",
      smallestText: "examples of smallest",
    },
    html: '<p style="color=green">example html<p>',
  };
}

export async function getEvals({
  chunker,
  maxSize,
  overlap,
}: Args): Promise<Evals> {
  // get evals from backend
  return {
    precision: 0.1,
    recall: 0.2,
    iou: 0.3,
  };
}
