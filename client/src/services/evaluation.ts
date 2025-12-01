// import axios from "axios";
// import { EvaluationResponseSchema, type EvaluationResponse } from "../types";

// export const getEvaluation = async (
//   workflowId: string
// ): Promise<EvaluationResponse> => {
//   const response = await axios.get(`/api/workflows/${workflowId}/evaluation`);
//   return EvaluationResponseSchema.parse(response.data);
// };

// For local testing on Saurabh's machine
import { type EvaluationResponse } from "../types";
export const getEvaluation = async (
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  _workflowId: string
): Promise<EvaluationResponse> => {
  await new Promise((resolve) => setTimeout(resolve, 1500));
  return {
    embedding_model: "text-embedding-ada-002",
    corpus_id: "corpus-12345",
    document_s3_key: "documents/sample-doc.pdf",
    queries_s3_key:
      "queries/generated-queries-12345.json",
    queries_generated: true,
    num_queries: 50,
    chunkers_evaluated: ["langchain recursive"],
    results: [
      {
        precision_mean: 0.708,
        recall_mean: 0.715,
        iou_mean: 0.65,
        precision_omega_mean: 0.725,
      },
    ],
  };
};
