import { useState } from "react";

interface TabViewProps {
  hasEvaluation: boolean;
  children: {
    visualization: React.ReactNode;
    evaluation: React.ReactNode;
  };
}

type Tab = "visualization" | "evaluation";

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
          Chunk Visualization
        </button>
        <button
          className={`tab-button ${activeTab === "evaluation" ? "active" : ""}`}
          onClick={() => setActiveTab("evaluation")}
          disabled={!hasEvaluation}
        >
          Evaluation
        </button>
      </div>
      <div className="tab-content">
        {activeTab === "visualization"
          ? children.visualization
          : children.evaluation}
      </div>
    </div>
  );
};

export default TabView;
