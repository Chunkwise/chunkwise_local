import { render, screen } from '@testing-library/react';
import VisualizationDisplay from '../components/VisualizationDisplay';

describe('VisualizationDisplay', () => {
  it('renders html content', () => {
    const html = '<div data-testid="viz-content">Hello Viz</div>';
    render(<VisualizationDisplay html={html} />);

    expect(screen.getByText('Visualization')).toBeInTheDocument();
    expect(screen.getByTestId('viz-content')).toBeInTheDocument();
    expect(screen.getByText('Hello Viz')).toBeInTheDocument();
  });
});
