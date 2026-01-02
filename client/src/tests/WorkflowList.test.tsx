import { render, screen, fireEvent } from '@testing-library/react';
import WorkflowList from '../components/WorkflowList';
import type { Workflow } from '../types';
import { vi } from 'vitest';

describe('WorkflowList', () => {
  const w1: Workflow = { id: "1", title: "W1", created_at: "2023-01-01", stage: "setup" };
  const w2: Workflow = { id: "2", title: "W2", created_at: "2023-01-02", stage: "setup" };
  const workflows = [w1, w2];

  const mockCreate = vi.fn();
  const mockSelect = vi.fn();
  const mockDelete = vi.fn();
  const mockEnterComp = vi.fn();
  const mockExitComp = vi.fn();
  const mockToggleComp = vi.fn();

  it('renders list', () => {
    render(
      <WorkflowList
        workflows={workflows}
        isComparing={false}
        comparedWorkflowIds={[]}
        onCreateWorkflow={mockCreate}
        onSelectWorkflow={mockSelect}
        onDeleteWorkflow={mockDelete}
        onEnterComparison={mockEnterComp}
        onExitComparison={mockExitComp}
        onToggleWorkflowComparison={mockToggleComp}
      />
    );

    expect(screen.getByText('Workflows')).toBeInTheDocument();
    expect(screen.getByText('W1')).toBeInTheDocument();
    expect(screen.getByText('W2')).toBeInTheDocument();
  });

  it('selects workflow', () => {
    render(
      <WorkflowList
        workflows={workflows}
        isComparing={false}
        comparedWorkflowIds={[]}
        onCreateWorkflow={mockCreate}
        onSelectWorkflow={mockSelect}
        onDeleteWorkflow={mockDelete}
        onEnterComparison={mockEnterComp}
        onExitComparison={mockExitComp}
        onToggleWorkflowComparison={mockToggleComp}
      />
    );

    fireEvent.click(screen.getByText('W1'));
    expect(mockSelect).toHaveBeenCalledWith('1');
  });

  it('creates workflow', () => {
    render(
      <WorkflowList
        workflows={workflows}
        isComparing={false}
        comparedWorkflowIds={[]}
        onCreateWorkflow={mockCreate}
        onSelectWorkflow={mockSelect}
        onDeleteWorkflow={mockDelete}
        onEnterComparison={mockEnterComp}
        onExitComparison={mockExitComp}
        onToggleWorkflowComparison={mockToggleComp}
      />
    );

    fireEvent.click(screen.getByText('+ New'));
    fireEvent.change(screen.getByPlaceholderText('Workflow name'), { target: { value: 'NewWF' } });
    fireEvent.click(screen.getByText('Create'));

    expect(mockCreate).toHaveBeenCalledWith('NewWF');
  });

  it('comparison mode', () => {
    render(
      <WorkflowList
        workflows={workflows}
        isComparing={true}
        comparedWorkflowIds={['1']}
        onCreateWorkflow={mockCreate}
        onSelectWorkflow={mockSelect}
        onDeleteWorkflow={mockDelete}
        onEnterComparison={mockEnterComp}
        onExitComparison={mockExitComp}
        onToggleWorkflowComparison={mockToggleComp}
      />
    );

    expect(screen.getByText('Select up to 3 (1/3)')).toBeInTheDocument();
    fireEvent.click(screen.getByText('W2'));
    expect(mockToggleComp).toHaveBeenCalledWith('2');
  });
});
