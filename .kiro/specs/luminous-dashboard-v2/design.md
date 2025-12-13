# Design Document: Luminous Structuralism Dashboard (UI v2.5)

## Overview

The Luminous Structuralism Dashboard represents a complete redesign of the Mobius Brand Governance Engine frontend, replacing the existing industrial neumorphic design system with a modern "Bento Grid" layout featuring glassmorphism, deep dark mode, and neon data accents.

### Design Philosophy

**"Luminous Structuralism"** - The UI is the stage; the Brand Asset is the star. The interface maintains chromatic neutrality (deep charcoal backgrounds) to avoid visual interference with generated brand assets, while using translucent glass layers and strategic neon accents to create a premium, precision-engineered aesthetic.

### Key Architectural Decisions

1. **Complete UI Replacement**: We preserve only the API client layer (`frontend/src/api/*`) and type definitions, rebuilding all UI components from scratch
2. **Supabase Realtime over WebSocket**: Leverage Supabase's real-time database subscriptions instead of maintaining custom WebSocket connections on Modal serverless infrastructure
3. **VisX for Data Visualization**: Use VisX for radial gauges and radar charts due to its modular, tree-shakeable architecture
4. **CSS-First Animations**: Prioritize CSS animations over JavaScript for performance and reduced bundle size
5. **Mobile-First Responsive**: Design for mobile first, then enhance for desktop using Tailwind breakpoints

## Architecture

### Technology Stack

- **Framework**: React 19.2.0 with TypeScript
- **Build Tool**: Vite 7.2.4
- **Styling**: Tailwind CSS 4.1.17
- **Icons**: Lucide React 0.556.0
- **Animation**: Framer Motion 12.23.25
- **Charts**: VisX (@visx/shape, @visx/gradient)
- **State Management**: React Context + Supabase Realtime
- **API Client**: Existing `frontend/src/api/client.ts`
- **Real-time**: Supabase Realtime (PostgreSQL subscriptions)

### Project Structure

```
frontend/src/
├── api/                    # PRESERVE - Existing API client
│   ├── client.ts
│   ├── types.ts
│   └── websocket.ts       # May be deprecated in favor of Supabase
├── luminous/              # NEW - Luminous design system
│   ├── tokens.ts          # Design tokens (colors, typography, effects)
│   ├── components/        # Atomic design components
│   │   ├── atoms/
│   │   │   ├── GlassPanel.tsx
│   │   │   ├── GradientText.tsx
│   │   │   ├── ConnectionPulse.tsx
│   │   │   └── MonoText.tsx
│   │   ├── molecules/
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ConstraintCard.tsx
│   │   │   ├── ViolationItem.tsx
│   │   │   ├── ColorSwatch.tsx
│   │   │   └── VersionThumbnail.tsx
│   │   └── organisms/
│   │       ├── AppShell.tsx
│   │       ├── Director.tsx
│   │       ├── Canvas.tsx
│   │       ├── ComplianceGauge.tsx
│   │       ├── ContextDeck.tsx
│   │       └── TwinData.tsx
│   └── layouts/
│       └── BentoGrid.tsx
├── hooks/                 # NEW - Custom hooks
│   ├── useSupabaseRealtime.ts
│   ├── useJobStatus.ts
│   └── useSessionHistory.ts
├── context/               # PRESERVE & EXTEND
│   ├── BrandContext.tsx   # Existing
│   └── DashboardContext.tsx  # NEW
└── views/
    └── Dashboard.tsx      # NEW - Main dashboard view
```


## Components and Interfaces

### Design Token System

**File**: `frontend/src/luminous/tokens.ts`

