import type { Workflow } from "../types";
import axios from "axios";

// Helper function to parse workflow fields
const parseWorkflowFields = (workflow: Record<string, unknown>): Workflow => {
  const parsed = { ...workflow };

  // Parse chunking_strategy
  if (
    typeof parsed.chunking_strategy === "string" &&
    parsed.chunking_strategy !== ""
  ) {
    try {
      parsed.chunking_strategy = JSON.parse(parsed.chunking_strategy);
    } catch (error) {
      console.error("Failed to parse chunking_strategy:", error);
      parsed.chunking_strategy = undefined;
    }
  }

  // Parse chunks_stats
  if (typeof parsed.chunks_stats === "string" && parsed.chunks_stats !== "") {
    try {
      parsed.chunks_stats = JSON.parse(parsed.chunks_stats);
    } catch (error) {
      console.error("Failed to parse chunks_stats:", error);
      parsed.chunks_stats = undefined;
    }
  }

  // Parse evaluation_metrics
  if (
    typeof parsed.evaluation_metrics === "string" &&
    parsed.evaluation_metrics !== ""
  ) {
    try {
      parsed.evaluation_metrics = JSON.parse(parsed.evaluation_metrics);
    } catch (error) {
      console.error("Failed to parse evaluation_metrics:", error);
      parsed.evaluation_metrics = undefined;
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
