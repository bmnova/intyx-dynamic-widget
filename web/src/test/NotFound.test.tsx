import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import NotFound from '../pages/NotFound';

function renderWithRouter() {
  return render(
    <MemoryRouter>
      <NotFound />
    </MemoryRouter>
  );
}

describe('NotFound', () => {
  it('renders 404 heading', () => {
    renderWithRouter();
    expect(screen.getByRole('heading', { name: 'Page Not Found' })).toBeInTheDocument();
  });

  it('displays 404 number', () => {
    renderWithRouter();
    expect(screen.getByText('404')).toBeInTheDocument();
  });

  it('renders back to home link', () => {
    renderWithRouter();
    const link = screen.getByRole('link', { name: /go back to intyx home/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', '/');
  });

  it('renders explanation text', () => {
    renderWithRouter();
    expect(screen.getByText(/doesn't exist or has been moved/i)).toBeInTheDocument();
  });

  it('has main landmark with label', () => {
    renderWithRouter();
    expect(screen.getByRole('main', { name: /page not found/i })).toBeInTheDocument();
  });
});
