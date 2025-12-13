# Mobius Brand Governance Engine - Luminous Dashboard

The Luminous Structuralism Dashboard is a modern, glassmorphism-based interface for the Mobius Brand Governance Engine. It features a Bento Grid layout with real-time compliance monitoring, AI-powered asset generation, and comprehensive brand governance tools.

## Design Philosophy

**"Luminous Structuralism"** - The UI is the stage; the Brand Asset is the star. The interface maintains chromatic neutrality (deep charcoal backgrounds) to avoid visual interference with generated brand assets, while using translucent glass layers and strategic neon accents to create a premium, precision-engineered aesthetic.

## Features

- **Luminous Design System**: Premium glassmorphism effects with deep dark mode aesthetics
- **Bento Grid Layout**: Five-zone dashboard (Director, Canvas, Compliance Gauge, Context Deck, Twin Data)
- **Real-time Updates**: Supabase Realtime integration for live job status and compliance monitoring
- **Multi-turn Sessions**: Iterative asset refinement through conversational AI
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Accessibility**: WCAG AA compliant with keyboard navigation and screen reader support

## Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Supabase project (for backend integration)

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

### Environment Variables

Create a `.env` file in the frontend directory (or use the root `.env`):

```bash
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# API Configuration (optional)
VITE_API_BASE_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── api/                    # API client and types
│   │   ├── client.ts           # HTTP client
│   │   ├── types.ts            # TypeScript interfaces
│   │   └── websocket.ts        # WebSocket utilities
│   ├── luminous/               # Luminous design system
│   │   ├── tokens.ts           # Design tokens
│   │   ├── COMPONENTS.md       # Component documentation
│   │   ├── components/
│   │   │   ├── atoms/          # Basic building blocks
│   │   │   ├── molecules/      # Composed components
│   │   │   └── organisms/      # Complex sections
│   │   └── layouts/
│   │       └── BentoGrid.tsx   # Main layout
│   ├── hooks/                  # Custom React hooks
│   │   ├── useSupabaseRealtime.ts
│   │   ├── useJobStatus.ts
│   │   └── useSessionHistory.ts
│   ├── context/                # React Context providers
│   │   └── DashboardContext.tsx
│   └── views/
│       └── Dashboard.tsx       # Main dashboard view
├── tests/
│   ├── integration/            # Playwright E2E tests
│   └── visual/                 # Visual regression tests
└── public/                     # Static assets
```

## Architecture

### Design System

The Luminous design system follows atomic design principles:

- **Atoms**: GlassPanel, GradientText, ConnectionPulse, MonoText
- **Molecules**: ChatMessage, ViolationItem, ConstraintCard, ColorSwatch
- **Organisms**: AppShell, Director, Canvas, ComplianceGauge, ContextDeck, TwinData
- **Layouts**: BentoGrid

See [COMPONENTS.md](src/luminous/COMPONENTS.md) for detailed API documentation.

### Dashboard Zones

| Zone | Purpose | Location |
|------|---------|----------|
| **Director** | Multi-turn chat interface for AI interaction | Top-left |
| **Canvas** | Image viewport with compliance bounding boxes | Center |
| **Compliance Gauge** | Radial chart showing overall brand compliance | Top-right |
| **Context Deck** | Active brand constraints visualization | Bottom-left |
| **Twin Data** | Detected visual tokens (colors, fonts) inspector | Bottom-right |

### State Management

- **DashboardContext**: Central state management with Supabase Realtime integration
- **Custom Hooks**: 
  - `useJobStatus` - Real-time job status tracking
  - `useSessionHistory` - Multi-turn session management
  - `useSupabaseRealtime` - WebSocket subscriptions

## Development

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run unit tests
npm test

# Run tests in watch mode
npm run test:watch

# Run visual/E2E tests
npm run test:visual

# Run linting
npm run lint
```

### Testing

The project includes comprehensive testing:

| Type | Framework | Command |
|------|-----------|---------|
| Unit Tests | Vitest + React Testing Library | `npm test` |
| Property-Based Tests | fast-check | `npm test` |
| E2E Tests | Playwright | `npm run test:visual` |
| Visual Regression | Playwright Screenshots | `npm run test:visual` |
| Accessibility | axe-core | `npm run test:visual` |

### Code Style

- TypeScript strict mode enabled
- ESLint with React hooks plugin
- Tailwind CSS for styling
- Framer Motion for animations

## Design Tokens

The design system uses centralized tokens defined in `src/luminous/tokens.ts`:

```typescript
import { luminousTokens, getComplianceColor } from '@/luminous/tokens';

// Colors
luminousTokens.colors.void          // #101012 - Background
luminousTokens.colors.compliance.pass    // #10B981 - ≥95%
luminousTokens.colors.compliance.review  // #F59E0B - 70-95%
luminousTokens.colors.compliance.critical // #EF4444 - <70%

// Typography
luminousTokens.typography.fontFamily.sans  // Inter, Geist Sans
luminousTokens.typography.fontFamily.mono  // JetBrains Mono

// Effects
luminousTokens.effects.glow         // Blue glow effect
luminousTokens.effects.backdropBlur // blur(12px)
```

## Accessibility

The dashboard follows WCAG AA guidelines:

- ✅ Keyboard navigation for all interactive elements
- ✅ ARIA labels on icon-only buttons
- ✅ Focus indicators (2px blue outline)
- ✅ Color contrast ratios ≥4.5:1
- ✅ Reduced motion support (`prefers-reduced-motion`)
- ✅ Screen reader announcements via `aria-live` regions
- ✅ Touch targets minimum 44x44px

## Performance Optimizations

- **Code Splitting**: Lazy loading for VisX chart components
- **Memoization**: React.memo() on Canvas and ComplianceGauge
- **CSS Animations**: GPU-accelerated transforms
- **Debouncing**: Input changes debounced at 300ms
- **Tree Shaking**: Modular VisX imports

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the atomic design pattern for new components
2. Add TypeScript types for all props
3. Include JSDoc comments for public APIs
4. Write unit tests for new functionality
5. Ensure accessibility compliance

## License

Proprietary - Mobius Brand Governance Engine
