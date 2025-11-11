import axios from "axios";
import type { VisualizationResponse } from "../types";

export const getVisualization = async (
  documentId: string,
  chunkerConfig: {
    chunker_type: string;
    [key: string]: string | number;
  }
): Promise<VisualizationResponse> => {
  const response = await axios.post(
    `/api/documents/${documentId}/visualization`,
    chunkerConfig
  );
  return response.data;
};
