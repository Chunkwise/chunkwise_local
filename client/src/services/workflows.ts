import type { Workflow } from "../types";
import axios from "axios";

export const getWorkflows = async (): Promise<Workflow[]> => {
  const response = await axios.get("/api/workflows");
  return response.data;
};

export const createWorkflow = async (title: string): Promise<Workflow> => {
  const response = await axios.post("/api/workflows", { title });
  return response.data;
};

export const deleteWorkflow = async (workflowId: string): Promise<void> => {
  await axios.delete(`/api/workflows/${workflowId}`);
};
