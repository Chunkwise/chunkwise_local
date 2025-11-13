import { useState } from "react";
import type { Workflow } from "../types";

type Props = {
  workflows: Workflow[];
  selectedId?: string;
  isComparing: boolean;
  comparedWorkflowIds: string[];
  onCreateWorkflow: (name: string) => void;
  onSelectWorkflow: (id: string) => void;
  onDeleteWorkflow: (id: string) => void;
  onEnterComparison: () => void;
  onExitComparison: () => void;
  onToggleWorkflowComparison: (id: string) => void;
};

const WorkflowList = ({
  workflows,
  selectedId,
  isComparing,
  comparedWorkflowIds,
  onCreateWorkflow,
  onSelectWorkflow,
  onDeleteWorkflow,
  onEnterComparison,
  onExitComparison,
  onToggleWorkflowComparison,
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

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <div className="workflow-list">
      <div className="workflow-list-header">
        <div className="workflow-list-title">
          <h3>Workflows</h3>
          {isComparing && (
            <p className="workflow-list-subtitle">
              Select up to 3 ({comparedWorkflowIds.length}/3)
            </p>
          )}
        </div>
        {!isComparing ? (
          <button
            className="btn btn-primary"
            onClick={() => {
              setCreating(!creating);
            }}
          >
            + New
          </button>
        ) : null}
        <button
          className="btn btn-compare"
          onClick={() => {
            if (isComparing) {
              onExitComparison();
            } else {
              onEnterComparison();
            }
          }}
          disabled={workflows.length < 2}
        >
          {isComparing ? "Cancel" : "Compare"}
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
              selectedId === workflow.id && !isComparing ? "selected" : ""
            } ${
              isComparing && comparedWorkflowIds.includes(workflow.id)
                ? "compared"
                : ""
            }`}
            onClick={() => {
              if (isComparing) {
                onToggleWorkflowComparison(workflow.id);
              } else {
                onSelectWorkflow(workflow.id);
              }
            }}
          >
            {isComparing && (
              <input
                type="checkbox"
                className="workflow-checkbox"
                checked={comparedWorkflowIds.includes(workflow.id)}
                onChange={() => onToggleWorkflowComparison(workflow.id)}
                onClick={(event) => event.stopPropagation()}
              />
            )}
            <div className="wi-left">
              <div className="wi-name">{workflow.title}</div>
              <div className="wi-meta">
                <span className="wi-date">
                  {formatDate(workflow.created_at)}
                </span>
                <span className="wi-stage">{workflow.stage}</span>
              </div>
            </div>
            {!isComparing && (
              <div className="wi-actions">
                <button
                  className="btn btn-sm"
                  onClick={(event) => {
                    event.stopPropagation();
                    onDeleteWorkflow(workflow.id);
                  }}
                  title="Delete"
                >
                  x
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default WorkflowList;
