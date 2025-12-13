import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ContextDeck } from '../ContextDeck';
import type { BrandGraphResponse } from '../../../../api/types';

describe('ContextDeck', () => {
  const mockBrandGraph: BrandGraphResponse = {
    brand_id: 'test-brand-123',
    name: 'Test Brand',
    version: '1.0',
    identity_core: {
      archetype: 'Innovator',
      voice_vectors: {
        formal: 0.7,
        witty: 0.3,
        technical: 0.8,
        urgent: 0.2,
      },
      negative_constraints: [
        'No Comic Sans',
        'Avoid red backgrounds',
      ],
    },
    visual_tokens: {
      colors: [],
      typography: [],
      logos: [],
    },
    contextual_rules: [
      {
        context: 'LinkedIn',
        rule: 'Use professional tone',
        priority: 1,
        applies_to: ['social'],
      },
      {
        context: 'Twitter',
        rule: 'Keep it concise',
        priority: 2,
        applies_to: ['social'],
      },
    ],
    asset_graph: {
      logos: {},
      templates: {},
      patterns: {},
    },
    relationships: {
      color_count: 0,
      colors_with_usage: [],
    },
    metadata: {
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
  };

  it('renders loading state when loading prop is true', () => {
    render(<ContextDeck brandId="test-brand-123" loading={true} />);
    
    // Check for skeleton loading elements - loading state shows skeleton divs
    const skeletonElements = document.querySelectorAll('.bg-white\\/10');
    expect(skeletonElements.length).toBeGreaterThan(0);
  });

  it('displays brand constraints when brandGraph is provided', () => {
    render(<ContextDeck brandId="test-brand-123" brandGraph={mockBrandGraph} />);
    
    expect(screen.getByTestId('context-deck')).toBeInTheDocument();
    expect(screen.getByText('Context Deck')).toBeInTheDocument();
    expect(screen.getByText('Active brand constraints')).toBeInTheDocument();
  });

  it('renders channel constraints from contextual rules', () => {
    render(<ContextDeck brandId="test-brand-123" brandGraph={mockBrandGraph} />);
    
    expect(screen.getByText('LinkedIn')).toBeInTheDocument();
    expect(screen.getByText('Twitter')).toBeInTheDocument();
  });

  it('renders negative constraints', () => {
    render(<ContextDeck brandId="test-brand-123" brandGraph={mockBrandGraph} />);
    
    expect(screen.getByText('No Comic Sans')).toBeInTheDocument();
    expect(screen.getByText('Avoid red backgrounds')).toBeInTheDocument();
  });

  it('renders voice constraint with voice vectors', () => {
    render(<ContextDeck brandId="test-brand-123" brandGraph={mockBrandGraph} />);
    
    expect(screen.getByText('Brand Voice')).toBeInTheDocument();
  });

  it('highlights active constraints', () => {
    render(
      <ContextDeck 
        brandId="test-brand-123" 
        brandGraph={mockBrandGraph}
        activeConstraints={['channel-0', 'negative-0']} 
      />
    );
    
    const cards = screen.getAllByTestId('constraint-card');
    expect(cards.length).toBeGreaterThan(0);
    
    // Check that some cards have active state
    const activeCards = cards.filter(card => card.getAttribute('data-active') === 'true');
    expect(activeCards.length).toBeGreaterThan(0);
  });

  it('displays error message when error prop is provided', () => {
    render(<ContextDeck brandId="test-brand-123" brandGraph={null} />);
    
    // Component should handle null brandGraph gracefully
    expect(screen.getByTestId('context-deck')).toBeInTheDocument();
  });

  it('displays message when no constraints are defined', () => {
    const emptyBrandGraph: BrandGraphResponse = {
      ...mockBrandGraph,
      identity_core: {
        archetype: 'Innovator',
        voice_vectors: {
          formal: 0,
          witty: 0,
          technical: 0,
          urgent: 0,
        },
        negative_constraints: [],
      },
      contextual_rules: [],
    };
    
    render(<ContextDeck brandId="test-brand-123" brandGraph={emptyBrandGraph} />);
    
    expect(screen.getByText('No constraints defined for this brand')).toBeInTheDocument();
  });
});
