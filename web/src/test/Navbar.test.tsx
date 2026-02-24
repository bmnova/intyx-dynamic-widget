import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import Navbar from '../components/Navbar';

function renderWithRouter(path = '/') {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Navbar />
    </MemoryRouter>
  );
}

describe('Navbar', () => {
  it('renders logo link', () => {
    renderWithRouter();
    expect(screen.getByRole('link', { name: /intyx home/i })).toBeInTheDocument();
  });

  it('renders all nav links', () => {
    renderWithRouter();
    expect(screen.getByRole('link', { name: 'Home' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Pricing' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Dashboard' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Studio' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Agent Tasks' })).toBeInTheDocument();
  });

  it('marks active link with aria-current="page"', () => {
    renderWithRouter('/pricing');
    const pricingLink = screen.getByRole('link', { name: 'Pricing' });
    expect(pricingLink).toHaveAttribute('aria-current', 'page');
  });

  it('does not mark non-active links with aria-current', () => {
    renderWithRouter('/pricing');
    const homeLink = screen.getByRole('link', { name: 'Home' });
    expect(homeLink).not.toHaveAttribute('aria-current', 'page');
  });

  it('has main navigation landmark', () => {
    renderWithRouter();
    expect(screen.getByRole('navigation', { name: /main navigation/i })).toBeInTheDocument();
  });
});