```typescript
export const luminousTokens = {
  colors: {
    void: '#101012',                    // Background
    glass: 'rgba(255, 255, 255, 0.03)', // Surface
    border: 'rgba(255, 255, 255, 0.08)', // Borders
    accent: {
      gradient: 'linear-gradient(135deg, #7C3AED 0%, #2563EB 100%)',
      purple: '#7C3AED',
      blue: '#2563EB',
    },
    compliance: {
      pass: '#10B981',      // ≥95%
      review: '#F59E0B',    // 70-95%
      critical: '#EF4444',  // <70%
    },
    text: {
      body: '#94A3B8',      // Slate-400
      high: '#F1F5F9',      // High contrast
      muted: '#64748B',     // Slate-500
    },
  },
  typography: {
    fontFamily: {
      sans: '"Inter", "Geist Sans", system-ui, sans-serif',
      mono: '"JetBrains Mono", "Fira Code", monospace',
    },
    tracking: {
      tight: '-0.02em',
      normal: '0',
    },
  },
  effects: {
    glow: '0 0 20px rgba(37, 99, 235, 0.15)',
    glowStrong: '0 0 30px rgba(37, 99, 235, 0.3)',
    backdropBlur: 'blur(12px)',
  },
  animation: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '500ms',
    },
    easing: {
      smooth: 'cubic-bezier(0.4, 0, 0.2, 1)',
      bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    },
  },
};
```

### Atomic Components

#### GlassPanel

**Purpose**: Reusable glassmorphism panel component

```typescript
interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
}

// Usage: <GlassPanel glow={isActive}>Content</GlassPanel>
```

**Styling**: `bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl`

#### GradientText

**Purpose**: Animated gradient text for AI status indicators

```typescript
interface GradientTextProps {
  children: string;
  animate?: boolean;
}

// Usage: <GradientText animate>Gemini 3 Pro - Thinking...</GradientText>
```

**Styling**: Uses CSS `background-clip: text` with animated gradient position

#### ConnectionPulse

**Purpose**: WebSocket connection status indicator

```typescript
interface ConnectionPulseProps {
  status: 'connected' | 'disconnected' | 'connecting';
}

// Usage: <ConnectionPulse status={connectionStatus} />
```

**Styling**: 
- Connected: `bg-green-500` with pulse animation
- Disconnected: `bg-red-500` static
- Connecting: `bg-yellow-500` with pulse animation

#### MonoText

**Purpose**: Monospace text for hex codes and data

```typescript
interface MonoTextProps {
  children: string;
  className?: string;
}

// Usage: <MonoText>#2563EB</MonoText>
```

### Molecular Components

#### ChatMessage

**Purpose**: Individual chat message in Director

```typescript
interface ChatMessageProps {
  role: 'user' | 'system';
  content: string;
  timestamp: Date;
}
```

**Layout**:
- User messages: `flex justify-end`, subtle purple tint background
- System messages: `flex justify-start`, neutral glass background

#### ConstraintCard

**Purpose**: Pill-shaped constraint card in Context Deck

```typescript
interface ConstraintCardProps {
  type: 'channel' | 'negative' | 'voice';
  label: string;
  icon: React.ReactNode;
  active?: boolean;
  metadata?: {
    voiceVectors?: { formal: number; witty: number; technical: number; urgent: number };
  };
}
```

**Styling**: Pill shape with icon on left, label in center, optional radar chart on right

#### ViolationItem

**Purpose**: Clickable violation list item in Compliance Gauge

```typescript
interface ViolationItemProps {
  violation: {
    id: string;
    severity: 'critical' | 'warning' | 'info';
    message: string;
  };
  onClick: () => void;
}
```

**Interaction**: Clicking triggers focus effect on corresponding Canvas bounding box

#### ColorSwatch

**Purpose**: Split pill showing detected vs. brand color

```typescript
interface ColorSwatchProps {
  detected: string;  // Hex code
  brand: string;     // Hex code
  distance: number;  // Color distance metric
  pass: boolean;
}
```

**Layout**: Left half shows detected color, right half shows brand color, tooltip shows distance

#### VersionThumbnail

**Purpose**: Thumbnail in Version Scrubber timeline

```typescript
interface VersionThumbnailProps {
  imageUrl: string;
  score: number;
  timestamp: Date;
  active: boolean;
  onClick: () => void;
}
```

### Organism Components

#### AppShell

