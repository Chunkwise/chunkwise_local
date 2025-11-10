import type { Config } from "../types";
import axios from "axios";

export const getConfigs = async (): Promise<Config[]> => {
  const response = await axios.get("/api/documents/configs");
  return response.data;
};
