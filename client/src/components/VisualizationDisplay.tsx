interface VisualizationDisplayProps {
  html: string;
}

const VisualizationDisplay = ({ html }: VisualizationDisplayProps) => {
  return (
    <div className="details-row">
      <h2 className="section-title">Visualization</h2>
      <div className="box">
        <div
          className="visualization-container"
          dangerouslySetInnerHTML={{ __html: JSON.parse(html) }}
        />
      </div>
    </div>
  );
};

export default VisualizationDisplay;
