import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ComplianceGauge } from '../ComplianceGauge';

describe('ComplianceGauge', () => {
  const mockViolations = [
    { id: '1', severity: 'critical' as const, message: 'Logo margin too small' },
    { id: '2', severity: 'warning' as const, message: 'Font weight incorrect' },
    { id: '3', severity: 'info' as const, message: 'Consider using brand colors' },
  ];

  it('renders with correct score', () => {
    render(
      <ComplianceGauge
        score={88}
        violations={[]}
        onViolationClick={vi.fn()}
      />
    );

    expect(screen.getByText('88')).toBeInTheDocument();
    expect(screen.getByText('SCORE')).toBeInTheDocument();
  });

  it('renders with data-testid', () => {
    const { container } = render(
      <ComplianceGauge
        score={75}
        violations={[]}
        onViolationClick={vi.fn()}
      />
    );

    expect(container.querySelector('[data-testid="compliance-gauge"]')).toBeInTheDocument();
  });

  it('displays "No violations detected" when violations array is empty', () => {
    render(
      <ComplianceGauge
        score={95}
        violations={[]}
        onViolationClick={vi.fn()}
      />
    );

    expect(screen.getByText('No violations detected')).toBeInTheDocument();
  });

  it('renders all violations in the list', () => {
    render(
      <ComplianceGauge
        score={70}
        violations={mockViolations}
        onViolationClick={vi.fn()}
      />
    );

    expect(screen.getByText('Logo margin too small')).toBeInTheDocument();
    expect(screen.getByText('Font weight incorrect')).toBeInTheDocument();
    expect(screen.getByText('Consider using brand colors')).toBeInTheDocument();
  });

  it('displays violation count summary', () => {
    render(
      <ComplianceGauge
        score={70}
        violations={mockViolations}
        onViolationClick={vi.fn()}
      />
    );

    expect(screen.getByText('1 Critical, 1 Warning, 1 Info')).toBeInTheDocument();
  });

  it('clamps score to 0-100 range', () => {
    const { rerender } = render(
      <ComplianceGauge
        score={150}
        violations={[]}
        onViolationClick={vi.fn()}
      />
    );

    expect(screen.getByText('100')).toBeInTheDocument();

    rerender(
      <ComplianceGauge
        score={-50}
        violations={[]}
        onViolationClick={vi.fn()}
      />
    );

    expect(screen.getByText('0')).toBeInTheDocument();
  });
});
