import { useEffect, useReducer, useState } from "react";
import type { Workflow, Config } from "./types";
import Header from "./components/Header";
import WorkflowList from "./components/WorkflowList";
import WorkflowDetails from "./components/WorkflowDetails";
import { useLocalStorage } from "./hooks/useLocalStorage";
import type { State } from "./reducers/workflowReducer";
import { workflowReducer } from "./reducers/workflowReducer";
import { getConfigs } from "./services/getConfigs";
import sampleText from "./assets/about_git_sample_text.txt?raw";

const STORAGE_KEY = "chunkwise_workflows_v1";

function makeId() {
  return Math.random().toString(36).slice(2, 9);
}

export default function App() {
  const [stored, setStored] = useLocalStorage<State>(STORAGE_KEY, {
    workflows: [],
  });
  const [state, dispatch] = useReducer(workflowReducer, {
    workflows: stored.workflows,
    selectedWorkflowId: stored.selectedWorkflowId,
  } as State);
  const [configs, setConfigs] = useState<Config[]>([]);
  const sampleDoc = { name: "about_git.txt", text: sampleText };

  useEffect(() => {
    getConfigs()
      .then((data) => setConfigs(data))
      .catch((error) => {
        console.error(error);
      });
  }, []);

  const createWorkflow = (name: string) => {
    const newWorkflow: Workflow = {
      id: makeId(),
      name,
      createdAt: new Date().toLocaleString(),
      stage: "Draft",
    };
    dispatch({ type: "CREATE_WORKFLOW", workflow: newWorkflow });
  };

  const selectWorkflow = (id: string) => {
    dispatch({ type: "SELECT_WORKFLOW", id });
  };

  const selectedWorkflow = state.workflows.find(
    (workflow) => workflow.id === state.selectedWorkflowId
  );

  const updateWorkflow = (id: string, patch: Partial<Workflow>) => {
    if (patch.chunker) {
      patch.stage = "Configured";
    }
    dispatch({ type: "UPDATE_WORKFLOW", id, patch: patch });
  };

  useEffect(() => {
    setStored(state);
  }, [state, setStored]);

  return (
    <div className="app-root">
      <Header />
      <div className="main-layout">
        <aside className="sidebar">
          <WorkflowList
            workflows={state.workflows}
            onCreate={createWorkflow}
            onSelect={selectWorkflow}
            selectedId={state.selectedWorkflowId}
            onDelete={(id) => dispatch({ type: "DELETE_WORKFLOW", id })}
          />
        </aside>

        <main className="main-content">
          <WorkflowDetails
            workflow={selectedWorkflow}
            configs={configs}
            sampleDoc={sampleDoc}
            onUpdate={(patch) =>
              selectedWorkflow && updateWorkflow(selectedWorkflow.id, patch)
            }
          />
        </main>
      </div>
    </div>
  );
}
