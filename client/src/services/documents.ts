import axios from "axios";
import { z } from "zod";
import type { File } from "../types";

const filesSchema = z.array(z.string());

export const getFiles = async (): Promise<string[]> => {
  const response = await axios.get("/api/documents/");
  return filesSchema.parse(response.data);
};

export const uploadFile = async (fileDetails: File): Promise<void> => {
  await axios.post("/api/documents/", fileDetails);
};
