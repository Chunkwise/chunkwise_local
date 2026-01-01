import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChooseFile from '../components/ChooseFile';
import { uploadFile } from '../services/documents';
import { vi } from 'vitest';
import type { Workflow } from '../types';

vi.mock('../services/documents', () => ({
  uploadFile: vi.fn(),
}));

describe('ChooseFile', () => {
  const mockWorkflow: Workflow = {
    id: "1",
    title: "Test Workflow",
    created_at: "2023-01-01",
    stage: "setup",
    document_title: "test.txt",
    chunking_strategy: undefined,
    chunks_stats: undefined,
    visualization_html: undefined,
    evaluation_metrics: undefined,
    deploy_table_name: undefined,
  };

  const mockOnFileChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly', () => {
    render(
      <ChooseFile
        workflow={mockWorkflow}
        isLoadingFiles={false}
        availableFiles={['test.txt', 'other.txt']}
        onFileChange={mockOnFileChange}
      />
    );

    expect(screen.getByText('File')).toBeInTheDocument();
    expect(screen.getByRole('combobox')).toHaveValue('test.txt');
    expect(screen.getByText('Selected: test.txt')).toBeInTheDocument();
  });

  it('handles file selection', () => {
    render(
      <ChooseFile
        workflow={mockWorkflow}
        isLoadingFiles={false}
        availableFiles={['test.txt', 'other.txt']}
        onFileChange={mockOnFileChange}
      />
    );

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'other.txt' } });
    expect(mockOnFileChange).toHaveBeenCalledWith('other.txt');
  });

  it('handles remove selection', () => {
    render(
      <ChooseFile
        workflow={mockWorkflow}
        isLoadingFiles={false}
        availableFiles={['test.txt']}
        onFileChange={mockOnFileChange}
      />
    );

    fireEvent.click(screen.getByTitle('Remove selection'));
    expect(mockOnFileChange).toHaveBeenCalledWith(undefined);
  });

  it('uploads file triggers uploadFile service', async () => {
    render(
      <ChooseFile
        workflow={mockWorkflow}
        isLoadingFiles={false}
        availableFiles={[]}
        onFileChange={mockOnFileChange}
      />
    );

    const file = new File(['content'], 'newfile.txt', { type: 'text/plain' });
    // Mock text() method which is missing in jsdom
    file.text = vi.fn().mockResolvedValue('content');

    // Actually we can't easily select the hidden input via label text directly if it's not properly associated or hidden.
    // The input is hidden: style={{ display: "none" }}
    // The select's onChange triggers the click on input.

    // Let's find the input directly by id
    const fileInput = document.getElementById('file-upload-input');

    if (fileInput) {
        // Need to wait for the async file reading in the component
        Object.defineProperty(fileInput, 'files', {
            value: [file]
        });
        fireEvent.change(fileInput);
    }

    // Wait for the uploadFile to be called
    await waitFor(() => {
        expect(uploadFile).toHaveBeenCalledTimes(1);
    });

    expect(uploadFile).toHaveBeenCalledWith({
        document_title: 'newfile',
        document_content: 'content'
    });
    expect(mockOnFileChange).toHaveBeenCalledWith('newfile');
  });
});
