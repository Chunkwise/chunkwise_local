import { useState } from "react";
import type { Workflow } from "../types";

type Props = {
  workflows: Workflow[];
  selectedId?: string;
  onCreateWorkflow: (name: string) => void;
  onSelectWorkflow: (id: string) => void;
  onDeleteWorkflow: (id: string) => void;
};

const WorkflowList = ({
  workflows,
  selectedId,
  onCreateWorkflow,
  onSelectWorkflow,
  onDeleteWorkflow,
}: Props) => {
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleCreate = () => {
    const trimmedName = name.trim();

    // Validate name length
    if (trimmedName.length === 0) {
      setValidationError("Workflow name cannot be empty");
      return;
    }
    if (trimmedName.length > 50) {
      setValidationError("Workflow name cannot exceed 50 characters");
      return;
    }

    // Validate characters
    if (!/^[a-zA-Z0-9\s]+$/.test(trimmedName)) {
      setValidationError(
        "Workflow name can only contain letters, numbers, and spaces"
      );
      return;
    }

    onCreateWorkflow(trimmedName);
    setCreating(false);
    setName("");
    setValidationError(null);
  };

  return (
    <div className="workflow-list">
      <div className="workflow-list-header">
        <button
          className="btn btn-primary"
          onClick={() => {
            setCreating(!creating);
          }}
        >
          + Create workflow
        </button>
      </div>

      {creating && (
        <div className="create-row">
          <input
            className="input"
            value={name}
            onChange={(event) => {
              setName(event.target.value);
              setValidationError(null);
            }}
            placeholder="Workflow name"
          />
          <button className="btn" onClick={handleCreate}>
            Create
          </button>
          <button
            className="btn btn-ghost"
            onClick={() => {
              setCreating(false);
              setName("");
              setValidationError(null);
            }}
          >
            Cancel
          </button>
          {validationError && (
            <div
              style={{
                color: "red",
                fontSize: "0.875rem",
                marginTop: "0.5rem",
              }}
            >
              {validationError}
            </div>
          )}
        </div>
      )}

      <div className="workflow-items">
        {workflows.length === 0 && (
          <div className="muted">No workflows yet! Create some to start.</div>
        )}
        {workflows.map((workflow) => (
          <div
            key={workflow.id}
            className={`workflow-item ${
              selectedId === workflow.id ? "selected" : ""
            }`}
            onClick={() => onSelectWorkflow(workflow.id)}
          >
            <div className="wi-left">
              <div className="wi-name">{workflow.name}</div>
              <div className="wi-meta">
                <span className="wi-date">{workflow.createdAt}</span>
                <span className="wi-stage">{workflow.stage}</span>
              </div>
            </div>
            <div className="wi-actions">
              <button
                className="btn btn-sm"
                onClick={() => onDeleteWorkflow(workflow.id)}
                title="Delete"
              >
                x
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WorkflowList;
