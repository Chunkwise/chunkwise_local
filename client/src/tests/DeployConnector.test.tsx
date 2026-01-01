import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import DeployConnector from '../components/DeployConnector';
import { vi } from 'vitest';
import type { Workflow } from '../types';
import * as deployService from '../services/deploy';

vi.mock('../services/deploy', async () => {
    const actual = await vi.importActual('../services/deploy');
    return {
        ...actual,
        deployWorkflow: vi.fn(),
    };
});

describe('DeployConnector', () => {
  const mockWorkflow: Workflow = {
    id: "1",
    title: "Test",
    created_at: "",
    stage: "setup",
    chunking_strategy: { provider: "a", chunker_type: "b" }
  };

  const mockWorkflowNoStrategy: Workflow = {
    id: "1",
    title: "Test",
    created_at: "",
    stage: "setup",
    chunking_strategy: undefined
  };

  it('renders correctly', () => {
    render(<DeployConnector workflow={mockWorkflow} />);
    expect(screen.getByText('Deploy')).toBeInTheDocument();
    expect(screen.getByText('Connect to Amazon S3')).toBeEnabled();
  });

  it('disabled if no chunking strategy', () => {
    render(<DeployConnector workflow={mockWorkflowNoStrategy} />);
    expect(screen.getByText('Connect to Amazon S3')).toBeDisabled();
    expect(screen.getByText('Configure a chunker before setting up deployment.')).toBeInTheDocument();
  });

  it('shows form on click', () => {
    render(<DeployConnector workflow={mockWorkflow} />);
    fireEvent.click(screen.getByText('Connect to Amazon S3'));
    expect(screen.getByLabelText('Access Key')).toBeInTheDocument();
    expect(screen.getByLabelText('Secret Key')).toBeInTheDocument();
  });

  it('calls deployWorkflow on submit', async () => {
    render(<DeployConnector workflow={mockWorkflow} />);
    fireEvent.click(screen.getByText('Connect to Amazon S3'));

    fireEvent.change(screen.getByLabelText('Access Key'), { target: { value: 'ak' } });
    fireEvent.change(screen.getByLabelText('Secret Key'), { target: { value: 'sk' } });
    fireEvent.change(screen.getByLabelText('Bucket Name'), { target: { value: 'bucket' } });

    fireEvent.click(screen.getByText('Connect', { selector: 'button[type="submit"]' }));

    expect(deployService.deployWorkflow).toHaveBeenCalled();
  });
});
