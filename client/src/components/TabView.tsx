import { useState } from "react";

export type Tab = "visualization" | "evaluation" | "deploy";

interface TabViewProps {
  hasEvaluation: boolean;
  defaultTab?: Tab;
  children: {
    visualization: React.ReactNode;
    evaluation: React.ReactNode;
    deploy: React.ReactNode;
  };
}

const TabView = ({ hasEvaluation, defaultTab = "visualization", children }: TabViewProps) => {
  const [activeTab, setActiveTab] = useState<Tab>(defaultTab);

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
