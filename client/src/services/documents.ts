import axios from "axios";
import type { File } from "../types";

export const getFiles = async (): Promise<string[]> => {
  const response = await axios.get("/api/documents/");
  return response.data;
};

export const uploadFile = async (content: string): Promise<File> => {
  const response = await axios.post("/api/documents/", content);
  return response.data;
};

export const deleteFile = async (documentId: string): Promise<void> => {
  await axios.delete(`/api/documents/${documentId}`);
};
