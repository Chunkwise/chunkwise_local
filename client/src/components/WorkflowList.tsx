import { useState } from "react";
import type { Workflow } from "../types";

type Props = {
  workflows: Workflow[];
  selectedId?: string;
  onCreate: (name: string) => void;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
};

export default function WorkflowList({
  workflows,
  selectedId,
  onCreate,
  onSelect,
  onDelete,
}: Props) {
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState("");

  const handleCreate = () => {
    const finalName = name.trim() || `Workflow ${new Date().toLocaleString()}`;
    onCreate(finalName);
    setCreating(false);
    setName("");
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
            onChange={(event) => setName(event.target.value)}
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
            }}
          >
            Cancel
          </button>
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
            onClick={() => onSelect(workflow.id)}
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
                onClick={() => onDelete(workflow.id)}
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
}
