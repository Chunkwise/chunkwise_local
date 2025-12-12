import { render, screen } from '@testing-library/react';
import ChunkStats from '../components/ChunkStats';

describe('ChunkStats', () => {
  const mockStats = {
    total_chunks: 10,
    largest_chunk_chars: 500,
    largest_text: "large",
    smallest_chunk_chars: 50,
    smallest_text: "small",
    avg_chars: 275.5
  };

  it('renders stats correctly', () => {
    render(<ChunkStats stats={mockStats} />);

    expect(screen.getByText('Total Chunks')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();

    expect(screen.getByText('Average Characters')).toBeInTheDocument();
    expect(screen.getByText('276')).toBeInTheDocument(); // Rounded 275.5

    expect(screen.getByText('Largest Chunk')).toBeInTheDocument();
    expect(screen.getByText('500 chars')).toBeInTheDocument();

    expect(screen.getByText('Smallest Chunk')).toBeInTheDocument();
    expect(screen.getByText('50 chars')).toBeInTheDocument();
  });
});
