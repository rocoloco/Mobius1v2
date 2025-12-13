# Organism Component Demos

This directory contains interactive demo pages for all organism components in the Luminous design system. These demos serve as a visual checkpoint (Task 16) before integrating components into the full dashboard.

## Accessing the Demos

### Via Dev Server

1. Start the development server:
   ```bash
   cd frontend
   npm run dev
   ```

2. Open your browser to the local URL (typically http://localhost:5174/)

3. Click the **"ORGANISMS"** button in the header (yellow button)

4. You'll see the Organism Demo Index with cards for each component

### Demo Pages

The following organism component demos are available:

#### 1. Director Demo
**Requirements:** 4.1-4.11

Multi-turn chat interface for AI prompt interaction featuring:
- Scrollable chat history with role-based alignment
- Quick Action chips for common prompts
- Floating input field with character counter (1000 max)
- Real-time generation status indicator
- Interactive controls to toggle generating state

**Test Features:**
- Type messages and submit with Enter (Shift+Enter for multi-line)
- Click Quick Action chips to populate input
- Watch character counter change color near limit
- Toggle generating state to see AI status indicator
- Observe message alignment (user right, system left)

#### 2. Canvas Demo
**Requirements:** 5.1-5.13

Image viewport with bounding boxes and version scrubber featuring:
- Image display with object-contain sizing
- Skeleton loader for generating state
- "Scanning Compliance..." overlay for auditing state
- Bounding boxes for violations (red for critical, amber for warning)
- Version scrubber timeline with thumbnails
- Conditional action buttons based on compliance score

**Test Features:**
- Switch between generating/auditing/complete/error states
- Click violations to highlight corresponding bounding boxes
- Navigate version history via thumbnails
- Observe conditional action button display
- Test different compliance score thresholds

#### 3. Compliance Gauge Demo
**Requirements:** 6.1-6.10

Radial donut chart with violation list featuring:
- SVG donut chart with color-coded thresholds
- Score display in center (0-100)
- Scrollable violation list grouped by severity
- Clickable violations that trigger focus events

**Test Features:**
- Adjust score slider to see color changes:
  - ≥95%: Green (#10B981)
  - 70-95%: Amber (#F59E0B)
  - <70%: Red (#EF4444)
- Click violations to trigger focus event
- Observe severity grouping (Critical → Warning → Info)
- Test empty state with no violations

#### 4. Context Deck Demo
**Requirements:** 7.1-7.8

Constraint visualization panel featuring:
- Channel constraints (platform-specific rules)
- Negative constraints (forbidden elements)
- Voice constraints (brand voice vectors with radar chart)
- Pill-shaped constraint cards

**Test Features:**
- Toggle constraints to see highlight effect
- Scroll through constraint list
- Observe different constraint types and icons
- View radar chart on voice constraint
- Test active/inactive states

#### 5. Twin Data Demo
**Requirements:** 8.1-8.9

Visual token inspector featuring:
- Color swatches (split pill design)
- Detected vs. brand color comparison
- Color distance metrics with pass/fail indicators
- Font detection with compliance status
- Monospace formatting for hex codes

**Test Features:**
- Switch between full/partial/empty data scenarios
- Hover over color swatches for distance tooltip
- Observe split pill design (detected | brand)
- Check font compliance badges (Allowed/Forbidden)
- Test empty states

## Demo Architecture

### File Structure

```
__tests__/
├── index.demo.tsx           # Master demo index page
├── Director.demo.tsx        # Director component demo
├── Canvas.demo.tsx          # Canvas component demo
├── ComplianceGauge.demo.tsx # Compliance Gauge demo
├── ContextDeck.demo.tsx     # Context Deck demo
├── TwinData.demo.tsx        # Twin Data demo
└── README.md               # This file
```

### Navigation

The demo index provides:
- Card-based navigation to each component demo
- Connection status demo (toggle connected/connecting/disconnected)
- Component status overview
- Review instructions and checklist

Each individual demo includes:
- Back button to return to index
- Interactive controls to manipulate component state
- Feature checklist for testing
- Side panels with additional information

## Review Checklist

When reviewing these demos, verify:

- [ ] Glassmorphism effects render correctly
- [ ] Component interactions work as expected
- [ ] Color schemes match Luminous design tokens
- [ ] Typography and spacing are consistent
- [ ] Animations and transitions are smooth (300ms ease-in-out)
- [ ] Components handle different data states properly
- [ ] Empty states display appropriate messages
- [ ] Hover effects work (scale 1.02, glow increase)
- [ ] Focus indicators are visible (2px outline)
- [ ] Components are responsive to container size

## Design System Compliance

All demos follow the Luminous design system:

### Colors
- Background: `#101012` (Deep Charcoal)
- Glass: `rgba(255, 255, 255, 0.03)` with `backdrop-blur(12px)`
- Borders: `rgba(255, 255, 255, 0.08)`
- Accent Gradient: `linear-gradient(135deg, #7C3AED 0%, #2563EB 100%)`

### Typography
- Sans: Inter or Geist Sans (400, 600, 700)
- Mono: JetBrains Mono or Fira Code
- Body Text: `#94A3B8` (Slate-400)
- High Contrast: `#F1F5F9`

### Effects
- Glow: `0 0 20px rgba(37, 99, 235, 0.15)`
- Backdrop Blur: `blur(12px)`
- Transitions: `300ms ease-in-out`

## Next Steps

After reviewing all organism demos:

1. Provide feedback on any visual or interaction issues
2. Confirm all components meet design requirements
3. Proceed to Task 17: Dashboard Integration
   - Integrate organisms into BentoGrid layout
   - Connect to DashboardContext
   - Wire up real-time state management

## Notes

- These demos use mock data and simulated interactions
- Real API integration happens in Task 17
- Supabase Realtime will be integrated in the full dashboard
- Some features (like actual image generation) are simulated

## Troubleshooting

### Dev Server Issues

If the dev server doesn't start:
```bash
cd frontend
npm install
npm run dev
```

### Missing Components

If components don't render, check:
1. All organism components are implemented
2. Molecular and atomic components are available
3. Design tokens are properly configured
4. Tailwind config includes Luminous tokens

### Styling Issues

If glassmorphism doesn't appear:
1. Verify backdrop-filter is supported in your browser
2. Check Tailwind config includes backdrop-blur plugin
3. Ensure luminousTokens are imported correctly
