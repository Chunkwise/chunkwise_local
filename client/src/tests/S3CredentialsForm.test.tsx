import { render, screen, fireEvent } from '@testing-library/react';
import S3CredentialsForm from '../components/S3CredentialsForm';
import { vi } from 'vitest';

describe('S3CredentialsForm', () => {
  const mockSubmit = vi.fn();
  const mockCancel = vi.fn();

  it('renders form fields', () => {
    render(
      <S3CredentialsForm
        onSubmit={mockSubmit}
        onCancel={mockCancel}
        isSubmitting={false}
      />
    );

    expect(screen.getByLabelText('Access Key')).toBeInTheDocument();
    expect(screen.getByLabelText('Secret Key')).toBeInTheDocument();
    expect(screen.getByLabelText('Bucket Name')).toBeInTheDocument();
  });

  it('submits data', () => {
    render(
      <S3CredentialsForm
        onSubmit={mockSubmit}
        onCancel={mockCancel}
        isSubmitting={false}
      />
    );

    fireEvent.change(screen.getByLabelText('Access Key'), { target: { value: 'ak' } });
    fireEvent.change(screen.getByLabelText('Secret Key'), { target: { value: 'sk' } });
    fireEvent.change(screen.getByLabelText('Bucket Name'), { target: { value: 'bk' } });

    fireEvent.click(screen.getByText('Connect'));

    expect(mockSubmit).toHaveBeenCalledWith({
      access_key: 'ak',
      secret_key: 'sk',
      bucket_name: 'bk'
    });
  });

  it('cancels', () => {
    render(
      <S3CredentialsForm
        onSubmit={mockSubmit}
        onCancel={mockCancel}
        isSubmitting={false}
      />
    );

    fireEvent.click(screen.getByText('Cancel'));
    expect(mockCancel).toHaveBeenCalled();
  });
});
