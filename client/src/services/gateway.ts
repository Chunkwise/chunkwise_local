import type { ChunkStats } from "../types/types";

export function getVisualizer({
  args,
}: {
  chunker: string;
  maxSize: number;
  overlap: number;
}): { stats: ChunkStats; html: string } {
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

export function getEvals() {}
