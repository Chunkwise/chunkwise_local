import { useEffect, useState } from "react";
import type { Workflow } from "../types";
import { uploadFile } from "../services/documents";
import ErrorMessage from "./ErrorMessage";

interface ChooseFileProps {
  workflow: Workflow;
  isLoadingFiles: boolean;
  availableFiles: string[];
  onFileChange: (fileId: string | undefined) => void;
}

const UPLOAD_OPTION_VALUE = "__upload__";
const MAX_FILE_SIZE_KB = 100;

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

  // Handler for file upload
  const handleFileUpload = async (file: File | null) => {
    if (!file) return;
    setError(null);

    if (file.size > MAX_FILE_SIZE_KB * 1024) {
      setError(`File size exceeds ${MAX_FILE_SIZE_KB}KB limit`);
      return;
    }

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

  // Handler for file change
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
    <div className="section">
      <h2 className="section-header">
        <span className="icon">description</span>
        <span className="title-md">File</span>
      </h2>
      <div className="card">
        <div className="file-controls">
          <select
            className="select"
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

        {error && (
          <ErrorMessage message={error} onDismiss={() => setError(null)} />
        )}

        {isLoadingFiles && (
          <div className="text-muted flex items-center gap-2 mt-2">
            <span className="icon spinner">sync</span>
            Loading available files...
          </div>
        )}

        {isUploadingFile && (
          <div className="text-muted flex items-center gap-2 mt-2">
            <span className="icon spinner">sync</span>
            Uploading...
          </div>
        )}

        {workflow.document_title ? (
          <div className="file-preview">
            <span className="icon">insert_drive_file</span>
            <span className="file-name">{workflow.document_title}</span>
            <button
              className="btn btn-icon btn-sm"
              onClick={() => onFileChange(undefined)}
              title="Remove selection"
            >
              <span className="icon icon-sm">close</span>
            </button>
          </div>
        ) : (
          <div className="text-muted mt-2">
            <span className="icon icon-sm">info</span>
            No document selected
          </div>
        )}
      </div>
    </div>
  );
};

export default ChooseFile;
