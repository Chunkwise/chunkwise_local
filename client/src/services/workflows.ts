import type { Workflow } from "../types";
import axios from "axios";

// Helper function to parse workflow fields
const parseWorkflowFields = (workflow: Record<string, unknown>): Workflow => {
  const parsed = { ...workflow };
  const jsonFields = [
    "chunking_strategy",
    "chunks_stats",
    "evaluation_metrics",
  ] as const;

  for (const key of jsonFields) {
    const val = parsed[key];
    if (typeof val === "string" && val !== "") {
      try {
        parsed[key] = JSON.parse(val);
      } catch (error) {
        console.error(`Failed to parse ${key}:`, error);
        parsed[key] = undefined;
      }
    }
  }

  return parsed as unknown as Workflow;
};

export const getWorkflows = async (): Promise<Workflow[]> => {
  const response = await axios.get("/api/workflows");
  return response.data.map(parseWorkflowFields);
};

export const createWorkflow = async (title: string): Promise<Workflow> => {
  const response = await axios.post("/api/workflows", { title });
  return parseWorkflowFields(response.data);
};

export const updateWorkflow = async (
  workflowId: string,
  patch: Partial<Workflow>
): Promise<Workflow> => {
  const response = await axios.put(`/api/workflows/${workflowId}`, patch);
  return parseWorkflowFields(response.data);
};

export const deleteWorkflow = async (workflowId: string): Promise<void> => {
  await axios.delete(`/api/workflows/${workflowId}`);
};
