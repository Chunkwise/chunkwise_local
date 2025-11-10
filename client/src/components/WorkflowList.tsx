import { useState } from 'react';
import type { Workflow } from '../types';

type Props = {
  workflows: Workflow[];
  selectedId?: string;
  onCreate: (name: string) => void;
  onSelect: (id?: string) => void;
  onDelete: (id: string) => void;
};

export default function WorkflowList({ workflows, selectedId, onCreate, onSelect, onDelete }: Props) {
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState('');

  function handleCreate() {
    const finalName = name.trim() || `Workflow ${new Date().toLocaleString()}`;
    onCreate(finalName);
    setName('');
    setCreating(false);
  }

  return (
    <div className="workflow-list">
      <div className="workflow-list-header">
        <button
          className="btn btn-primary"
          onClick={() => {
            setCreating((s) => !s);
          }}
        >
          + Create Workflow
        </button>
      </div>

      {creating && (
        <div className="create-row">
          <input
            className="input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Workflow name"
          />
          <button className="btn" onClick={handleCreate}>
            Create
          </button>
          <button
            className="btn btn-ghost"
            onClick={() => {
              setCreating(false);
              setName('');
            }}
          >
            Cancel
          </button>
        </div>
      )}

      <div className="workflow-items">
        {workflows.length === 0 && <div className="muted">No workflows yet. Create one to start.</div>}
        {workflows.map((w) => (
          <div
            key={w.id}
            className={`workflow-item ${selectedId === w.id ? 'selected' : ''}`}
            onClick={() => onSelect(w.id)}
          >
            <div className="wi-left">
              <div className="wi-name">{w.name}</div>
              <div className="wi-meta">
                <span className="wi-date">{new Date(w.createdAt).toLocaleString()}</span>
                <span className="wi-stage">{w.stage}</span>
              </div>
            </div>
            <div className="wi-actions">
              <button
                className="btn btn-sm"
                onClick={(ev) => {
                  ev.stopPropagation();
                  onDelete(w.id);
                }}
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
