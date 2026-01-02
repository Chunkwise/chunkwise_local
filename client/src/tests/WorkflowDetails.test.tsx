import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import WorkflowDetails from '../components/WorkflowDetails';
import { vi } from 'vitest';
import type { Workflow } from '../types';

vi.mock('../services/visualization', () => ({
  getVisualization: vi.fn().mockResolvedValue({ stats: {}, html: '<div>viz</div>' })
}));

vi.mock('../services/evaluation', () => ({
  getEvaluationMetrics: vi.fn().mockResolvedValue({ precision_mean: 1 })
}));

describe('WorkflowDetails', () => {
  const mockWorkflow: Workflow = {
    id: "1",
    title: "Test",
    created_at: "",
    stage: "setup",
    document_title: "doc.txt",
    chunking_strategy: { provider: "P", chunker_type: "T" }
  };

  const chunkers = [{ name: "P T", description: "desc" }];

  const mockUpdate = vi.fn();
  const mockPatch = vi.fn();

  it('renders correctly', () => {
    render(
      <WorkflowDetails
        chunkers={chunkers}
        isLoadingFiles={false}
        availableFiles={['doc.txt']}
        workflow={mockWorkflow}
        onUpdateWorkflow={mockUpdate}
        onPatchWorkflow={mockPatch}
      />
    );

    expect(screen.getByText('File')).toBeInTheDocument();
    expect(screen.getByText('Chunker & configuration')).toBeInTheDocument();
  });

  it('shows visualization tab', () => {
    render(
      <WorkflowDetails
        chunkers={chunkers}
        isLoadingFiles={false}
        availableFiles={['doc.txt']}
        workflow={{...mockWorkflow, chunks_stats: {} as any, visualization_html: 'html'}}
        onUpdateWorkflow={mockUpdate}
        onPatchWorkflow={mockPatch}
      />
    );
    // There are multiple "Visualization" texts (tab button and section title)
    // We check that the section title is present, indicating the tab content is rendered
    expect(screen.getByRole('heading', { name: 'Visualization' })).toBeInTheDocument();
  });

  it('runs evaluation', async () => {
    render(
      <WorkflowDetails
        chunkers={chunkers}
        isLoadingFiles={false}
        availableFiles={['doc.txt']}
        workflow={mockWorkflow}
        onUpdateWorkflow={mockUpdate}
        onPatchWorkflow={mockPatch}
      />
    );

    const evalBtn = screen.getByText('⚡ Run Evaluation');
    fireEvent.click(evalBtn);

    expect(screen.getByText('Running Evaluation...')).toBeInTheDocument();
    await waitFor(() => {
        expect(mockPatch).toHaveBeenCalledWith({ evaluation_metrics: { precision_mean: 1 } });
    });
  });
});
