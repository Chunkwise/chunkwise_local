import type { Chunker } from "../types";
import axios from "axios";

export const getChunkers = async (): Promise<Chunker[]> => {
  const response = await axios.get("/api/documents/configs");
  return response.data;
};
