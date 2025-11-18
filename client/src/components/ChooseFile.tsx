import { useEffect, useState } from "react";
import type { Workflow } from "../types";
import { uploadFile } from "../services/documents";

interface ChooseFileProps {
  workflow: Workflow;
  isLoadingFiles: boolean;
  availableFiles: string[];
  onFileChange: (fileId: string | undefined) => void;
}

const UPLOAD_OPTION_VALUE = "__upload__";

const ChooseFile = ({
  workflow,
  isLoadingFiles,
  availableFiles,
  onFileChange,
}: ChooseFileProps) => {
  const [files, setFiles] = useState<string[]>([]);
  const [isUploadingFile, setIsUploadingFile] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sync with availableFiles
  useEffect(() => {
    setFiles(availableFiles);
  }, [availableFiles]);

  // Helper to remove .txt extension
  const removeExtension = (filename: string): string => {
    return filename.endsWith(".txt") ? filename.slice(0, -4) : filename;
  };

  const handleFileUpload = async (file: File | null) => {
    if (!file) return;
    setError(null);
    setIsUploadingFile(true);

    try {
      const title = removeExtension(file.name);
      const text = await file.text();
      await uploadFile({ document_title: title, document_content: text });
      setFiles((prev) => (prev.includes(title) ? prev : [...prev, title]));
      onFileChange(title);
    } catch (error) {
      console.error("Upload failed:", error);
      setError("Failed to upload file");
    } finally {
      setIsUploadingFile(false);
    }
  };

  const handleSelectChange = (value: string) => {
    if (value === "") {
      onFileChange(undefined);
    } else if (value === UPLOAD_OPTION_VALUE) {
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
            value={workflow.document_title || ""}
            onChange={(event) => handleSelectChange(event.target.value)}
            disabled={isLoadingFiles || isUploadingFile}
          >
            <option value="">-- Select a file --</option>
            {files.map((title) => (
              <option key={title} value={title}>
                {title}
              </option>
            ))}
            <option value={UPLOAD_OPTION_VALUE}>+ Upload new file</option>
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

        {isLoadingFiles && (
          <div className="muted">Loading available files...</div>
        )}

        {isUploadingFile && <div className="muted">Uploading...</div>}

        {workflow.document_title ? (
          <div className="file-preview">
            <div className="file-name">Selected: {workflow.document_title}</div>
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
