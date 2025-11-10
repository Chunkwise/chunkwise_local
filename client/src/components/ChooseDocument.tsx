import type { Workflow } from "../types";

interface ChooseDocumentProps {
  workflow: Workflow;
  onFileUpload: (file: File | null) => void;
  onSetSample: () => void;
  onRemoveFile: () => void;
  error: string | null;
}

const ChooseDocument = ({
  workflow,
  onFileUpload,
  onSetSample,
  onRemoveFile,
  error,
}: ChooseDocumentProps) => {
  return (
    <div className="details-row">
      <h2 className="section-title">Document</h2>
      <div className="box">
        <div className="file-controls">
          <label className="file-label">
            Upload .txt (max 50KB)
            <input
              className="file-input"
              type="file"
              accept=".txt"
              onChange={(event) => {
                const file = event.target.files?.[0] ?? null;
                onFileUpload(file);
                if (event.target) (event.target as HTMLInputElement).value = "";
              }}
            />
          </label>

          <button className="btn" onClick={onSetSample}>
            Use sample document
          </button>
        </div>

        {error && <div className="error">{error}</div>}
        {workflow.file ? (
          <div className="file-preview">
            <div className="file-name">{workflow.file.name}</div>
            <button
              className="btn btn-sm"
              onClick={onRemoveFile}
              title="Remove file"
            >
              x
            </button>
          </div>
        ) : (
          <div className="muted">
            No document attached! Upload or accept the sample.
          </div>
        )}
      </div>
    </div>
  );
};

export default ChooseDocument;
