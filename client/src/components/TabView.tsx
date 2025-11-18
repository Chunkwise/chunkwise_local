import { useState } from "react";

interface TabViewProps {
  hasEvaluation: boolean;
  children: {
    visualization: React.ReactNode;
    evaluation: React.ReactNode;
    deploy: React.ReactNode;
  };
}

type Tab = "visualization" | "evaluation" | "deploy";

const TabView = ({ hasEvaluation, children }: TabViewProps) => {
  const [activeTab, setActiveTab] = useState<Tab>("visualization");

  return (
    <div className="tab-view">
      <div className="tab-nav">
        <button
          className={`tab-button ${
            activeTab === "visualization" ? "active" : ""
          }`}
          onClick={() => setActiveTab("visualization")}
        >
          Visualization
        </button>
        <button
          className={`tab-button ${
            activeTab === "evaluation" ? "active" : ""
          }`}
          onClick={() => setActiveTab("evaluation")}
          disabled={!hasEvaluation}
        >
          Evaluation
        </button>
        <button
          className={`tab-button ${activeTab === "deploy" ? "active" : ""}`}
          onClick={() => setActiveTab("deploy")}
        >
          Deploy
        </button>
      </div>
      <div className="tab-content">
        {activeTab === "visualization"
          ? children.visualization
          : activeTab === "evaluation"
            ? children.evaluation
            : children.deploy}
      </div>
    </div>
  );
};

export default TabView;
