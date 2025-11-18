import axios from "axios";
import { EvaluationMetricsSchema, type EvaluationMetrics } from "../types";

export const getEvaluationMetrics = async (
  workflowId: string
): Promise<EvaluationMetrics> => {
  const response = await axios.get(`/api/workflows/${workflowId}/evaluation`);
  return EvaluationMetricsSchema.parse(response.data);
};
