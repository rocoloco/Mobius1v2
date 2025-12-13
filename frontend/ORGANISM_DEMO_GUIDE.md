# Organism Component Demo Guide

## Quick Start

The organism component demos are now ready for visual review! 🎉

### Access the Demos

1. **Dev server is running** at: http://localhost:5174/

2. **Click the yellow "ORGANISMS" button** in the header

3. **Navigate through each demo** using the card-based interface

## What to Review

### 1. Director (Chat Interface)
- ✅ Chat message alignment (user right, system left)
- ✅ Quick Action chips functionality
- ✅ Character counter (turns yellow at 900, red at 1000)
- ✅ "Gemini 3 Pro - Thinking..." animated gradient text
- ✅ Submit button glow effect
- ✅ Auto-scroll to latest message

### 2. Canvas (Image Viewport)
- ✅ Skeleton loader animation during generation
- ✅ "Scanning Compliance..." overlay during audit
- ✅ Bounding boxes (red for critical, amber for warning)
- ✅ Version scrubber with thumbnails
- ✅ Conditional action buttons based on score
- ✅ Violation highlighting on click

### 3. Compliance Gauge (Radial Chart)
- ✅ Color-coded donut chart (green ≥95%, amber 70-95%, red <70%)
- ✅ Score display in center
- ✅ Violation list grouped by severity
- ✅ Clickable violations
- ✅ Smooth color transitions

### 4. Context Deck (Constraints)
- ✅ Channel constraints with platform icons
- ✅ Negative constraints with EyeOff icon
- ✅ Voice constraints with radar chart
- ✅ Pill-shaped card design
- ✅ Active state highlighting

### 5. Twin Data (Token Inspector)
- ✅ Split pill color swatches (detected | brand)
- ✅ Color distance tooltips
- ✅ Font compliance badges
- ✅ Monospace hex code formatting
- ✅ Empty state handling

## Design System Verification

Check that all components follow Luminous design tokens:

### Visual Effects
- [ ] Glassmorphism: `bg-white/5 backdrop-blur-md border border-white/10`
- [ ] Glow effects on active elements
- [ ] Smooth transitions (300ms ease-in-out)
- [ ] Gradient text animations

### Colors
- [ ] Background: Deep charcoal `#101012`
- [ ] Text: Slate-400 `#94A3B8` for body, `#F1F5F9` for high contrast
- [ ] Accent gradient: Purple to blue
- [ ] Compliance colors: Green/Amber/Red thresholds

### Typography
- [ ] Sans-serif: Inter or Geist Sans
- [ ] Monospace: JetBrains Mono for data
- [ ] Consistent font weights (400, 600, 700)

## Interactive Testing

### Director Demo
1. Type a message and press Enter
2. Try Shift+Enter for multi-line
3. Click "Fix Red Violations" quick action
4. Toggle generating state
5. Watch character counter approach limit

### Canvas Demo
1. Switch between generating/auditing/complete states
2. Click violation buttons to highlight bounding boxes
3. Navigate version history
4. Observe action button changes with score

### Compliance Gauge Demo
1. Drag score slider from 0 to 100
2. Watch gauge color change at thresholds
3. Click violations in the list
4. Test empty state (100% score, no violations)

### Context Deck Demo
1. Toggle individual constraints
2. Activate/deactivate all
3. Observe radar chart on voice constraint
4. Scroll through long constraint lists

### Twin Data Demo
1. Switch between full/partial/empty scenarios
2. Hover over color swatches for tooltips
3. Check font compliance badges
4. Verify monospace formatting

## Connection Status Demo

In the header, test the connection pulse indicator:
- **Green dot with pulse**: Connected
- **Yellow dot with pulse**: Connecting
- **Red dot (static)**: Disconnected

## Known Limitations

These are demo pages with mock data:
- No real API calls
- Simulated generation delays
- Placeholder images
- Mock violation data

Real integration happens in Task 17 (Dashboard Integration).

## Feedback Checklist

Please review and provide feedback on:

- [ ] Overall visual consistency
- [ ] Component interactions feel natural
- [ ] Glassmorphism effects are visible and attractive
- [ ] Animations are smooth (not janky)
- [ ] Text is readable with good contrast
- [ ] Components handle edge cases (empty states, long text)
- [ ] Mobile responsiveness (if testing on smaller screens)
- [ ] Any visual bugs or glitches
- [ ] Suggestions for improvements

## Next Steps

After your review:

1. **Provide feedback** on any issues or improvements
2. **Confirm approval** to proceed to Task 17
3. **Task 17** will integrate these organisms into the full BentoGrid dashboard
4. **Real-time state management** will be connected via DashboardContext

## Questions?

If you encounter any issues:
- Check the browser console for errors
- Verify dev server is running (http://localhost:5174/)
- Ensure all dependencies are installed (`npm install`)
- Review the detailed README at `frontend/src/luminous/components/organisms/__tests__/README.md`

---

**Status**: ✅ Task 16 Complete - Ready for User Review

**Dev Server**: 🟢 Running on http://localhost:5174/

**Access**: Click yellow "ORGANISMS" button in header
