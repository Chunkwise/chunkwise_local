import { render, screen } from '@testing-library/react';
import EvaluationMetrics from '../components/EvaluationMetrics';

describe('EvaluationMetrics', () => {
  const mockMetrics = {
    precision_mean: 0.9,
    recall_mean: 0.85,
    iou_mean: 0.8,
    precision_omega_mean: 0.88,
    metrics_by_query: []
  };

  it('renders metrics correctly', () => {
    render(<EvaluationMetrics metrics={mockMetrics} />);

    expect(screen.getByText('Evaluation Results')).toBeInTheDocument();

    // Check values rendered as percentages
    expect(screen.getByText('90.0%')).toBeInTheDocument(); // precision
    expect(screen.getByText('85.0%')).toBeInTheDocument(); // recall
    expect(screen.getByText('80.0%')).toBeInTheDocument(); // iou
    expect(screen.getByText('88.0%')).toBeInTheDocument(); // precision omega

    // Check rating
    expect(screen.getByText('Excellent')).toBeInTheDocument();
  });
});
