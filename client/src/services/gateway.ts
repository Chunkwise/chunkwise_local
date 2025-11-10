import type { ChunkerSelection, ChunkStats, Evals, Config } from "../types";
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
    `http://localhost:8000/api/visualize`,
    requestBody
  );

  return data;
}

export async function getEvals(configuration: Args): Promise<Evals> {
  const requestBody = createRequestBody({ ...configuration, text });
  const { data } = await axios.post(
    "http://localhost:8000/api/evaluate",
    requestBody
  );

  return data;
}

export async function getConfigs(): Promise<Config[]> {
  const { data } = await axios.get("http://localhost:8000/api/configs");

  return data;
}
