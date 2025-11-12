// import axios from "axios";
import type { File } from "../types";

const MOCK_FILES = ["file1.txt", "file2.txt", "file3.txt"];

// Mock getFiles function
export const getFiles = async (): Promise<string[]> => {
  return MOCK_FILES;
};

// export const getFiles = async (): Promise<string[]> => {
//   const response = await axios.get("/api/documents/");
//   return response.data;
// };

// Mock uploadFile function
export const uploadFile = async (fileDetails: File): Promise<void> => {
  MOCK_FILES.push(fileDetails.document_title);
};

// export const uploadFile = async (fileDetails: File): Promise<void> => {
//   await axios.post("/api/documents/", fileDetails);
// };
