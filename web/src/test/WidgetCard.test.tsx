import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import WidgetCard from '../components/WidgetCard';

describe('WidgetCard', () => {
  const defaultProps = {
    icon: '☁️',
    title: 'Contextual',
    description: 'Contextual info card based on weather and AI context.',
  };

  it('renders title and description', () => {
    render(<WidgetCard {...defaultProps} />);
    expect(screen.getByText('Contextual')).toBeInTheDocument();
    expect(screen.getByText('Contextual info card based on weather and AI context.')).toBeInTheDocument();
  });

  it('renders icon', () => {
    render(<WidgetCard {...defaultProps} />);
    expect(screen.getByText('☁️')).toBeInTheDocument();
  });

  it('renders tag when provided', () => {
    render(<WidgetCard {...defaultProps} tag="AI Driven" />);
    expect(screen.getByText('AI Driven')).toBeInTheDocument();
  });

  it('does not render tag when not provided', () => {
    render(<WidgetCard {...defaultProps} />);
    // No tag element should exist
    const article = screen.getByRole('article');
    expect(article).not.toHaveTextContent('AI Driven');
  });

  it('has correct aria-label on article', () => {
    render(<WidgetCard {...defaultProps} title="Hero Image" />);
    expect(screen.getByRole('article', { name: 'Hero Image' })).toBeInTheDocument();
  });
});
