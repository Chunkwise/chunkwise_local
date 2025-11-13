import axios from "axios";
import type { EvaluationMetrics } from "../types";

// Real implementation (commented out until evaluation server is ready)
export const getEvaluationMetrics = async (
  workflowId: string
): Promise<EvaluationMetrics> => {
  const response = await axios.get(`/api/workflows/${workflowId}/evaluation`);
  return response.data;
};

// export const getEvaluationMetrics = async (
//   // eslint-disable-next-line @typescript-eslint/no-unused-vars
//   _workflowId: string
// ): Promise<EvaluationMetrics> => {
//   await new Promise((resolve) => setTimeout(resolve, 1500));
//   return {
//     precision_mean: 0.708,
//     recall_mean: 0.715,
//     iou_mean: 0.65,
//     precision_omega_mean: 0.725,
//   };
// };
