import type { ChunkStats, Evals } from "../types/types";
import createRequestBody from "../utils/createRequestBody";
import axios from "axios";
import { text } from "../dataset/rumpelstiltskin";

type Args = {
  chunker: string;
  size: number;
  overlap: number;
};

interface VisualizerOutput {
  stats: ChunkStats;
  html: string;
}

export async function getVisualizer({
  chunker,
  size,
  overlap,
}: Args): Promise<VisualizerOutput> {
  const requestBody = createRequestBody(chunker, size, overlap, text);
  const { data } = await axios.post(
    `http://localhost:8000/visualize`,
    requestBody
  );

  return data;
}

export async function getEvals({
  chunker,
  size,
  overlap,
}: Args): Promise<Evals> {
  const requestBody = createRequestBody(chunker, size, overlap, text);
  const { data } = await axios.post(
    "http://localhost:8000/evaluate",
    requestBody
  );

  return data;
}
