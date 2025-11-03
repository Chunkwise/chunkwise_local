import type { ChunkerSelection, ChunkStats, Evals } from "../types/types";
import createRequestBody from "../utils/createRequestBody";
import axios from "axios";
import { text } from "../dataset/rumpelstiltskin";

type Args = {
  chunker: ChunkerSelection;
  size: number;
  overlap: number;
  min_characters_per_chunk?: number;
  tokenizer?: string;
};

interface VisualizationOutput {
  stats: ChunkStats;
  html: string;
}

export async function getVisualization(
  configuration: Args
): Promise<VisualizationOutput> {
  const requestBody = createRequestBody({ ...configuration, text });
  const { data } = await axios.post(
    `http://localhost:8000/visualize`,
    requestBody
  );

  return data;
}

export async function getEvals(configuration: Args): Promise<Evals> {
  const requestBody = createRequestBody({ ...configuration, text });
  const { data } = await axios.post(
    "http://localhost:8000/evaluate",
    requestBody
  );

  return data;
}
