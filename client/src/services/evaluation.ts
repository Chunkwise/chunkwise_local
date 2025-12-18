import axios from "axios";
import { EvaluationResponseSchema, type EvaluationResponse } from "../types";

export const getEvaluation = async (
  workflowId: string
): Promise<EvaluationResponse> => {
  const response = await axios.get(`/api/workflows/${workflowId}/evaluation`, {
    timeout: 300000,
  });
  return EvaluationResponseSchema.parse(response.data);
};
