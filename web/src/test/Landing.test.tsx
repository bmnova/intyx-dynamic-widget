import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import Landing from '../pages/Landing';

function renderWithRouter() {
  return render(
    <MemoryRouter>
      <Landing />
    </MemoryRouter>
  );
}

describe('Landing', () => {
  it('renders hero heading', () => {
    renderWithRouter();
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
  });

  it('renders View Plans and Dashboard links', () => {
    renderWithRouter();
    // "View Plans →" appears in both hero and CTA sections
    const planLinks = screen.getAllByRole('link', { name: /view plans/i });
    expect(planLinks.length).toBeGreaterThanOrEqual(1);
    planLinks.forEach((link) => expect(link).toHaveAttribute('href', '/pricing'));
    // Dashboard link appears only in the hero
    expect(screen.getByRole('link', { name: 'Dashboard' })).toHaveAttribute('href', '/dashboard');
  });

  it('renders all 10 widget cards', () => {
    renderWithRouter();
    const cards = screen.getAllByRole('article');
    expect(cards.length).toBeGreaterThanOrEqual(10);
  });

  it('renders Features section', () => {
    renderWithRouter();
    expect(screen.getByRole('heading', { name: /how it works/i })).toBeInTheDocument();
  });

  it('renders Widget Catalog section', () => {
    renderWithRouter();
    expect(screen.getByRole('heading', { name: /widget catalog/i })).toBeInTheDocument();
  });

  it('renders Live Widget Preview section', () => {
    renderWithRouter();
    expect(screen.getByRole('heading', { name: /live widget preview/i })).toBeInTheDocument();
  });

  it('renders demo tab list', () => {
    renderWithRouter();
    expect(screen.getByRole('tablist', { name: /widget type selector/i })).toBeInTheDocument();
  });

  it('banner tab is selected by default', () => {
    renderWithRouter();
    const bannerTab = screen.getByRole('tab', { name: /banner/i });
    expect(bannerTab).toHaveAttribute('aria-selected', 'true');
  });

  it('switches demo preview when a tab is clicked', async () => {
    renderWithRouter();
    const promoTab = screen.getByRole('tab', { name: /promotional/i });
    await userEvent.click(promoTab);
    expect(promoTab).toHaveAttribute('aria-selected', 'true');
    // Banner tab should no longer be selected
    expect(screen.getByRole('tab', { name: /banner/i })).toHaveAttribute('aria-selected', 'false');
  });

  it('renders the demo tabpanel', () => {
    renderWithRouter();
    expect(screen.getByRole('tabpanel')).toBeInTheDocument();
  });

  it('renders Get Started CTA section', () => {
    renderWithRouter();
    expect(screen.getByRole('heading', { name: /get started/i })).toBeInTheDocument();
  });

  it('renders footer', () => {
    renderWithRouter();
    expect(screen.getByRole('contentinfo')).toBeInTheDocument();
  });

  it('renders code example figure', () => {
    renderWithRouter();
    expect(screen.getByRole('figure', { name: /code example/i })).toBeInTheDocument();
    expect(screen.getByText(/DynamicWidgetContainer/)).toBeInTheDocument();
  });
});
