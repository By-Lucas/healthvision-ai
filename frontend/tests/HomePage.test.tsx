import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { HomePage } from '@/features/home/pages/HomePage';

function renderHome() {
  return render(
    <MemoryRouter>
      <HomePage />
    </MemoryRouter>,
  );
}

describe('HomePage', () => {
  it('renders the hero heading', () => {
    renderHome();
    expect(
      screen.getByRole('heading', { name: /chest x-ray analysis/i }),
    ).toBeInTheDocument();
  });

  it('shows the educational disclaimer', () => {
    renderHome();
    expect(
      screen.getByText(/not a medical diagnosis tool/i),
    ).toBeInTheDocument();
  });

  it('links to the upload page', () => {
    renderHome();
    const link = screen.getByRole('link', { name: /upload an exam/i });
    expect(link).toHaveAttribute('href', '/upload');
  });
});
