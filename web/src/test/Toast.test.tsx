import { render, screen, act, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import Toast from '../components/Toast';

describe('Toast', () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders message', () => {
    render(<Toast type="error" message="Something went wrong" onClose={vi.fn()} />);
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('has role="alert" for accessibility', () => {
    render(<Toast type="error" message="Error!" onClose={vi.fn()} />);
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('calls onClose when dismiss button is clicked', () => {
    const onClose = vi.fn();
    render(<Toast type="error" message="Error!" onClose={onClose} />);
    fireEvent.click(screen.getByRole('button', { name: /dismiss/i }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose automatically after duration', () => {
    vi.useFakeTimers();
    const onClose = vi.fn();
    render(<Toast type="info" message="Info" onClose={onClose} duration={3000} />);
    expect(onClose).not.toHaveBeenCalled();
    act(() => { vi.advanceTimersByTime(3000); });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('does not call onClose before duration elapses', () => {
    vi.useFakeTimers();
    const onClose = vi.fn();
    render(<Toast type="success" message="Done" onClose={onClose} duration={4000} />);
    act(() => { vi.advanceTimersByTime(3999); });
    expect(onClose).not.toHaveBeenCalled();
  });

  it('renders success type', () => {
    render(<Toast type="success" message="Saved!" onClose={vi.fn()} />);
    expect(screen.getByText('Saved!')).toBeInTheDocument();
  });

  it('renders info type', () => {
    render(<Toast type="info" message="Note this." onClose={vi.fn()} />);
    expect(screen.getByText('Note this.')).toBeInTheDocument();
  });
});
