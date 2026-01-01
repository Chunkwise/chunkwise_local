import { render, screen, fireEvent } from '@testing-library/react';
import ConfigSlider from '../components/ConfigSlider';
import { vi } from 'vitest';
import type { Workflow, Chunker, ConfigOption } from '../types';

describe('ConfigSlider', () => {
  const mockWorkflow: Workflow = {
    id: "1",
    title: "Test",
    created_at: "",
    stage: "setup",
    chunking_strategy: {
        provider: "test",
        chunker_type: "fixed",
        chunk_size: 500,
        chunk_overlap: 50
    }
  };

  const mockChunker: Chunker = {
      name: "Test Fixed",
      description: "desc",
      chunk_size: { default: 500, min: 100, max: 1000, type: "int" },
      chunk_overlap: { default: 50, min: 0, max: 200, type: "int" }
  };

  const mockOnConfigChange = vi.fn();

  it('renders correctly with value', () => {
    const option: ConfigOption = { default: 500, min: 100, max: 1000, type: "int" };

    render(
      <ConfigSlider
        optionKey="chunk_size"
        configOption={option}
        chunkerConfig={mockChunker}
        workflow={mockWorkflow}
        onConfigChange={mockOnConfigChange}
      />
    );

    expect(screen.getByText('chunk_size')).toBeInTheDocument();
    expect(screen.getByText('500')).toBeInTheDocument(); // slider value display
    expect(screen.getByRole('slider')).toHaveValue('500');
  });

  it('calls onConfigChange when slider moves', () => {
    const option: ConfigOption = { default: 500, min: 100, max: 1000, type: "int" };

    render(
      <ConfigSlider
        optionKey="chunk_size"
        configOption={option}
        chunkerConfig={mockChunker}
        workflow={mockWorkflow}
        onConfigChange={mockOnConfigChange}
      />
    );

    fireEvent.change(screen.getByRole('slider'), { target: { value: '600' } });
    expect(mockOnConfigChange).toHaveBeenCalledWith('chunk_size', 600);
  });

  it('respects dynamic bounds (overlap vs chunk_size)', () => {
    // chunk_overlap max should be chunk_size - 1
    // chunk_size is 500. So max overlap should be 499 (or clamped by config max)
    const option: ConfigOption = { default: 50, min: 0, max: 1000, type: "int" };

    render(
      <ConfigSlider
        optionKey="chunk_overlap"
        configOption={option}
        chunkerConfig={mockChunker}
        workflow={mockWorkflow}
        onConfigChange={mockOnConfigChange}
      />
    );

    const slider = screen.getByRole('slider');
    expect(slider).toHaveAttribute('max', '499');
  });
});
