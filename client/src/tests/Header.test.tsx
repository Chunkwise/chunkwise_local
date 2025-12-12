import { render, screen } from '@testing-library/react';
import Header from '../components/Header';

describe('Header', () => {
  it('renders title and subtitle', () => {
    render(<Header />);
    expect(screen.getByText('Chunkwise - Chunker comparison')).toBeInTheDocument();
    expect(screen.getByText('Compare chunking strategies via visualization and evaluation.')).toBeInTheDocument();
  });
});
