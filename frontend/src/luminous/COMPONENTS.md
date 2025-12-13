# Luminous Design System - Component Documentation

This document provides comprehensive API documentation for all components in the Luminous Structuralism design system.

## Table of Contents

- [Design Tokens](#design-tokens)
- [Atomic Components](#atomic-components)
  - [GlassPanel](#glasspanel)
  - [GradientText](#gradienttext)
  - [ConnectionPulse](#connectionpulse)
  - [MonoText](#monotext)
  - [SpotlightCard](#spotlightcard)
  - [AriaLiveRegions](#arialiveregions)
  - [Confetti](#confetti)
- [Molecular Components](#molecular-components)
  - [ChatMessage](#chatmessage)
  - [ViolationItem](#violationitem)
  - [ConstraintCard](#constraintcard)
  - [ColorSwatch](#colorswatch)
  - [VersionThumbnail](#versionthumbnail)
  - [BoundingBox](#boundingbox)
- [Organism Components](#organism-components)
  - [AppShell](#appshell)
  - [Director](#director)
  - [Canvas](#canvas)
  - [ComplianceGauge](#compliancegauge)
  - [ContextDeck](#contextdeck)
  - [TwinData](#twindata)
- [Layout Components](#layout-components)
  - [BentoGrid](#bentogrid)

---

## Design Tokens

The Luminous design system uses centralized design tokens defined in `tokens.ts`.

### Import

```typescript
import { luminousTokens, getComplianceColor, getConnectionColor } from '@/luminous/tokens';
```

### Token Structure

```typescript
luminousTokens = {
  colors: {
    void: '#101012',           // Deep charcoal background
    glass: 'rgba(255, 255, 255, 0.03)',  // Glass surface
    border: 'rgba(255, 255, 255, 0.08)', // Subtle borders
    accent: {
      gradient: 'linear-gradient(135deg, #7C3AED 0%, #2563EB 100%)',
      purple: '#7C3AED',
      blue: '#2563EB',
    },
    compliance: {
      pass: '#10B981',      // ≥95% score
      review: '#F59E0B',    // 70-95% score
      critical: '#EF4444',  // <70% score
    },
    text: {
      body: '#94A3B8',
      high: '#F1F5F9',
      muted: '#8B8B8B',
    },
  },
  typography: {
    fontFamily: {
      sans: '"Inter", "Geist Sans", system-ui, sans-serif',
      mono: '"JetBrains Mono", "Fira Code", monospace',
    },
  },
  effects: {
    glow: '0 0 20px rgba(37, 99, 235, 0.15)...',
    glowStrong: '0 0 30px rgba(37, 99, 235, 0.3)...',
    backdropBlur: 'blur(12px)',
  },
  animation: {
    duration: { fast: '150ms', normal: '300ms', slow: '500ms' },
    easing: { smooth: 'cubic-bezier(0.4, 0, 0.2, 1)' },
  },
}
```

### Utility Functions

```typescript
// Get compliance color based on score
getComplianceColor(score: number): string
// Returns: '#10B981' (≥95), '#F59E0B' (70-95), '#EF4444' (<70)

// Get connection status color class
getConnectionColor(status: 'connected' | 'disconnected' | 'connecting'): string
// Returns: 'bg-green-500', 'bg-red-500', or 'bg-yellow-500'
```

---

## Atomic Components

### GlassPanel

Premium glassmorphism container with interactive effects.

#### Import

```typescript
import { GlassPanel } from '@/luminous/components/atoms';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | `ReactNode` | required | Content to render inside the panel |
| `className` | `string` | `''` | Additional CSS classes |
| `glow` | `boolean` | `false` | Enable static glow effect (active/focus state) |
| `spotlight` | `boolean` | `false` | Enable interactive cursor spotlight |
| `noise` | `boolean` | `true` | Enable organic noise texture |
| `shimmer` | `boolean` | `false` | Enable entrance shimmer animation |
| `as` | `ElementType` | `'div'` | HTML element to render as |
| `onClick` | `() => void` | - | Click handler |

#### Usage

```tsx
// Basic usage
<GlassPanel>
  <p>Content inside glass panel</p>
</GlassPanel>

// With glow effect (for active states)
<GlassPanel glow>
  <p>Active panel with glow</p>
</GlassPanel>

// Interactive with spotlight
<GlassPanel spotlight shimmer>
  <p>Interactive panel with cursor spotlight</p>
</GlassPanel>

// As a button
<GlassPanel as="button" onClick={handleClick} glow={isActive}>
  Click me
</GlassPanel>
```

---

### GradientText

Animated gradient text for AI status indicators.

#### Import

```typescript
import { GradientText } from '@/luminous/components/atoms';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | `string` | required | Text content to display |
| `animate` | `boolean` | `false` | Enable breathing gradient animation |

#### Usage

```tsx
// Static gradient text
<GradientText>Gemini 3 Pro</GradientText>

// Animated (for "thinking" state)
<GradientText animate>Gemini 3 Pro - Thinking...</GradientText>
```

---

### ConnectionPulse

WebSocket connection status indicator dot.

#### Import

```typescript
import { ConnectionPulse } from '@/luminous/components/atoms';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `status` | `'connected' \| 'disconnected' \| 'connecting'` | required | Connection status |

#### Usage

```tsx
<ConnectionPulse status="connected" />   // Green with pulse
<ConnectionPulse status="disconnected" /> // Red, static
<ConnectionPulse status="connecting" />   // Yellow with pulse
```

---

### MonoText

Monospace text for hex codes and technical data.

#### Import

```typescript
import { MonoText } from '@/luminous/components/atoms';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | `string` | required | Text content |
| `className` | `string` | `''` | Additional CSS classes |

#### Usage

```tsx
<MonoText>#2563EB</MonoText>
<MonoText className="text-sm">Inter-Bold</MonoText>
```

---

### SpotlightCard

Card with interactive cursor spotlight effect.

#### Import

```typescript
import { SpotlightCard } from '@/luminous/components/atoms';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | `ReactNode` | required | Card content |
| `className` | `string` | `''` | Additional CSS classes |

---

### AriaLiveRegions

Accessibility component for screen reader announcements.

#### Import

```typescript
import { AriaLiveRegions } from '@/luminous/components/atoms';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `politeMessage` | `string` | `''` | Message for polite announcements |
| `assertiveMessage` | `string` | `''` | Message for assertive announcements |

#### Usage

```tsx
<AriaLiveRegions
  politeMessage={statusMessage}
  assertiveMessage={errorMessage}
/>
```

---

### Confetti

Celebration animation for high compliance scores.

#### Import

```typescript
import { Confetti } from '@/luminous/components/atoms';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `trigger` | `boolean` | `false` | Trigger confetti animation |
| `onComplete` | `() => void` | - | Callback when animation completes |

#### Usage

```tsx
<Confetti trigger={score >= 95} onComplete={() => setShowConfetti(false)} />
```

---

## Molecular Components

### ChatMessage

Individual chat message in the Director interface.

#### Import

```typescript
import { ChatMessage } from '@/luminous/components/molecules';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `role` | `'user' \| 'system' \| 'error'` | required | Message sender role |
| `content` | `string` | required | Message text content |
| `timestamp` | `Date` | required | Message timestamp |

#### Usage

```tsx
<ChatMessage
  role="user"
  content="Generate a LinkedIn banner with our brand colors"
  timestamp={new Date()}
/>

<ChatMessage
  role="system"
  content="I'll create a LinkedIn banner using your brand guidelines..."
  timestamp={new Date()}
/>

<ChatMessage
  role="error"
  content="Generation failed. Please try again."
  timestamp={new Date()}
/>
```

---

### ViolationItem

Clickable violation list item in ComplianceGauge.

#### Import

```typescript
import { ViolationItem } from '@/luminous/components/molecules';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `violation` | `{ id: string; severity: 'critical' \| 'warning' \| 'info'; message: string }` | required | Violation data |
| `onClick` | `() => void` | required | Click handler |
| `focused` | `boolean` | `false` | Whether item is keyboard-focused |
| `keyboardIndex` | `number` | - | Index for keyboard navigation |

#### Usage

```tsx
<ViolationItem
  violation={{
    id: 'v1',
    severity: 'critical',
    message: 'Logo margin too small'
  }}
  onClick={() => highlightBoundingBox('v1')}
  focused={focusedIndex === 0}
/>
```

---

### ConstraintCard

Pill-shaped constraint card for Context Deck.

#### Import

```typescript
import { ConstraintCard } from '@/luminous/components/molecules';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `type` | `'channel' \| 'negative' \| 'voice'` | required | Constraint type |
| `label` | `string` | required | Constraint label |
| `icon` | `ReactNode` | required | Icon component |
| `active` | `boolean` | `false` | Highlight state |
| `metadata` | `{ voiceVectors?: VoiceVectors }` | - | Optional metadata |

#### Usage

```tsx
import { Linkedin, EyeOff, Mic } from 'lucide-react';

<ConstraintCard
  type="channel"
  label="LinkedIn"
  icon={<Linkedin size={16} />}
  active={false}
/>

<ConstraintCard
  type="voice"
  label="Brand Voice"
  icon={<Mic size={16} />}
  metadata={{
    voiceVectors: { formal: 0.8, witty: 0.3, technical: 0.6, urgent: 0.2 }
  }}
/>
```

---

### ColorSwatch

Split pill showing detected vs. brand color comparison.

#### Import

```typescript
import { ColorSwatch } from '@/luminous/components/molecules';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `detected` | `string` | required | Detected color hex code |
| `brand` | `string` | required | Brand color hex code |
| `distance` | `number` | required | Color distance metric |
| `pass` | `boolean` | required | Whether color passes compliance |

#### Usage

```tsx
<ColorSwatch
  detected="#2664EC"
  brand="#2563EB"
  distance={1.2}
  pass={true}
/>
```

---

### VersionThumbnail

Thumbnail for Version Scrubber timeline.

#### Import

```typescript
import { VersionThumbnail } from '@/luminous/components/molecules';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `imageUrl` | `string` | required | Thumbnail image URL |
| `score` | `number` | required | Compliance score (0-100) |
| `timestamp` | `Date` | required | Version creation time |
| `active` | `boolean` | required | Whether version is active |
| `onClick` | `() => void` | required | Click handler |

#### Usage

```tsx
<VersionThumbnail
  imageUrl="/thumbnails/v1.jpg"
  score={88}
  timestamp={new Date()}
  active={currentVersion === 0}
  onClick={() => loadVersion(0)}
/>
```

---

### BoundingBox

Visual overlay for compliance violations on Canvas.

#### Import

```typescript
import { BoundingBox } from '@/luminous/components/molecules';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `x` | `number` | required | X coordinate |
| `y` | `number` | required | Y coordinate |
| `width` | `number` | required | Box width |
| `height` | `number` | required | Box height |
| `severity` | `'critical' \| 'warning'` | required | Violation severity |
| `label` | `string` | required | Violation description |
| `highlighted` | `boolean` | `false` | Highlight state |

#### Usage

```tsx
<BoundingBox
  x={100}
  y={50}
  width={200}
  height={100}
  severity="critical"
  label="Logo margin violation"
  highlighted={selectedViolation === 'v1'}
/>
```

---

## Organism Components

### AppShell

Universal app shell with fixed header.

#### Import

```typescript
import { AppShell } from '@/luminous/components/organisms';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | `ReactNode` | required | Main content |
| `connectionStatus` | `'connected' \| 'disconnected' \| 'connecting'` | required | WebSocket status |
| `onSettingsClick` | `() => void` | - | Settings button handler |
| `userAvatar` | `string` | - | User avatar URL |

#### Usage

```tsx
<AppShell
  connectionStatus="connected"
  onSettingsClick={() => openSettings()}
  userAvatar="/avatars/user.jpg"
>
  <BentoGrid {...zones} />
</AppShell>
```

---

### Director

Multi-turn chat interface for AI interaction.

#### Import

```typescript
import { Director } from '@/luminous/components/organisms';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `sessionId` | `string` | required | Current session ID |
| `messages` | `ChatMessage[]` | required | Chat history |
| `onSubmit` | `(prompt: string) => void` | required | Submit handler |
| `isGenerating` | `boolean` | required | Generation in progress |
| `onQuickAction` | `(action: string) => void` | - | Quick action handler |

---

### Canvas

Image viewport with bounding boxes and version scrubber.

#### Import

```typescript
import { Canvas } from '@/luminous/components/organisms';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `imageUrl` | `string` | - | Generated image URL |
| `violations` | `Violation[]` | required | Violation data |
| `versions` | `Version[]` | required | Version history |
| `currentVersion` | `number` | required | Active version index |
| `complianceScore` | `number` | required | Current score |
| `status` | `'generating' \| 'auditing' \| 'complete' \| 'error'` | required | Current status |
| `onVersionChange` | `(index: number) => void` | required | Version change handler |
| `onAcceptCorrection` | `() => void` | required | Accept correction handler |
| `highlightedViolation` | `string` | - | ID of highlighted violation |

---

### ComplianceGauge

Radial donut chart with violation list.

#### Import

```typescript
import { ComplianceGauge } from '@/luminous/components/organisms';
// Or lazy-loaded version:
import { LazyComplianceGauge } from '@/luminous/components/organisms';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `score` | `number` | required | Compliance score (0-100) |
| `violations` | `Violation[]` | required | Violation list |
| `onViolationClick` | `(id: string) => void` | required | Violation click handler |

---

### ContextDeck

Vertical stack of constraint cards.

#### Import

```typescript
import { ContextDeck } from '@/luminous/components/organisms';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `brandId` | `string` | required | Brand ID for fetching constraints |
| `activeConstraints` | `Constraint[]` | required | Active constraint list |
| `highlightedRules` | `string[]` | - | Rules to highlight |

---

### TwinData

Visual token inspector panel.

#### Import

```typescript
import { TwinData } from '@/luminous/components/organisms';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `detectedColors` | `string[]` | required | Detected color hex codes |
| `brandColors` | `string[]` | required | Brand color hex codes |
| `detectedFonts` | `FontInfo[]` | required | Detected font information |

---

## Layout Components

### BentoGrid

CSS Grid layout for the five dashboard zones.

#### Import

```typescript
import { BentoGrid } from '@/luminous/layouts';
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `director` | `ReactNode` | required | Director zone content |
| `canvas` | `ReactNode` | required | Canvas zone content |
| `gauge` | `ReactNode` | required | Compliance Gauge zone content |
| `context` | `ReactNode` | required | Context Deck zone content |
| `twin` | `ReactNode` | required | Twin Data zone content |

#### Usage

```tsx
<BentoGrid
  director={<Director {...directorProps} />}
  canvas={<Canvas {...canvasProps} />}
  gauge={<ComplianceGauge {...gaugeProps} />}
  context={<ContextDeck {...contextProps} />}
  twin={<TwinData {...twinProps} />}
/>
```

#### Grid Layout

Desktop (≥768px):
```
┌─────────┬───────────────┬─────────┐
│ Director│               │  Gauge  │
│         │    Canvas     ├─────────┤
│         │               │  Twin   │
├─────────┤               │  Data   │
│ Context │               │         │
└─────────┴───────────────┴─────────┘
```

Mobile (<768px):
```
┌─────────────┐
│   Director  │
├─────────────┤
│   Canvas    │
├─────────────┤
│    Gauge    │
├─────────────┤
│  Twin Data  │
├─────────────┤
│   Context   │
└─────────────┘
```

---

## Accessibility

All components follow WCAG AA guidelines:

- Keyboard navigation support
- ARIA labels on interactive elements
- Focus indicators (2px blue outline)
- Color contrast ratios ≥4.5:1
- Reduced motion support via `prefers-reduced-motion`
- Screen reader announcements via `aria-live` regions

## Performance

- Lazy loading for VisX chart components
- React.memo() on expensive components
- CSS-only animations where possible
- Debounced input handlers (300ms)
