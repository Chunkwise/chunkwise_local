import { useEffect, useState } from "react";
import type { Workflow } from "../types";
import { getFiles, uploadFile } from "../services/documents";

interface ChooseFileProps {
  workflow: Workflow;
  onFileChange: (fileId: string | undefined) => void;
  error: string | null;
}

const ChooseFile = ({
  workflow,
  onFileChange,
  error,
}: ChooseFileProps) => {
  const [availableFiles, setAvailableFiles] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const loadFiles = async () => {
    try {
      const files = await getFiles();
      setAvailableFiles(files);
    } catch (err) {
      console.error("Failed to load files:", err);
      setUploadError("Failed to load files from server");
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  const handleFileUpload = async (file: File | null) => {
    if (!file) return;

    setUploadError(null);
    setIsLoading(true);

    try {
      const text = await file.text();
      const fileId = await uploadFile(text);
      setAvailableFiles((prev) => [...prev, fileId]);
      onFileChange(fileId);
    } catch (error) {
      console.error("Upload failed:", error);
      setUploadError("Failed to upload File");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectChange = (value: string) => {
    if (value === "") {
      onFileChange(undefined);
    } else if (value === "__upload__") {
      // Trigger file input
      document.getElementById("file-upload-input")?.click();
    } else {
      onFileChange(value);
    }
  };

  return (
    <div className="details-row">
      <h2 className="section-title">File</h2>
      <div className="box">
        <div className="file-controls">
          <select
            className="file-select"
            value={workflow.fileId || ""}
            onChange={(e) => handleSelectChange(e.target.value)}
            disabled={isLoading}
          >
            <option value="">-- Select a file --</option>
            {availableFiles.map((fileId) => (
              <option key={fileId} value={fileId}>
                {fileId}
              </option>
            ))}
            <option value="__upload__">+ Upload new file</option>
          </select>

          <input
            id="file-upload-input"
            type="file"
            accept=".txt"
            style={{ display: "none" }}
            onChange={(event) => {
              const file = event.target.files?.[0] ?? null;
              handleFileUpload(file);
              if (event.target) (event.target as HTMLInputElement).value = "";
            }}
          />
        </div>

        {(error || uploadError) && (
          <div className="error">{error || uploadError}</div>
        )}

        {isLoading && <div className="muted">Uploading...</div>}

        {workflow.fileId ? (
          <div className="file-preview">
            <div className="file-name">Selected: {workflow.fileId}</div>
            <button
              className="btn btn-sm"
              onClick={() => onFileChange(undefined)}
              title="Remove selection"
            >
              x
            </button>
          </div>
        ) : (
          <div className="muted">No document selected</div>
        )}
      </div>
    </div>
  );
};

export default ChooseFile;
