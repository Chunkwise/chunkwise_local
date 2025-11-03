import type { ChunkStats, Evals } from "../types/types";
import createRequestBody from "../utils/createRequestBody";
import axios from "axios";

type Args = {
  chunker: string;
  maxSize: number;
  overlap: number;
};

interface VisualizerOutput {
  stats: ChunkStats;
  html: string;
}

export async function getVisualizer({
  chunker,
  maxSize,
  overlap,
}: Args): Promise<VisualizerOutput> {
  const requestBody = createRequestBody(chunker, maxSize, overlap);

  const { data } = await axios.post(
    `http://localhost:8000/visualize`,
    requestBody
  );

  return data;
}

export async function getEvals({
  chunker,
  maxSize,
  overlap,
}: Args): Promise<Evals> {
  // get evals from backend
  return {
    precision: 0.1,
    omegaPrecision: 1.5,
    recall: 0.2,
    iou: 0.3,
  };
}