**Purpose**: Fixed header with logo, utilities, and connection status

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ [Logo] Brand Governance Engine    [●] [⚙] [👤]         │
└─────────────────────────────────────────────────────────┘
```

**Props**:
```typescript
interface AppShellProps {
  connectionStatus: 'connected' | 'disconnected' | 'connecting';
  onSettingsClick: () => void;
  userAvatar?: string;
}
```

#### Director

**Purpose**: Multi-turn chat interface

**Layout**:
```
┌─────────────────────┐
│ Chat History        │
│ [Messages...]       │
│                     │
│ [Quick Actions]     │
│ [Input Field]       │
│ [Gemini Status]     │
└─────────────────────┘
```

**Props**:
```typescript
interface DirectorProps {
  sessionId: string;
  onSubmit: (prompt: string) => void;
  isGenerating: boolean;
}
```

**State Management**: Uses local state for chat history, syncs with backend via API

#### Canvas

**Purpose**: Image viewport with bounding boxes and version scrubber

**Layout**:
```
┌─────────────────────────────────┐
│                                 │
│     [Generated Image]           │
│     [Bounding Boxes]            │
│                                 │
│ [Version Scrubber Timeline]     │
│ [Action Button]                 │
└─────────────────────────────────┘
```

**Props**:
```typescript
interface CanvasProps {
  imageUrl?: string;
  violations: Violation[];
  versions: Version[];
  currentVersion: number;
  complianceScore: number;
  status: 'generating' | 'auditing' | 'complete' | 'error';
  onVersionChange: (index: number) => void;
  onAcceptCorrection: () => void;
}
```

**Bounding Box Rendering**:
```typescript
interface BoundingBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  severity: 'critical' | 'warning';
  label: string;
}
```

#### ComplianceGauge

**Purpose**: Radial donut chart with violation list

**Layout**:
```
┌─────────────────────┐
│   ╭─────╮           │
│  │  88%  │          │
│   ╰─────╯           │
│                     │
│ Violations:         │
│ ⚠ Logo margin       │
│ ⚠ Font usage        │
└─────────────────────┘
```

**Props**:
```typescript
interface ComplianceGaugeProps {
  score: number;
  violations: Violation[];
  onViolationClick: (violationId: string) => void;
}
```

**VisX Implementation**: Use `@visx/shape` Arc component for donut chart

#### ContextDeck

**Purpose**: Vertical stack of constraint cards

**Props**:
```typescript
interface ContextDeckProps {
  brandId: string;
  activeConstraints: Constraint[];
}
```

**Data Source**: Fetches from `/brands/{id}/graph` on mount

#### TwinData

**Purpose**: Visual token inspector (colors, fonts)

**Layout**:
```
┌─────────────────────┐
│ Compressed Twin     │
│                     │
│ Colors:             │
│ [#2664EC | #2563EB] │
│ Distance: 1.2 ✓     │
│                     │
│ Fonts:              │
│ Inter-Bold ✓        │
└─────────────────────┘
```

**Props**:
```typescript
interface TwinDataProps {
  detectedColors: string[];
  brandColors: string[];
  detectedFonts: Array<{ family: string; weight: string; allowed: boolean }>;
}
```


## Data Models

### Dashboard State

```typescript
interface DashboardState {
  // Current job
  jobId: string | null;
  sessionId: string | null;
  brandId: string;
  
  // Generation state
  status: JobStatus;
  progress: number;
  currentImageUrl?: string;
  
  // Compliance data
  complianceScore?: number;
  violations: Violation[];
  
  // Twin data
  twinData?: {
    colorsDetected: string[];
    fontsDetected: Array<{ family: string; weight: string }>;
  };
  
  // Session history
  versions: Version[];
  currentVersionIndex: number;
  
  // Chat history
  messages: ChatMessage[];
  
  // Connection state
  connectionStatus: 'connected' | 'disconnected' | 'connecting';
}
```

### API Response Types

**Generation Request**:
```typescript
interface GenerateRequest {
  brand_id: string;
  prompt: string;
  session_id?: string;  // For multi-turn
  context?: string;     // e.g., "social_linkedin"
}

interface GenerateResponse {
  job_id: string;
  status: JobStatus;
  queue_position?: number;
}
```

**Job Status** (from Supabase Realtime):
```typescript
interface JobStatusUpdate {
  job_id: string;
  brand_id: string;
  prompt: string;
  status: 'pending' | 'generating' | 'auditing' | 'correcting' | 'completed' | 'failed';
  progress: number;
  current_image_url?: string;
  compliance_score?: number;
  violations?: Violation[];
  twin_data?: TwinData;
  error?: string;
  created_at: string;
  updated_at: string;
}
```

**Session History**:
```typescript
interface Version {
  attempt_id: number;
  image_url: string;
  thumb_url: string;
  score: number;
  timestamp: string;
  prompt: string;
}

interface SessionHistoryResponse {
  session_id: string;
  versions: Version[];
}
```

**Brand Graph** (for Context Deck):
```typescript
interface BrandGraphResponse {
  brand_id: string;
  identity_core: {
    archetype: string;
    voice_vectors: {
      formal: number;
      witty: number;
      technical: number;
      urgent: number;
    };
    negative_constraints: string[];
  };
  contextual_rules: Array<{
    context: string;
    rule: string;
    priority: number;
  }>;
}
```

### Violation Model

```typescript
interface Violation {
  id: string;
  rule_id: string;
  severity: 'critical' | 'warning' | 'info';
  message: string;
  bounding_box?: [number, number, number, number]; // [x, y, w, h]
  fix_suggestion?: string;
}
```

### Constraint Model

```typescript
interface Constraint {
  id: string;
  type: 'channel' | 'negative' | 'voice';
  label: string;
  icon: string;
  active: boolean;
  metadata?: {
    voiceVectors?: {
      formal: number;
      witty: number;
      technical: number;
      urgent: number;
    };
    platform?: string;
  };
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Connection Status Indicator Correctness

*For any* connection status value ('connected', 'disconnected', 'connecting'), the connection pulse dot should display the correct color: green for connected, red for disconnected, yellow for connecting.

**Validates: Requirements 2.5, 2.6**

### Property 2: Chat Message Rendering Completeness

*For any* list of chat messages, all messages should be rendered in the DOM with correct role-based alignment (user messages right-aligned, system messages left-aligned).

**Validates: Requirements 4.1, 4.2**

### Property 3: Input Character Limit Enforcement

*For any* string input to the prompt field, if the length exceeds 1000 characters, the system should prevent submission or truncate the input.

**Validates: Requirements 4.7**

### Property 4: Optimistic Message Update

*For any* user message submission, the message should appear in the chat history immediately before backend confirmation is received.

**Validates: Requirements 4.11**

### Property 5: Bounding Box Rendering Completeness

*For any* list of violations containing bounding box coordinates, the system should render a corresponding absolutely-positioned div overlay for each violation.

**Validates: Requirements 5.4**

### Property 6: Conditional Action Button Display

*For any* compliance score value, the system should display the correct primary action button: "Accept Auto-Correction" with gold glow for scores 70-95%, "Download / Export" for scores ≥95%, and no action button for scores <70%.

**Validates: Requirements 5.10, 5.11**

### Property 7: Violation Click Highlighting

*For any* violation item clicked in the Compliance Gauge, the corresponding bounding box on the Canvas should be highlighted while others are dimmed.

**Validates: Requirements 5.12, 6.8**

### Property 8: Version History Navigation

*For any* version thumbnail clicked in the Version Scrubber, the system should load that version's complete state including image URL, audit data, and chat context.

**Validates: Requirements 5.13, 10.7**

### Property 9: Compliance Gauge Color Mapping

*For any* compliance score value, the gauge color should match the correct threshold: #10B981 for ≥95%, #F59E0B for 70-95%, #EF4444 for <70%.

**Validates: Requirements 6.3, 6.4, 6.5**

### Property 10: Violation Severity Grouping

*For any* list of violations with mixed severity levels, the system should group and display them in order: Critical, Warning, Info.

**Validates: Requirements 6.9**

### Property 11: Constraint Highlighting on Violation

*For any* constraint that appears in the violation list, the corresponding constraint card in the Context Deck should be highlighted.

**Validates: Requirements 7.7**

### Property 12: Color Distance Tooltip Display

*For any* color swatch displaying detected vs. brand colors, the tooltip should contain the calculated distance metric.

**Validates: Requirements 8.5**

### Property 13: Font Compliance Status Display

*For any* detected font, the system should display the correct compliance status indicator: "(Allowed)" or "(Forbidden)" based on brand guidelines.

**Validates: Requirements 8.8**

### Property 14: Status-Driven Canvas Rendering

*For any* job status change, the Canvas should display the correct UI state: skeleton loader for 'generating', "Scanning Compliance..." overlay for 'auditing', image with audit data for 'completed'.

**Validates: Requirements 9.2, 9.3, 9.4**

### Property 15: WebSocket Fallback Behavior

*For any* WebSocket connection failure, the system should automatically fall back to polling mode without user intervention.

**Validates: Requirements 9.10**

### Property 16: Session ID Persistence

*For any* prompt submission within an active session, the API request should include the session_id parameter.

**Validates: Requirements 10.2**

### Property 17: Version History Growth

*For any* new version generated in a session, a new thumbnail should be added to the Version Scrubber.

**Validates: Requirements 10.3**

### Property 18: Touch Target Minimum Size

*For all* interactive elements (buttons, links, thumbnails), the computed dimensions should be at least 44x44 pixels to ensure touch-friendly interaction.

**Validates: Requirements 11.6**

### Property 19: Error Message Display on Failure

*For any* generation request that fails, an error message should appear in the Director chat interface.

**Validates: Requirements 13.3**

### Property 20: Exponential Backoff Retry Timing

*For any* sequence of failed API requests, the retry delay should increase exponentially (e.g., 1s, 2s, 4s, 8s).

**Validates: Requirements 13.7**

### Property 21: ARIA Label Completeness

*For all* icon-only buttons in the interface, an aria-label attribute should be present with descriptive text.

**Validates: Requirements 14.2**

### Property 22: Aria-Live Region Updates

*For any* significant state change (status updates, score changes, errors), the corresponding aria-live region should be updated to announce the change to screen readers.

**Validates: Requirements 14.5**

### Property 23: Color Contrast Compliance

*For all* text elements in the interface, the color contrast ratio between text and background should be at least 4.5:1 to meet WCAG AA standards.

**Validates: Requirements 14.6**


## Error Handling

### Network Errors

**Strategy**: Graceful degradation with user-friendly messaging

1. **Generation Request Failure**:
   - Display error message in Director chat
   - Provide "Retry" button
   - Log detailed error to console for debugging

2. **Audit Service Unavailable**:
   - Display image if generation succeeded
   - Show grey Compliance Gauge with "Audit Unavailable" message
   - Allow download with warning toast
   - Retry audit in background

3. **WebSocket Connection Failure**:
   - Automatically fall back to polling mode (5-second intervals)
   - Display yellow connection pulse indicator
   - Show toast notification: "Real-time updates unavailable, using polling"

4. **Image Load Failure**:
   - Display placeholder with "Image failed to load" message
   - Provide "Reload" button
   - Check if image URL is valid/accessible

### State Errors

**Strategy**: Prevent invalid states through TypeScript and runtime checks

1. **Missing Job ID**:
   - Redirect to brand selection if no active job
   - Clear stale session data

2. **Invalid Compliance Score**:
   - Clamp score to 0-100 range
   - Log warning if score is out of bounds

3. **Malformed Violation Data**:
   - Skip rendering bounding boxes with invalid coordinates
   - Log warning with violation ID

### User Input Errors

**Strategy**: Validate and provide immediate feedback

1. **Empty Prompt**:
   - Disable submit button when input is empty
   - Show placeholder text: "Describe the asset you want to generate..."

2. **Prompt Too Long**:
   - Show character count: "842 / 1000"
   - Prevent typing beyond limit
   - Show warning at 900 characters: "Approaching character limit"

3. **Invalid Session State**:
   - Clear session and start fresh
   - Show toast: "Session expired, starting new conversation"

## Testing Strategy

### Unit Testing

**Framework**: Vitest with React Testing Library

**Coverage Areas**:
1. **Component Rendering**: Verify each component renders with correct props
2. **User Interactions**: Test button clicks, input changes, form submissions
3. **Conditional Rendering**: Test components render correctly based on state
4. **Error Boundaries**: Test error handling and fallback UI

**Example Unit Tests**:
- `GlassPanel` renders with correct glassmorphism classes
- `ConnectionPulse` displays correct color for each status
- `ChatMessage` aligns correctly based on role
- `ComplianceGauge` renders with correct score and color
- `ViolationItem` triggers onClick callback when clicked

### Property-Based Testing

**Framework**: fast-check (already in package.json)

**Configuration**: Each property test should run minimum 100 iterations

**Test Tagging**: Each property test must include a comment with format:
```typescript
// Feature: luminous-dashboard-v2, Property 1: Connection Status Indicator Correctness
```

**Property Test Examples**:

1. **Property 1: Connection Status Indicator**
```typescript
// Feature: luminous-dashboard-v2, Property 1: Connection Status Indicator Correctness
test('connection pulse displays correct color for any status', () => {
  fc.assert(
    fc.property(
      fc.constantFrom('connected', 'disconnected', 'connecting'),
      (status) => {
        const { container } = render(<ConnectionPulse status={status} />);
        const pulse = container.querySelector('[data-testid="connection-pulse"]');
        
        const expectedColor = status === 'connected' ? 'bg-green-500' 
          : status === 'disconnected' ? 'bg-red-500' 
          : 'bg-yellow-500';
        
        expect(pulse).toHaveClass(expectedColor);
      }
    ),
    { numRuns: 100 }
  );
});
```

2. **Property 9: Compliance Gauge Color Mapping**
```typescript
// Feature: luminous-dashboard-v2, Property 9: Compliance Gauge Color Mapping
test('gauge color matches score threshold for any score', () => {
  fc.assert(
    fc.property(
      fc.integer({ min: 0, max: 100 }),
      (score) => {
        const { container } = render(<ComplianceGauge score={score} violations={[]} />);
        const gauge = container.querySelector('[data-testid="compliance-gauge"]');
        
        const expectedColor = score >= 95 ? '#10B981'
          : score >= 70 ? '#F59E0B'
          : '#EF4444';
        
        const computedColor = window.getComputedStyle(gauge!).stroke;
        expect(computedColor).toBe(expectedColor);
      }
    ),
    { numRuns: 100 }
  );
});
```

3. **Property 10: Violation Severity Grouping**
```typescript
// Feature: luminous-dashboard-v2, Property 10: Violation Severity Grouping
test('violations are grouped by severity for any violation list', () => {
  fc.assert(
    fc.property(
      fc.array(
        fc.record({
          id: fc.uuid(),
          severity: fc.constantFrom('critical', 'warning', 'info'),
          message: fc.string(),
        })
      ),
      (violations) => {
        const { container } = render(<ComplianceGauge score={50} violations={violations} />);
        const items = container.querySelectorAll('[data-testid="violation-item"]');
        
        // Extract severity from each rendered item
        const renderedSeverities = Array.from(items).map(
          item => item.getAttribute('data-severity')
        );
        
        // Check that critical comes before warning, warning before info
        let lastSeverityIndex = -1;
        const severityOrder = ['critical', 'warning', 'info'];
        
        renderedSeverities.forEach(severity => {
          const currentIndex = severityOrder.indexOf(severity!);
          expect(currentIndex).toBeGreaterThanOrEqual(lastSeverityIndex);
          lastSeverityIndex = currentIndex;
        });
      }
    ),
    { numRuns: 100 }
  );
});
```

### Integration Testing

**Framework**: Playwright (already configured)

**Coverage Areas**:
1. **End-to-End Workflows**: Test complete user journeys
2. **Real-time Updates**: Test Supabase Realtime integration
3. **Multi-turn Sessions**: Test session persistence and history
4. **Responsive Behavior**: Test mobile and desktop layouts

**Example Integration Tests**:
- User submits prompt → sees generating state → sees completed image with audit
- User clicks violation → corresponding bounding box highlights
- User clicks version thumbnail → previous version loads
- WebSocket disconnects → system falls back to polling

### Visual Regression Testing

**Framework**: Playwright with screenshot comparison

**Coverage Areas**:
1. **Glassmorphism Effects**: Verify glass panels render correctly
2. **Gradient Animations**: Verify gradient text animates smoothly
3. **Bounding Box Overlays**: Verify overlays position correctly
4. **Responsive Layouts**: Verify grid collapses correctly on mobile

### Accessibility Testing

**Tools**: 
- axe-core (via @axe-core/playwright)
- Manual keyboard navigation testing
- Screen reader testing (NVDA/JAWS)

**Coverage Areas**:
1. **Keyboard Navigation**: All interactive elements reachable via Tab
2. **Focus Indicators**: Visible focus outlines on all focusable elements
3. **ARIA Labels**: All icon buttons have descriptive labels
4. **Color Contrast**: All text meets WCAG AA standards (4.5:1)
5. **Screen Reader Announcements**: State changes announced via aria-live


## State Management

### Context Architecture

**DashboardContext**: Central state management for dashboard

```typescript
interface DashboardContextValue {
  // Job state
  jobId: string | null;
  sessionId: string | null;
  brandId: string;
  status: JobStatus;
  progress: number;
  
  // Image and audit data
  currentImageUrl?: string;
  complianceScore?: number;
  violations: Violation[];
  twinData?: TwinData;
  
  // Session history
  versions: Version[];
  currentVersionIndex: number;
  
  // Chat
  messages: ChatMessage[];
  
  // Connection
  connectionStatus: 'connected' | 'disconnected' | 'connecting';
  
  // Actions
  submitPrompt: (prompt: string) => Promise<void>;
  loadVersion: (index: number) => void;
  acceptCorrection: () => Promise<void>;
  retryGeneration: () => Promise<void>;
}
```

**Provider Implementation**:
```typescript
export function DashboardProvider({ children, brandId }: Props) {
  const [state, setState] = useState<DashboardState>(initialState);
  
  // Supabase Realtime subscription
  useSupabaseRealtime(state.jobId, (update) => {
    setState(prev => ({
      ...prev,
      status: update.status,
      progress: update.progress,
      currentImageUrl: update.current_image_url,
      complianceScore: update.compliance_score,
      violations: update.violations || [],
      twinData: update.twin_data,
    }));
  });
  
  // Actions
  const submitPrompt = async (prompt: string) => {
    // Optimistically add message
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, { role: 'user', content: prompt, timestamp: new Date() }],
    }));
    
    // Call API
    const response = await apiClient.post<GenerateResponse>('/generate', {
      brand_id: brandId,
      prompt,
      session_id: state.sessionId,
    });
    
    setState(prev => ({
      ...prev,
      jobId: response.job_id,
      status: response.status,
    }));
  };
  
  // ... other actions
  
  return (
    <DashboardContext.Provider value={{ ...state, submitPrompt, loadVersion, acceptCorrection, retryGeneration }}>
      {children}
    </DashboardContext.Provider>
  );
}
```

### Custom Hooks

#### useSupabaseRealtime

**Purpose**: Subscribe to job status updates via Supabase Realtime

```typescript
function useSupabaseRealtime(
  jobId: string | null,
  onUpdate: (update: JobStatusUpdate) => void
) {
  useEffect(() => {
    if (!jobId) return;
    
    const subscription = supabase
      .channel(`job:${jobId}`)
      .on('postgres_changes', {
        event: 'UPDATE',
        schema: 'public',
        table: 'jobs',
        filter: `id=eq.${jobId}`,
      }, (payload) => {
        onUpdate(payload.new as JobStatusUpdate);
      })
      .subscribe();
    
    return () => {
      subscription.unsubscribe();
    };
  }, [jobId, onUpdate]);
}
```

#### useJobStatus

**Purpose**: Fetch and track job status with polling fallback

```typescript
function useJobStatus(jobId: string | null) {
  const [status, setStatus] = useState<JobStatusUpdate | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  
  // Try Supabase Realtime first
  useSupabaseRealtime(jobId, (update) => {
    setStatus(update);
    setIsPolling(false);
  });
  
  // Fallback to polling if Realtime fails
  useEffect(() => {
    if (!jobId || !isPolling) return;
    
    const interval = setInterval(async () => {
      try {
        const response = await apiClient.get<JobStatusUpdate>(`/jobs/${jobId}`);
        setStatus(response);
      } catch (err) {
        setError(err as Error);
      }
    }, 5000);
    
    return () => clearInterval(interval);
  }, [jobId, isPolling]);
  
  return { status, error, isPolling };
}
```

#### useSessionHistory

**Purpose**: Fetch and manage session version history

```typescript
function useSessionHistory(sessionId: string | null) {
  const [versions, setVersions] = useState<Version[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  
  useEffect(() => {
    if (!sessionId) return;
    
    apiClient.get<SessionHistoryResponse>(`/sessions/${sessionId}/history`)
      .then(response => {
        setVersions(response.versions);
        setCurrentIndex(response.versions.length - 1);
      })
      .catch(console.error);
  }, [sessionId]);
  
  const loadVersion = (index: number) => {
    setCurrentIndex(index);
  };
  
  const addVersion = (version: Version) => {
    setVersions(prev => [...prev, version]);
    setCurrentIndex(versions.length);
  };
  
  return { versions, currentIndex, currentVersion: versions[currentIndex], loadVersion, addVersion };
}
```

## Performance Considerations

### Bundle Size Optimization

1. **Lazy Load Heavy Components**:
   - Defer loading of VisX chart components until needed
   - Use React.lazy() for non-critical components

2. **Tree-Shaking**:
   - Import only needed VisX modules: `@visx/shape`, `@visx/gradient`
   - Import only needed Lucide icons

3. **Code Splitting**:
   - Split dashboard into separate chunk from onboarding
   - Split design system into separate chunk

### Runtime Performance

1. **Memoization**:
   - Use `React.memo()` for expensive components (Canvas, ComplianceGauge)
   - Use `useMemo()` for expensive calculations (color distance, violation grouping)
   - Use `useCallback()` for event handlers passed to children

2. **Virtualization**:
   - Use virtual scrolling for long violation lists (react-window)
   - Use virtual scrolling for version scrubber if >50 versions

3. **Debouncing**:
   - Debounce input field changes (300ms)
   - Debounce window resize events for responsive layout

### Animation Performance

1. **CSS-First Approach**:
   - Use CSS transforms for animations (GPU-accelerated)
   - Use CSS transitions for simple state changes
   - Reserve Framer Motion for complex orchestrated animations

2. **Reduce Motion**:
   - Respect `prefers-reduced-motion` media query
   - Disable animations when user prefers reduced motion

## Deployment Considerations

### Environment Variables

```env
VITE_API_BASE_URL=https://rocoloco--mobius-v2-final-fastapi-app.modal.run/v1
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### Build Configuration

**Vite Config Optimizations**:
```typescript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom'],
          'design-system': ['framer-motion', 'lucide-react'],
          'charts': ['@visx/shape', '@visx/gradient'],
        },
      },
    },
  },
});
```

### Browser Support

- **Target**: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- **Polyfills**: None required (using native ES2020+ features)
- **Fallbacks**: Provide fallback for backdrop-filter (solid background)

## Migration Strategy

### Phase 1: Design System Setup (Week 1)

1. Create `frontend/src/luminous/tokens.ts` with design tokens
2. Create atomic components (GlassPanel, GradientText, ConnectionPulse, MonoText)
3. Set up Tailwind config with custom colors and utilities
4. Create Storybook stories for atomic components

### Phase 2: Layout & Shell (Week 1-2)

1. Create BentoGrid layout component
2. Create AppShell with header
3. Implement responsive breakpoints
4. Test layout on mobile and desktop

### Phase 3: Core Components (Week 2-3)

1. Build Director chat interface
2. Build Canvas with bounding boxes
3. Build ComplianceGauge with VisX
4. Build ContextDeck
5. Build TwinData panel

### Phase 4: State Management (Week 3)

1. Create DashboardContext
2. Implement useSupabaseRealtime hook
3. Implement useJobStatus with polling fallback
4. Implement useSessionHistory hook

### Phase 5: Integration & Testing (Week 4)

1. Connect components to real API
2. Test Supabase Realtime integration
3. Write unit tests for all components
4. Write property-based tests for correctness properties
5. Write integration tests for key workflows

### Phase 6: Polish & Accessibility (Week 4-5)

1. Add animations and transitions
2. Implement error handling
3. Add ARIA labels and live regions
4. Test keyboard navigation
5. Test with screen readers
6. Run accessibility audit with axe-core

### Rollout Strategy

1. **Feature Flag**: Deploy behind feature flag, enable for internal testing
2. **Beta Users**: Enable for select beta users, gather feedback
3. **Gradual Rollout**: Enable for 10% → 50% → 100% of users
4. **Monitoring**: Track error rates, performance metrics, user feedback
5. **Rollback Plan**: Keep old UI available via feature flag for 2 weeks

