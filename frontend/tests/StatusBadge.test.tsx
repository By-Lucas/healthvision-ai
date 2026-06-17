import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ClassBadge, StatusBadge } from '@/shared/components/StatusBadge';

describe('badges', () => {
  it('renders a status badge', () => {
    render(<StatusBadge status="COMPLETED" />);
    expect(screen.getByText('COMPLETED')).toBeInTheDocument();
  });

  it('renders a dash when class is null', () => {
    render(<ClassBadge value={null} />);
    expect(screen.getByText('—')).toBeInTheDocument();
  });

  it('renders the predicted class', () => {
    render(<ClassBadge value="PNEUMONIA" />);
    expect(screen.getByText('PNEUMONIA')).toBeInTheDocument();
  });
});
