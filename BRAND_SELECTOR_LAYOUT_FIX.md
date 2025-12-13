# Brand Selector Layout Fix

## Issue
The brand text was getting cut off in the single-row layout, especially with longer brand names and additional metadata (colors, rules, archetype).

## Solution
Updated the BrandSelectorButton to use a two-row layout for better space utilization and readability.

## Layout Changes

### Before (Single Row - Text Cut Off)
```
┌─────────────────────────────────────────────────────────────┐
│ [✨] Very Long Brand Name Here  4 colors·9 rules  The Inn... [▼] │
└─────────────────────────────────────────────────────────────┘
```
**Problems:**
- Brand name truncated
- Archetype cut off
- Cramped appearance
- Poor readability

### After (Two Row - Full Visibility)
```
┌─────────────────────────────────────────────────────────────┐
│ [✨] Very Long Brand Name Here                          [▼] │
│      4 colors · 9 rules  The Innovator                     │
└─────────────────────────────────────────────────────────────┘
```
**Benefits:**
- Full brand name visible
- All metadata displayed
- Better visual hierarchy
- Improved readability

## Implementation Details

### Two-Row Structure
```tsx
<button className="flex flex-col gap-1 ...">
  {/* Top row: Brand name with icon and chevron */}
  <div className="flex items-center gap-2 w-full">
    <Sparkles /> 
    <span className="truncate flex-1">{brandGraph.name}</span>
    <ChevronDown />
  </div>
  
  {/* Bottom row: Details */}
  <div className="flex items-center gap-2 w-full pl-6">
    <span>{colorCount} colors · {ruleCount} rules</span>
    <span>{archetype}</span>
  </div>
</button>
```

### Visual Hierarchy
1. **Top Row**: Brand name (most important) with visual indicators
2. **Bottom Row**: Metadata details with proper indentation
3. **Icon Alignment**: Sparkles icon on top row, details indented below
4. **Chevron Position**: Consistently positioned on top row

### Responsive Behavior
- **Desktop**: Shows all metadata including archetype
- **Mobile**: Hides archetype on smaller screens (`hidden md:inline`)
- **Truncation**: Brand name can still truncate if extremely long, but much more space available

### Consistent Padding
- Updated all states to use `padding: '6px 8px'` for consistent height
- Maintains proper touch targets and visual balance

## States Handled

### 1. Loading State
```
┌─────────────────────────────────────────────────────────────┐
│ [⟳] Loading brands...                                      │
└─────────────────────────────────────────────────────────────┘
```
- Single row (appropriate for loading message)
- Consistent padding with other states

### 2. Select Brand State
```
┌─────────────────────────────────────────────────────────────┐
│ [✨] Select Brand                                      [▼] │
└─────────────────────────────────────────────────────────────┘
```
- Single row (simple message)
- Pulsing amber highlight
- Clear call-to-action

### 3. Brand Selected State
```
┌─────────────────────────────────────────────────────────────┐
│ [✨] Acme Corporation                                  [▼] │
│      4 colors · 9 rules  The Innovator                     │
└─────────────────────────────────────────────────────────────┘
```
- Two rows for full information display
- Proper visual hierarchy
- All metadata visible

## Design System Compliance

### Spacing
- **Gap**: 1 unit between rows (`gap-1`)
- **Padding**: Consistent 6px vertical, 8px horizontal
- **Indentation**: 6 units left padding for details row (`pl-6`)

### Typography
- **Brand Name**: `text-sm font-medium` (primary information)
- **Details**: `text-[11px] font-mono` (secondary information)
- **Colors**: Maintains Luminous token consistency

### Interactions
- **Hover**: Subtle background change
- **Focus**: Purple ring for accessibility
- **Animation**: Smooth transitions maintained

## Accessibility Improvements

- **Better Readability**: Full text visible reduces cognitive load
- **Clear Hierarchy**: Visual structure helps screen readers
- **Consistent Layout**: Predictable structure for navigation
- **Proper Labeling**: ARIA labels remain descriptive

## Files Modified

1. `frontend/src/luminous/components/molecules/BrandSelectorButton.tsx`
   - Updated brand selected state to two-row layout
   - Consistent padding across all states
   - Improved visual hierarchy

## Testing

The layout fix maintains all existing functionality while improving:
- **Visual Appeal**: Better use of available space
- **Information Density**: More content visible without clutter
- **User Experience**: Easier to read and understand brand information
- **Responsive Design**: Works well across different screen sizes

This fix ensures that agency users with longer brand names and detailed metadata can see all relevant information at a glance, improving the overall brand selection experience.