import { useState, useEffect } from "react";
import type { Workflow } from "../types";
import { getFiles, uploadFile } from "../services/documents";

interface ChooseFileProps {
  workflow: Workflow;
  onFileChange: (fileId: string | undefined) => void;
}

const ChooseFile = ({ workflow, onFileChange }: ChooseFileProps) => {
  const [availableFiles, setAvailableFiles] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load available files on mount
  useEffect(() => {
    getFiles()
      .then((files) => setAvailableFiles(files))
      .catch((error) => {
        console.error("Failed to load files:", error);
        setError("Failed to load files from the server");
      });
  }, []);

  // Handle file upload
  const handleFileUpload = async (file: File | null) => {
    if (!file) return;
    setError(null);
    setIsLoading(true);

    try {
      const title = file.name;
      const text = await file.text();
      await uploadFile({ document_title: title, document_content: text });
      setAvailableFiles((prev) => [...prev, title]);
      onFileChange(title);
    } catch (error) {
      console.error("Upload failed:", error);
      setError("Failed to upload file");
    } finally {
      setIsLoading(false);
    }
  };

  // Handle selection change
  const handleSelectChange = (value: string) => {
    if (value === "") {
      onFileChange(undefined);
    } else if (value === "__upload__") {
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
            value={workflow.fileTitle || ""}
            onChange={(event) => handleSelectChange(event.target.value)}
            disabled={isLoading}
          >
            <option value="">-- Select a file --</option>
            {availableFiles.map((fileTitle) => (
              <option key={fileTitle} value={fileTitle}>
                {fileTitle}
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

        {error && <div className="error">{error}</div>}

        {isLoading && <div className="muted">Uploading...</div>}

        {workflow.fileTitle ? (
          <div className="file-preview">
            <div className="file-name">Selected: {workflow.fileTitle}</div>
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
