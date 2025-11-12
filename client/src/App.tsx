import { useEffect, useReducer, useState } from "react";
import type { Workflow, Chunker } from "./types";
import Header from "./components/Header";
import WorkflowList from "./components/WorkflowList";
import WorkflowDetails from "./components/WorkflowDetails";
import { useLocalStorage } from "./hooks/useLocalStorage";
import type { State } from "./reducers/workflowReducer";
import { getChunkers } from "./services/chunkers";
import {
  workflowReducer,
  createWorkflowAction,
  selectWorkflowAction,
  updateWorkflowAction,
  deleteWorkflowAction,
} from "./reducers/workflowReducer";

const STORAGE_KEY = "chunkwise_workflows_v1";

function makeId() {
  return Math.random().toString(36).slice(2, 9);
}

export default function App() {
  const [stored, setStored] = useLocalStorage(STORAGE_KEY, {
    workflows: [],
    selectedWorkflowId: undefined,
  });
  const [state, dispatch] = useReducer(workflowReducer, {
    workflows: stored.workflows,
    selectedWorkflowId: stored.selectedWorkflowId,
  } as State);
  const [chunkers, setChunkers] = useState<Chunker[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setStored(state);
  }, [state, setStored]);

  // Load chunkers on mount
  useEffect(() => {
    getChunkers()
      .then((data) => setChunkers(data))
      .catch((error) => {
        console.error(error);
        setError("Failed to load chunkers from the server");
      });
  }, []);

  const selectedWorkflow = state.workflows.find(
    (workflow) => workflow.id === state.selectedWorkflowId
  );

  const handleCreateWorkflow = (name: string) => {
    const newWorkflow: Workflow = {
      id: makeId(),
      name,
      createdAt: new Date().toLocaleString(),
      stage: "Draft",
    };
    dispatch(createWorkflowAction(newWorkflow));
  };

  const handleSelectWorkflow = (id: string) => {
    dispatch(selectWorkflowAction(id));
  };

  const handleUpdateWorkflow = (id: string, patch: Partial<Workflow>) => {
    if (patch.chunker) {
      patch.stage = "Configured";
    }
    dispatch(updateWorkflowAction(id, patch));
  };

  const handleDeleteWorkflow = (id: string) => {
    dispatch(deleteWorkflowAction(id));
  };

  return (
    <div className="app-root">
      <Header />

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button
            className="error-close"
            onClick={() => setError(null)}
            aria-label="Dismiss error"
          >
            x
          </button>
        </div>
      )}

      <div className="main-layout">
        <aside className="sidebar">
          <WorkflowList
            workflows={state.workflows}
            selectedId={state.selectedWorkflowId}
            onCreateWorkflow={handleCreateWorkflow}
            onSelectWorkflow={handleSelectWorkflow}
            onDeleteWorkflow={handleDeleteWorkflow}
          />
        </aside>

        <main className="main-content">
          <WorkflowDetails
            chunkers={chunkers}
            workflow={selectedWorkflow}
            onUpdateWorkflow={(patch) =>
              state.selectedWorkflowId &&
              handleUpdateWorkflow(state.selectedWorkflowId, patch)
            }
          />
        </main>
      </div>
    </div>
  );
}
