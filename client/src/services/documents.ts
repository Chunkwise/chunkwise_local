import axios from "axios";
import type { File } from "../types";

export const getFiles = async (): Promise<string[]> => {
  const response = await axios.get("/api/documents/");
  return response.data;
};

export const uploadFile = async (fileDetails: File): Promise<void> => {
  await axios.post("/api/documents/", fileDetails);
};
