import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import Pricing from '../pages/Pricing';

// Mock react-router-dom's useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return { ...actual, useNavigate: () => mockNavigate };
});

// Mock lib/paddle so we don't load external scripts
vi.mock('../lib/paddle', () => ({
  setPaddleConfig: vi.fn(),
  loadPaddleScript: vi.fn(() => Promise.resolve()),
  initPaddle: vi.fn(() => Promise.resolve()),
  openCheckout: vi.fn(),
}));

// Mock global fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

function renderWithRouter() {
  return render(
    <MemoryRouter>
      <Pricing />
    </MemoryRouter>
  );
}

describe('Pricing', () => {
  beforeEach(() => {
    mockFetch.mockReset();
    mockNavigate.mockReset();
    localStorage.clear();
  });

  it('renders page heading', () => {
    renderWithRouter();
    expect(screen.getByRole('heading', { name: /simple pricing/i })).toBeInTheDocument();
  });

  it('renders all three plans', () => {
    renderWithRouter();
    expect(screen.getByRole('article', { name: /starter plan/i })).toBeInTheDocument();
    expect(screen.getByRole('article', { name: /pro plan/i })).toBeInTheDocument();
    expect(screen.getByRole('article', { name: /enterprise plan/i })).toBeInTheDocument();
  });

  it('renders Popular badge on Pro plan', () => {
    renderWithRouter();
    expect(screen.getByText('Popular')).toBeInTheDocument();
  });

  it('renders plan prices', () => {
    renderWithRouter();
    expect(screen.getByText('Free')).toBeInTheDocument();
    expect(screen.getByText('$49')).toBeInTheDocument();
    expect(screen.getByText('$199')).toBeInTheDocument();
  });

  it('renders CTA buttons for each plan', () => {
    renderWithRouter();
    expect(screen.getByRole('button', { name: /start free — starter plan/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /choose pro — pro plan/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /contact us — enterprise plan/i })).toBeInTheDocument();
  });

  it('renders feature lists', () => {
    renderWithRouter();
    expect(screen.getByRole('list', { name: /starter features/i })).toBeInTheDocument();
    expect(screen.getByRole('list', { name: /pro features/i })).toBeInTheDocument();
    expect(screen.getByRole('list', { name: /enterprise features/i })).toBeInTheDocument();
  });

  it('clicking Start Free creates license and navigates to dashboard', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ api_key: 'test-key-123' }),
    });

    renderWithRouter();
    await userEvent.click(screen.getByRole('button', { name: /start free/i }));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/licenses'),
        expect.objectContaining({ method: 'POST' })
      );
      expect(localStorage.getItem('intyx_api_key')).toBe('test-key-123');
      expect(localStorage.getItem('intyx_plan')).toBe('starter');
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('shows error toast when license creation fails', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'Server error' }),
    });

    renderWithRouter();
    await userEvent.click(screen.getByRole('button', { name: /start free/i }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText('Server error')).toBeInTheDocument();
    });
  });

  it('disables all buttons while a plan is loading', async () => {
    // Never-resolving fetch to keep loading state
    mockFetch.mockImplementation(() => new Promise(() => {}));

    renderWithRouter();
    const starterBtn = screen.getByRole('button', { name: /start free/i });
    await userEvent.click(starterBtn);

    await waitFor(() => {
      expect(starterBtn).toBeDisabled();
      expect(screen.getByRole('button', { name: /choose pro/i })).toBeDisabled();
    });
  });
});
