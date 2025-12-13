import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Canvas } from '../Canvas';

describe('Canvas', () => {
  const mockVersions = [
    {
      attempt_id: 1,
      image_url: 'https://example.com/image1.png',
      thumb_url: 'https://example.com/thumb1.png',
      score: 85,
      timestamp: '2024-01-01T10:00:00Z',
      prompt: 'Test prompt 1',
    },
    {
      attempt_id: 2,
      image_url: 'https://example.com/image2.png',
      thumb_url: 'https://example.com/thumb2.png',
      score: 92,
      timestamp: '2024-01-01T11:00:00Z',
      prompt: 'Test prompt 2',
    },
  ];

  const mockViolations = [
    {
      id: 'v1',
      severity: 'critical' as const,
      message: 'Logo too small',
      bounding_box: [10, 20, 30, 40] as [number, number, number, number],
    },
    {
      id: 'v2',
      severity: 'warning' as const,
      message: 'Color mismatch',
      bounding_box: [50, 60, 20, 30] as [number, number, number, number],
    },
  ];

  it('renders skeleton loader when status is generating', () => {
    render(
      <Canvas
        violations={[]}
        versions={[]}
        currentVersion={0}
        complianceScore={0}
        status="generating"
        highlightedViolationId={null}
        onVersionChange={vi.fn()}
        onAcceptCorrection={vi.fn()}
      />
    );

    expect(screen.getByTestId('generating-state')).toBeTruthy();
  });

  it('renders auditing overlay when status is auditing', () => {
    render(
      <Canvas
        imageUrl="https://example.com/image.png"
        violations={[]}
        versions={[]}
        currentVersion={0}
        complianceScore={0}
        status="auditing"
        highlightedViolationId={null}
        onVersionChange={vi.fn()}
        onAcceptCorrection={vi.fn()}
      />
    );

    expect(screen.getByTestId('auditing-overlay')).toBeTruthy();
    expect(screen.getByText('Scanning Compliance...')).toBeTruthy();
  });

  it('renders image with bounding boxes when status is complete', () => {
    render(
      <Canvas
        imageUrl="https://example.com/image.png"
        violations={mockViolations}
        versions={[]}
        currentVersion={0}
        complianceScore={85}
        status="complete"
        highlightedViolationId={null}
        onVersionChange={vi.fn()}
        onAcceptCorrection={vi.fn()}
      />
    );

    expect(screen.getByTestId('canvas-image')).toBeTruthy();
    const boundingBoxes = screen.getAllByTestId('bounding-box');
    expect(boundingBoxes.length).toBe(2);
  });

  it('renders version scrubber when versions are provided', () => {
    render(
      <Canvas
        imageUrl="https://example.com/image.png"
        violations={[]}
        versions={mockVersions}
        currentVersion={0}
        complianceScore={85}
        status="complete"
        highlightedViolationId={null}
        onVersionChange={vi.fn()}
        onAcceptCorrection={vi.fn()}
      />
    );

    expect(screen.getByTestId('version-scrubber')).toBeTruthy();
    const thumbnails = screen.getAllByTestId('version-thumbnail');
    expect(thumbnails.length).toBe(2);
  });

  it('renders download button when score is >= 95%', () => {
    render(
      <Canvas
        imageUrl="https://example.com/image.png"
        violations={[]}
        versions={[]}
        currentVersion={0}
        complianceScore={96}
        status="complete"
        highlightedViolationId={null}
        onVersionChange={vi.fn()}
        onAcceptCorrection={vi.fn()}
      />
    );

    expect(screen.getByTestId('download-button')).toBeTruthy();
    expect(screen.getByText('Download')).toBeTruthy();
  });

  it('renders ship it button when score is 70-95%', () => {
    render(
      <Canvas
        imageUrl="https://example.com/image.png"
        violations={[]}
        versions={[]}
        currentVersion={0}
        complianceScore={85}
        status="complete"
        highlightedViolationId={null}
        onVersionChange={vi.fn()}
        onAcceptCorrection={vi.fn()}
      />
    );

    expect(screen.getByTestId('ship-it-button')).toBeTruthy();
    expect(screen.getByText('Ship It')).toBeTruthy();
  });

  it('does not render action button when score is < 70%', () => {
    render(
      <Canvas
        imageUrl="https://example.com/image.png"
        violations={[]}
        versions={[]}
        currentVersion={0}
        complianceScore={65}
        status="complete"
        highlightedViolationId={null}
        onVersionChange={vi.fn()}
        onAcceptCorrection={vi.fn()}
      />
    );

    expect(screen.queryByTestId('action-button-container')).toBeFalsy();
  });

  it('calls onVersionChange when version thumbnail is clicked', () => {
    const onVersionChange = vi.fn();
    render(
      <Canvas
        imageUrl="https://example.com/image.png"
        violations={[]}
        versions={mockVersions}
        currentVersion={0}
        complianceScore={85}
        status="complete"
        highlightedViolationId={null}
        onVersionChange={onVersionChange}
        onAcceptCorrection={vi.fn()}
      />
    );

    const thumbnails = screen.getAllByTestId('version-thumbnail');
    fireEvent.click(thumbnails[1]);

    expect(onVersionChange).toHaveBeenCalledWith(1);
  });

  it('calls onAcceptCorrection when ship it button is clicked', () => {
    const onAcceptCorrection = vi.fn();
    render(
      <Canvas
        imageUrl="https://example.com/image.png"
        violations={[]}
        versions={[]}
        currentVersion={0}
        complianceScore={85}
        status="complete"
        highlightedViolationId={null}
        onVersionChange={vi.fn()}
        onAcceptCorrection={onAcceptCorrection}
      />
    );

    const button = screen.getByTestId('ship-it-button');
    fireEvent.click(button);

    expect(onAcceptCorrection).toHaveBeenCalled();
  });

  it('renders error state when status is error', () => {
    render(
      <Canvas
        violations={[]}
        versions={[]}
        currentVersion={0}
        complianceScore={0}
        status="error"
        highlightedViolationId={null}
        onVersionChange={vi.fn()}
        onAcceptCorrection={vi.fn()}
      />
    );

    expect(screen.getByText('Generation Failed')).toBeTruthy();
    expect(screen.getByText('Please try again or adjust your prompt')).toBeTruthy();
  });
});
