import { useState } from "react";
import type { Workflow } from "../types";
import ErrorMessage from "./ErrorMessage";

type Props = {
  isLoadingWorkflows?: boolean;
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
  isLoadingWorkflows,
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

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

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
      <div className="workflow-header">
        <div className="workflow-header-left">
          <h3 className="title-md">
            Workflows{" "}
            {isComparing && (
              <span className="text-muted">
                ({comparedWorkflowIds.length}/4)
              </span>
            )}
          </h3>
        </div>
        <div className="workflow-header-actions">
          {!isComparing ? (
            <button
              className="btn btn-primary"
              onClick={() => {
                setCreating(!creating);
              }}
            >
              <span className="icon icon-sm">add</span>
              New
            </button>
          ) : null}
          <button
            className="btn"
            onClick={() => {
              if (isComparing) {
                onExitComparison();
              } else {
                onEnterComparison();
              }
            }}
            disabled={workflows.length < 2}
          >
            <span className="icon icon-sm">compare_arrows</span>
            {isComparing ? "Exit" : "Compare"}
          </button>
        </div>
      </div>

      {creating && (
        <div className="create-form">
          <input
            className="input"
            value={name}
            onChange={(event) => {
              setName(event.target.value);
              setValidationError(null);
            }}
            placeholder="Workflow name"
          />
          <button className="btn btn-primary" onClick={handleCreate}>
            <span className="icon icon-sm">check</span>
            Create
          </button>
          <button
            className="btn btn-outline"
            onClick={() => {
              setCreating(false);
              setName("");
              setValidationError(null);
            }}
          >
            <span className="icon icon-sm">close</span>
            Cancel
          </button>
          {validationError && (
            <ErrorMessage
              message={validationError}
              onDismiss={() => setValidationError(null)}
            />
          )}
        </div>
      )}

      <div className="workflow-items">
        {isLoadingWorkflows ? (
          <div className="placeholder">
            <span className="icon icon-lg spinner">sync</span>
            <span>Loading workflows...</span>
          </div>
        ) : workflows.length === 0 ? (
          <div className="placeholder">
            <span className="icon icon-lg">inbox</span>
            <span>No workflows yet. Create one to start.</span>
          </div>
        ) : null}
        {!isLoadingWorkflows &&
          workflows.map((workflow) => (
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
              <div className="workflow-item-left">
                <div className="workflow-item-name">{workflow.title}</div>
                <div className="workflow-item-meta">
                  <span className="workflow-date">
                    {formatDate(workflow.created_at)}
                  </span>
                  <span
                    className={`workflow-stage stage-${workflow.stage?.toLowerCase()}`}
                  >
                    {workflow.stage}
                  </span>
                </div>
              </div>
              <div className="workflow-item-actions">
                <input
                  type="checkbox"
                  className="checkbox"
                  checked={comparedWorkflowIds.includes(workflow.id)}
                  onChange={() => onToggleWorkflowComparison(workflow.id)}
                  onClick={(event) => event.stopPropagation()}
                  style={{ display: isComparing ? "block" : "none" }}
                />
                <button
                  className="btn btn-icon btn-sm"
                  onClick={(event) => {
                    event.stopPropagation();
                    onDeleteWorkflow(workflow.id);
                  }}
                  title="Delete"
                  style={{ display: isComparing ? "none" : "flex" }}
                >
                  <span className="icon icon-sm">delete</span>
                </button>
              </div>
            </div>
          ))}
      </div>
    </div>
  );
};

export default WorkflowList;
