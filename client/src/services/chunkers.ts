import { z } from "zod";
import { ChunkerSchema } from "../types";
import type { Chunker } from "../types";
import axios from "axios";

const chunkerListSchema = z.array(ChunkerSchema);

export const getChunkers = async (): Promise<Chunker[]> => {
  const response = await axios.get("/api/configs");
  return chunkerListSchema.parse(response.data);
};
