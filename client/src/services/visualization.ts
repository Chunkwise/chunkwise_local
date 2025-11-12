import axios from "axios";
import type { VisualizationResponse } from "../types";

export const getVisualization = async (
  workflowId: string
): Promise<VisualizationResponse> => {
  const response = await axios.post(
    `/api/workflows/${workflowId}/visualization`
  );
  return response.data;
};
