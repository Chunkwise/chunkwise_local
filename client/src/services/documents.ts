import axios from "axios";

export const getFiles = async (): Promise<string[]> => {
  const response = await axios.get("/api/documents/");
  return response.data;
};

export const uploadFile = async (content: string): Promise<string> => {
  const response = await axios.post("/api/documents/", content, {
    headers: {
      "Content-Type": "application/json",
    },
  });
  return response.data.document_id;
};

export const deleteFile = async (documentId: string): Promise<void> => {
  await axios.delete(`/api/documents/${documentId}`);
};
