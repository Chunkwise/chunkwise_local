import { render, screen } from '@testing-library/react';
import WorkflowComparison from '../components/WorkflowComparison';
import type { Workflow, Chunker } from '../types';

describe('WorkflowComparison', () => {
  const chunkers: Chunker[] = [
    { name: "Provider Type", description: "desc", chunk_size: { default: 100, min: 1, max: 2, type: 'int' } }
  ];

  const w1: Workflow = {
    id: "1",
    title: "W1",
    created_at: "",
    stage: "setup",
    chunking_strategy: { provider: "Provider", chunker_type: "Type", chunk_size: 100 },
    chunks_stats: { total_chunks: 10, avg_chars: 50, largest_chunk_chars: 100, smallest_chunk_chars: 10, largest_text: "", smallest_text: "" },
    evaluation_metrics: { precision_mean: 0.9, recall_mean: 0.8, iou_mean: 0.7, precision_omega_mean: 0.85, metrics_by_query: [] }
  };

  const w2: Workflow = {
    id: "2",
    title: "W2",
    created_at: "",
    stage: "setup",
    chunking_strategy: undefined
  };

  it('renders placeholder when less than 2 workflows', () => {
    render(<WorkflowComparison workflows={[w1]} chunkers={chunkers} />);
    expect(screen.getByText('Select at least 2 workflows to compare')).toBeInTheDocument();
  });

  it('renders comparison for 2 workflows', () => {
    render(<WorkflowComparison workflows={[w1, w2]} chunkers={chunkers} />);

    expect(screen.getByText('W1')).toBeInTheDocument();
    expect(screen.getByText('W2')).toBeInTheDocument();

    // Check W1 stats
    expect(screen.getByText('Total chunks')).toBeInTheDocument();
    expect(screen.getAllByText('10')[0]).toBeInTheDocument(); // total chunks value

    // Check W1 evaluation
    expect(screen.getByText('Precision mean')).toBeInTheDocument();
    expect(screen.getByText('0.900')).toBeInTheDocument();

    // Check W2 empty state
    expect(screen.getByText('Not configured')).toBeInTheDocument();
    expect(screen.getByText('No stats available')).toBeInTheDocument();
    expect(screen.getByText('Not evaluated')).toBeInTheDocument();
  });
});
