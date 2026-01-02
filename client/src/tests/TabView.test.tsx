import { render, screen, fireEvent } from '@testing-library/react';
import TabView from '../components/TabView';

describe('TabView', () => {
  const children = {
    visualization: <div>Viz Content</div>,
    evaluation: <div>Eval Content</div>,
    deploy: <div>Deploy Content</div>
  };

  it('renders default tab (visualization)', () => {
    render(<TabView hasEvaluation={true} children={children} />);
    expect(screen.getByText('Viz Content')).toBeInTheDocument();
  });

  it('switches tabs', () => {
    render(<TabView hasEvaluation={true} children={children} />);

    fireEvent.click(screen.getByText('Deploy'));
    expect(screen.getByText('Deploy Content')).toBeInTheDocument();
    expect(screen.queryByText('Viz Content')).not.toBeInTheDocument();
  });

  it('evaluation tab disabled if hasEvaluation is false', () => {
    render(<TabView hasEvaluation={false} children={children} />);
    expect(screen.getByText('Evaluation')).toBeDisabled();
  });
});
