import { useEffect, useReducer, useState } from "react";
import axios from "axios";
import type { Workflow, Config } from "./types";
import Header from "./components/Header";
import WorkflowList from "./components/WorkflowList";
import WorkflowDetails from "./components/WorkflowDetails";
import { useLocalStorage } from "./hooks/useLocalStorage";
import type { State } from "./reducers/workflowReducer";
import { workflowReducer } from "./reducers/workflowReducer";
import "./styles.css";

const STORAGE_KEY = "chunkwise_workflows_v1";

function makeId() {
  return Math.random().toString(36).slice(2, 9);
}

const SAMPLE_DOC_NAME = "sample-document.txt";
const SAMPLE_DOC_TEXT = `This is a short sample document used for chunker testing.
You can replace this with your own .txt file (max 50KB).`;

export default function App() {
  const [stored, setStored] = useLocalStorage<State>(STORAGE_KEY, {
    workflows: [],
  });
  const [state, dispatch] = useReducer(workflowReducer, {
    workflows: stored.workflows ?? [],
    selectedWorkflowId: stored.selectedWorkflowId,
  } as State);

  useEffect(() => {
    setStored(state);
  }, [state, setStored]);

  // Fetch chunker configs
  const [configs, setConfigs] = useState<Config[]>([]);
  const [configsError, setConfigsError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    axios
      .get<Config[]>("/api/documents/configs")
      .then((r) => {
        if (!cancelled) setConfigs(r.data);
      })
      .catch((e) => {
        if (!cancelled) {
          setConfigsError("Failed to load chunker configs from server.");
          console.error(e);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    dispatch({ type: "INIT", workflows: stored.workflows ?? [] });
  }, [stored.workflows]);

  const createWorkflow = (name: string) => {
    const newW: Workflow = {
      id: makeId(),
      name,
      createdAt: new Date().toISOString(),
      stage: "draft",
    };
    dispatch({ type: "CREATE_WORKFLOW", workflow: newW });
  };

  const selectWorkflow = (id?: string) => {
    dispatch({ type: "SELECT_WORKFLOW", id });
  };

  const updateWorkflow = (id: string, patch: Partial<Workflow>) => {
    const patch2 = { ...patch };
    if (patch.chunker) {
      patch2.stage = "configured";
    }
    dispatch({ type: "UPDATE_WORKFLOW", id, patch: patch2 });
  };

  const selectedWorkflow = state.workflows.find(
    (w) => w.id === state.selectedWorkflowId
  );

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
            configsError={configsError}
            sampleDoc={{ name: SAMPLE_DOC_NAME, text: SAMPLE_DOC_TEXT }}
            onUpdate={(patch) =>
              selectedWorkflow && updateWorkflow(selectedWorkflow.id, patch)
            }
          />
        </main>
      </div>
    </div>
  );
}
