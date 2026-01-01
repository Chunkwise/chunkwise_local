import { render, screen, fireEvent } from '@testing-library/react';
import ChunkerForm from '../components/ChunkerForm';
import { vi } from 'vitest';
import type { Workflow, Chunker } from '../types';

describe('ChunkerForm', () => {
  const mockWorkflow: Workflow = {
    id: "1",
    title: "Test Workflow",
    created_at: "2023-01-01",
    stage: "setup",
    chunking_strategy: undefined
  };

  const mockChunkers: Chunker[] = [
    {
      name: "Provider Type",
      description: "Description",
      chunk_size: { default: 100, min: 10, max: 1000, type: "int" }
    }
  ];

  const mockOnChunkerChange = vi.fn();
  const mockOnConfigChange = vi.fn();

  it('renders chunker selection', () => {
    render(
      <ChunkerForm
        workflow={mockWorkflow}
        chunkers={mockChunkers}
        selectedChunkerConfig={undefined}
        onChunkerChange={mockOnChunkerChange}
        onConfigChange={mockOnConfigChange}
      />
    );

    expect(screen.getByText('Chunker & configuration')).toBeInTheDocument();
    expect(screen.getByRole('combobox')).toBeInTheDocument();
    expect(screen.getByText('Choose a chunker to preview its config options.')).toBeInTheDocument();
  });

  it('renders config sliders when chunker selected', () => {
    const strategy = { provider: "Provider", chunker_type: "Type", chunk_size: 100 };
    render(
      <ChunkerForm
        workflow={{ ...mockWorkflow, chunking_strategy: strategy }}
        chunkers={mockChunkers}
        selectedChunkerConfig={mockChunkers[0]}
        onChunkerChange={mockOnChunkerChange}
        onConfigChange={mockOnConfigChange}
      />
    );

    expect(screen.getByText('Description')).toBeInTheDocument();
    // Should see ConfigSlider for chunk_size
    expect(screen.getByText('chunk_size')).toBeInTheDocument();
  });

  it('calls onChunkerChange when selecting a chunker', () => {
    render(
      <ChunkerForm
        workflow={mockWorkflow}
        chunkers={mockChunkers}
        selectedChunkerConfig={undefined}
        onChunkerChange={mockOnChunkerChange}
        onConfigChange={mockOnConfigChange}
      />
    );

    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'Provider Type' } });
    expect(mockOnChunkerChange).toHaveBeenCalledWith('Provider Type');
  });
});
