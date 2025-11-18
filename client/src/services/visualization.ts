import axios from "axios";
import {
  VisualizationResponseSchema,
  type VisualizationResponse,
} from "../types";

export const getVisualization = async (
  workflowId: string
): Promise<VisualizationResponse> => {
  const response = await axios.get(
    `/api/workflows/${workflowId}/visualization`
  );
  return VisualizationResponseSchema.parse(response.data);
};
