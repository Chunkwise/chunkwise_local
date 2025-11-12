import { useEffect, useReducer, useState } from "react";
import type { Workflow, Config } from "./types";
import Header from "./components/Header";
import WorkflowList from "./components/WorkflowList";
import WorkflowDetails from "./components/WorkflowDetails";
import { useLocalStorage } from "./hooks/useLocalStorage";
import type { State } from "./reducers/workflowReducer";
import { getConfigs } from "./services/configs";
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
  const [configs, setConfigs] = useState<Config[]>([]);

  useEffect(() => {
    setStored(state);
  }, [state, setStored]);

  useEffect(() => {
    getConfigs()
      .then((data) => setConfigs(data))
      .catch((error) => {
        console.error(error);
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
            configs={configs}
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
