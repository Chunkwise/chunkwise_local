import { render, screen, fireEvent } from '@testing-library/react';
import RDSConnectionDetails from '../components/RDSConnectionDetails';

describe('RDSConnectionDetails', () => {
  const mockDetails = {
    endpoint: "db.example.com",
    port: 5432,
    database: "vectordb",
    table_name: "vectors_123",
    secret_arn: "arn:aws:secretsmanager:...",
    db_instance_identifier: "db-inst-1",
    ok: true,
    stage: "rds-ready" as const
  };

  it('renders details correctly', () => {
    render(<RDSConnectionDetails details={mockDetails} />);

    expect(screen.getByText('RDS instance is online.')).toBeInTheDocument();
    expect(screen.getByText('postgres://db.example.com:5432/vectordb')).toBeInTheDocument();
    expect(screen.getByText('db.example.com')).toBeInTheDocument();
    expect(screen.getByText('vectors_123')).toBeInTheDocument();
  });

  it('copy buttons exist', () => {
    render(<RDSConnectionDetails details={mockDetails} />);
    expect(screen.getByText('Copy connection')).toBeInTheDocument();
    expect(screen.getByText('Copy')).toBeInTheDocument(); // secret arn copy
  });
});
