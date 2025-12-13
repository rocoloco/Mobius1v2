# Implementation Plan: Luminous Structuralism Dashboard

## Overview

This implementation plan breaks down the Luminous Structuralism Dashboard redesign into discrete, actionable coding tasks. Each task builds incrementally on previous work, starting with the design system foundation and progressing through component implementation, state management, and testing.

The plan follows a bottom-up approach: design tokens → atomic components → molecular components → organism components → layout → state management → integration → testing.

## Task List

- [x] 1. Set up Luminous design system foundation





  - Create `frontend/src/luminous/` directory structure
  - Implement design token system with colors, typography, and effects
  - Configure Tailwind with custom Luminous tokens
  - _Requirements: 1.1-1.12_


- [x] 1.1 Create design tokens file

  - Create `frontend/src/luminous/tokens.ts`
  - Define luminousTokens object with colors (void, glass, border, accent, compliance, text)
  - Define typography (fontFamily, tracking)
  - Define effects (glow, backdropBlur)
  - Define animation (duration, easing)
  - Export tokens and utility functions
  - _Requirements: 1.1-1.12_

- [x] 1.2 Configure Tailwind with Luminous tokens


  - Update `frontend/tailwind.config.ts`
  - Extend theme with Luminous colors
  - Add custom utilities for glassmorphism
  - Add custom utilities for gradient text
  - Configure backdrop-filter plugin
  - _Requirements: 1.1-1.12_

- [x] 1.3 Create atomic component directory structure


  - Create `frontend/src/luminous/components/atoms/` directory
  - Create `frontend/src/luminous/components/molecules/` directory
  - Create `frontend/src/luminous/components/organisms/` directory
  - Create `frontend/src/luminous/layouts/` directory
  - Create index files for exports
  - _Requirements: All_

- [x] 2. Build atomic components





  - Implement GlassPanel, GradientText, ConnectionPulse, MonoText
  - Each component should be minimal, reusable, and follow Luminous design tokens
  - _Requirements: 1.1-1.12, 2.1-2.10, 12.1-12.7_

- [x] 2.1 Implement GlassPanel component


  - Create `frontend/src/luminous/components/atoms/GlassPanel.tsx`
  - Accept children, className, and glow props
  - Apply glassmorphism styling: `bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl`
  - Conditionally apply glow effect when glow prop is true
  - _Requirements: 1.2, 1.3, 12.2_

- [x] 2.2 Write property test for GlassPanel glow effect






  - **Property 1 (Partial): GlassPanel applies glow when prop is true**
  - **Validates: Requirements 1.12, 12.3**

- [x] 2.3 Implement GradientText component


  - Create `frontend/src/luminous/components/atoms/GradientText.tsx`
  - Accept children and animate props
  - Apply gradient background with text clipping
  - Implement CSS animation for gradient position when animate is true
  - Use accent gradient from tokens
  - _Requirements: 1.4, 12.4_

- [x] 2.4 Implement ConnectionPulse component


  - Create `frontend/src/luminous/components/atoms/ConnectionPulse.tsx`
  - Accept status prop: 'connected' | 'disconnected' | 'connecting'
  - Render colored dot: green for connected, red for disconnected, yellow for connecting
  - Apply pulse animation for connected and connecting states
  - Add data-testid for testing
  - _Requirements: 2.5, 2.6_

- [x] 2.5 Write property test for ConnectionPulse color mapping






  - **Property 1: Connection Status Indicator Correctness**
  - **Validates: Requirements 2.5, 2.6**

- [x] 2.6 Implement MonoText component


  - Create `frontend/src/luminous/components/atoms/MonoText.tsx`
  - Accept children and className props
  - Apply monospace font from tokens (JetBrains Mono)
  - Use high contrast text color
  - _Requirements: 1.9, 1.11, 8.9_


- [x] 3. Build AppShell organism





  - Implement fixed header with logo, utilities, and connection status
  - This is the top-level layout wrapper for the entire dashboard
  - _Requirements: 2.1-2.10_

- [x] 3.1 Implement AppShell component





  - Create `frontend/src/luminous/components/organisms/AppShell.tsx`
  - Render fixed header with height 64px
  - Apply glassmorphism styling with bottom border
  - Position Mobius logo and "Brand Governance Engine" text on left
  - Position ConnectionPulse, Settings icon, and user avatar on right
  - Render children with pt-16 offset
  - _Requirements: 2.1-2.10_

- [x] 3.2 Write unit test for AppShell layout





  - Test that header is rendered with correct height
  - Test that logo and branding text are present
  - Test that utilities section contains connection pulse, settings, and avatar
  - _Requirements: 2.1, 2.3_

- [x] 4. Build BentoGrid layout




  - Implement CSS Grid layout with five zones
  - Handle responsive breakpoints for mobile
  - _Requirements: 3.1-3.9_

- [x] 4.1 Implement BentoGrid layout component


  - Create `frontend/src/luminous/layouts/BentoGrid.tsx`
  - Implement CSS Grid with calc(100vh - 64px) height
  - Define grid template areas for five zones
  - Accept zone components as props (director, canvas, gauge, context, twin)
  - Apply responsive styles: single column on mobile (<768px)
  - _Requirements: 3.1-3.9_

- [x] 4.2 Write unit test for BentoGrid responsive behavior





  - Test that grid uses correct template areas on desktop
  - Test that grid collapses to single column on mobile
  - _Requirements: 3.8, 3.9, 11.1_


- [x] 5. Build molecular components for chat



  - Implement ChatMessage component for Director
  - _Requirements: 4.1-4.3_

- [x] 5.1 Implement ChatMessage component

  - Create `frontend/src/luminous/components/molecules/ChatMessage.tsx`
  - Accept role, content, and timestamp props
  - Align user messages to right with purple tint background
  - Align system messages to left with neutral glass background
  - Display timestamp in muted text
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 5.2 Write property test for ChatMessage alignment






  - **Property 2: Chat Message Rendering Completeness**
  - **Validates: Requirements 4.1, 4.2**


- [x] 6. Build Director organism



  - Implement multi-turn chat interface with input field and status indicator
  - _Requirements: 4.1-4.11_

- [x] 6.1 Implement Director component


  - Create `frontend/src/luminous/components/organisms/Director.tsx`
  - Render scrollable chat history using ChatMessage components
  - Render Quick Action chips above input field
  - Render floating input field at bottom with character counter
  - Display GradientText status indicator when generating
  - Implement 1000 character limit on input
  - Trigger onSubmit callback when user sends message
  - _Requirements: 4.1-4.11_

- [ ]* 6.2 Write property test for input character limit
  - **Property 3: Input Character Limit Enforcement**
  - **Validates: Requirements 4.7**

- [ ]* 6.3 Write property test for optimistic message update
  - **Property 4: Optimistic Message Update**
  - **Validates: Requirements 4.11**


- [x] 7. Build molecular components for violations and constraints




  - Implement ViolationItem and ConstraintCard components
  - _Requirements: 6.7-6.9, 7.1-7.8_


- [x] 7.1 Implement ViolationItem component

  - Create `frontend/src/luminous/components/molecules/ViolationItem.tsx`
  - Accept violation object and onClick callback
  - Render severity icon (critical/warning/info)
  - Render violation message
  - Apply hover effect
  - Add data-testid and data-severity attributes
  - _Requirements: 6.7, 6.8_

- [x] 7.2 Implement ConstraintCard component


  - Create `frontend/src/luminous/components/molecules/ConstraintCard.tsx`
  - Accept type, label, icon, active, and metadata props
  - Render pill-shaped card with icon on left
  - Render label in center
  - Conditionally render radar chart for voice constraints
  - Apply highlight styling when active is true
  - _Requirements: 7.1-7.8_


- [x] 8. Build ComplianceGauge organism



  - Implement radial donut chart with VisX and violation list
  - _Requirements: 6.1-6.10_

- [x] 8.1 Implement ComplianceGauge component


  - Create `frontend/src/luminous/components/organisms/ComplianceGauge.tsx`
  - Use VisX Arc component to render donut chart
  - Display score value in center of chart
  - Color gauge based on score thresholds (≥95% green, 70-95% amber, <70% red)
  - Render scrollable violation list below gauge
  - Group violations by severity (Critical, Warning, Info)
  - Trigger onViolationClick callback when violation is clicked
  - Add data-testid="compliance-gauge"
  - _Requirements: 6.1-6.10_

- [ ]* 8.2 Write property test for gauge color mapping
  - **Property 9: Compliance Gauge Color Mapping**
  - **Validates: Requirements 6.3, 6.4, 6.5**

- [ ]* 8.3 Write property test for violation severity grouping
  - **Property 10: Violation Severity Grouping**
  - **Validates: Requirements 6.9**

- [x] 9. Build ContextDeck organism





  - Implement constraint visualization panel
  - _Requirements: 7.1-7.8_

- [x] 9.1 Implement ContextDeck component


  - Create `frontend/src/luminous/components/organisms/ContextDeck.tsx`
  - Accept brandId and activeConstraints props
  - Fetch brand graph data from `/brands/{id}/graph` on mount
  - Render vertical stack of ConstraintCard components
  - Parse constraints from brand graph (channel, negative, voice)
  - Highlight cards when corresponding rule is in violations
  - _Requirements: 7.1-7.8_

- [ ]* 9.2 Write property test for constraint highlighting
  - **Property 11: Constraint Highlighting on Violation**
  - **Validates: Requirements 7.7**


- [x] 10. Build molecular components for Twin Data



  - Implement ColorSwatch component
  - _Requirements: 8.1-8.9_


- [x] 10.1 Implement ColorSwatch component






  - Create `frontend/src/luminous/components/molecules/ColorSwatch.tsx`
  - Accept detected, brand, distance, and pass props
  - Render split pill: left half shows detected color, right half shows brand color
  - Display hex codes using MonoText
  - Show distance metric in tooltip
  - _Requirements: 8.3, 8.4, 8.5_

- [ ]* 10.2 Write property test for color distance tooltip
  - **Property 12: Color Distance Tooltip Display**
  - **Validates: Requirements 8.5**

- [x] 11. Build TwinData organism




  - Implement visual token inspector panel
  - _Requirements: 8.1-8.9_

- [x] 11.1 Implement TwinData component


  - Create `frontend/src/luminous/components/organisms/TwinData.tsx`
  - Accept detectedColors, brandColors, and detectedFonts props
  - Render "Compressed Digital Twin" header
  - Render color swatches using ColorSwatch components
  - Render font detection results with compliance status
  - Use MonoText for hex codes
  - _Requirements: 8.1-8.9_

- [ ]* 11.2 Write property test for font compliance status
  - **Property 13: Font Compliance Status Display**
  - **Validates: Requirements 8.8**


- [x] 12. Build molecular components for Canvas




  - Implement VersionThumbnail and BoundingBox components
  - _Requirements: 5.1-5.13_

- [x] 12.1 Implement VersionThumbnail component


  - Create `frontend/src/luminous/components/molecules/VersionThumbnail.tsx`
  - Accept imageUrl, score, timestamp, active, and onClick props
  - Render thumbnail image with border
  - Display score badge overlay
  - Apply active styling when active is true
  - Trigger onClick callback when clicked
  - _Requirements: 5.9, 5.13_




- [x] 12.2 Implement BoundingBox component



  - Create `frontend/src/luminous/components/molecules/BoundingBox.tsx`
  - Accept x, y, width, height, severity, label, and highlighted props
  - Render absolutely positioned div overlay
  - Apply dashed border: red for critical, amber for warning
  - Attach label tag to box
  - Apply highlight styling when highlighted is true
  - _Requirements: 5.4, 5.5, 5.6, 5.7, 5.12_

- [x] 13. Build Canvas organism





  - Implement image viewport with bounding boxes and version scrubber
  - _Requirements: 5.1-5.13_

- [x] 13.1 Implement Canvas component


  - Create `frontend/src/luminous/components/organisms/Canvas.tsx`
  - Accept imageUrl, violations, versions, currentVersion, complianceScore, status, onVersionChange, onAcceptCorrection props
  - Render image with object-contain sizing
  - Render skeleton loader when status is 'generating'
  - Render "Scanning Compliance..." overlay when status is 'auditing'
  - Render BoundingBox components for each violation
  - Render Version Scrubber timeline at bottom
  - Conditionally render action button based on compliance score
  - _Requirements: 5.1-5.13_

- [ ]* 13.2 Write property test for bounding box rendering
  - **Property 5: Bounding Box Rendering Completeness**
  - **Validates: Requirements 5.4**

- [ ]* 13.3 Write property test for conditional action button
  - **Property 6: Conditional Action Button Display**
  - **Validates: Requirements 5.10, 5.11**

- [ ]* 13.4 Write property test for version history navigation
  - **Property 8: Version History Navigation**
  - **Validates: Requirements 5.13, 10.7**

- [x] 14. Visual Checkpoint - Review atomic and molecular components





  - Create a simple demo page showcasing all atomic and molecular components
  - Display GlassPanel, GradientText, ConnectionPulse, MonoText in isolation
  - Display ChatMessage, ViolationItem, ConstraintCard, ColorSwatch, VersionThumbnail examples
  - Run dev server for visual review
  - **PAUSE FOR USER FEEDBACK** - User should review visual design before proceeding
  - _Requirements: 1.1-1.12, 12.1-12.7_

- [x] 14.1 Checkpoint - Ensure all component tests pass


  - Ensure all tests pass, ask the user if questions arise.

- [x] 15. Implement state management with DashboardContext




  - Create context provider with Supabase Realtime integration
  - _Requirements: 9.1-9.10, 10.1-10.7_

- [x] 15.1 Create useSupabaseRealtime hook


  - Create `frontend/src/hooks/useSupabaseRealtime.ts`
  - Accept jobId and onUpdate callback
  - Subscribe to Supabase Realtime channel for job updates
  - Call onUpdate when job status changes
  - Unsubscribe on cleanup
  - _Requirements: 9.1-9.10_

- [x] 15.2 Create useJobStatus hook


  - Create `frontend/src/hooks/useJobStatus.ts`
  - Accept jobId
  - Use useSupabaseRealtime for real-time updates
  - Implement polling fallback if Realtime fails
  - Return status, error, and isPolling
  - _Requirements: 9.1-9.10_

- [ ]* 15.3 Write property test for WebSocket fallback
  - **Property 15: WebSocket Fallback Behavior**
  - **Validates: Requirements 9.10**

- [x] 15.4 Create useSessionHistory hook


  - Create `frontend/src/hooks/useSessionHistory.ts`
  - Accept sessionId
  - Fetch session history from `/sessions/{id}/history`
  - Manage versions array and currentIndex
  - Provide loadVersion and addVersion functions
  - _Requirements: 10.1-10.7_

- [ ]* 15.5 Write property test for version history growth
  - **Property 17: Version History Growth**
  - **Validates: Requirements 10.3**

- [x] 15.6 Create DashboardContext


  - Create `frontend/src/context/DashboardContext.tsx`
  - Define DashboardContextValue interface
  - Implement DashboardProvider with state management
  - Use useSupabaseRealtime for job updates
  - Use useSessionHistory for version management
  - Implement submitPrompt action with optimistic updates
  - Implement loadVersion, acceptCorrection, retryGeneration actions
  - _Requirements: 9.1-9.10, 10.1-10.7_

- [ ]* 15.7 Write property test for session ID persistence
  - **Property 16: Session ID Persistence**
  - **Validates: Requirements 10.2**

- [x] 16. Visual Checkpoint - Review organism components





  - Create demo pages for each organism component in isolation
  - Test Director chat interface with mock data
  - Test Canvas with sample images and bounding boxes
  - Test ComplianceGauge with different score values
  - Test ContextDeck with sample constraints
  - Test TwinData with sample color/font data
  - Run dev server for visual review
  - **PAUSE FOR USER FEEDBACK** - User should review organisms before integration
  - _Requirements: 4.1-8.9_

- [x] 17. Build main Dashboard view





  - Integrate all organisms into BentoGrid layout
  - Connect to DashboardContext
  - _Requirements: All_


- [x] 17.1 Implement Dashboard view

  - Create `frontend/src/views/Dashboard.tsx`
  - Wrap in DashboardProvider
  - Render AppShell with connection status
  - Render BentoGrid with all five zone components
  - Pass context values to each organism
  - Handle violation click to highlight bounding box
  - _Requirements: All_

- [ ]* 17.2 Write property test for violation click highlighting
  - **Property 7: Violation Click Highlighting**
  - **Validates: Requirements 5.12, 6.8**

- [x] 18. Implement error handling





  - Add error states and user-friendly messaging
  - _Requirements: 13.1-13.9_

- [x] 18.1 Add error handling to Director


  - Display error messages in chat when generation fails
  - Provide "Retry" button
  - Log detailed errors to console
  - _Requirements: 13.3, 13.8_

- [ ]* 18.2 Write property test for error message display
  - **Property 19: Error Message Display on Failure**
  - **Validates: Requirements 13.3**

- [x] 18.3 Add error handling to Canvas


  - Display grey Compliance Gauge when audit unavailable
  - Show warning toast when audit fails but image succeeds
  - Allow download with warning
  - _Requirements: 13.4, 13.5, 13.6_

- [x] 18.4 Implement retry mechanism with exponential backoff


  - Create utility function for exponential backoff
  - Apply to failed API requests
  - _Requirements: 13.7_

- [ ]* 18.5 Write property test for exponential backoff timing
  - **Property 20: Exponential Backoff Retry Timing**
  - **Validates: Requirements 13.7**

- [x] 19. Implement accessibility features





  - Add ARIA labels, live regions, and keyboard navigation
  - _Requirements: 14.1-14.8_

- [x] 19.1 Add ARIA labels to icon buttons


  - Add aria-label to all icon-only buttons (Settings, Profile, Quick Actions)
  - _Requirements: 14.2_

- [ ]* 19.2 Write property test for ARIA label completeness
  - **Property 21: ARIA Label Completeness**
  - **Validates: Requirements 14.2**

- [x] 19.3 Add aria-live regions for state changes


  - Add aria-live="polite" region for status updates
  - Add aria-live="assertive" region for errors
  - Update regions when state changes
  - _Requirements: 14.5_

- [ ]* 19.4 Write property test for aria-live updates
  - **Property 22: Aria-Live Region Updates**
  - **Validates: Requirements 14.5**

- [x] 19.5 Implement keyboard navigation


  - Ensure all interactive elements are keyboard accessible
  - Add visible focus indicators (2px outline in accent color)
  - Make violation list navigable with arrow keys
  - _Requirements: 14.1, 14.3, 14.8_

- [x] 19.6 Add reduced motion support


  - Detect prefers-reduced-motion media query
  - Disable animations when user prefers reduced motion
  - _Requirements: 14.7_

- [x] 19.7 Verify color contrast ratios


  - Audit all text elements for WCAG AA compliance (4.5:1)
  - Adjust colors if needed
  - _Requirements: 14.6_

- [ ]* 19.8 Write property test for color contrast compliance
  - **Property 23: Color Contrast Compliance**
  - **Validates: Requirements 14.6**

- [x] 20. Implement responsive mobile layout




  - Ensure dashboard works on mobile devices
  - _Requirements: 11.1-11.7_

- [x] 20.1 Add mobile-specific styles to BentoGrid


  - Collapse to single column on <768px
  - Stack zones in correct order
  - Adjust zone heights for mobile
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [x] 20.2 Make Version Scrubber mobile-friendly


  - Enable horizontal swipe gesture
  - Adjust thumbnail sizes for mobile
  - _Requirements: 11.5, 11.7_

- [x] 20.3 Ensure touch targets are 44x44px minimum


  - Audit all interactive elements
  - Increase size if needed
  - _Requirements: 11.6_

- [x] 20.4 Write property test for touch target minimum size





  - **Property 18: Touch Target Minimum Size**
  - **Validates: Requirements 11.6**

- [x] 22. Add animations and polish





  - Implement smooth transitions and micro-interactions
  - _Requirements: 12.1-12.7_

- [x] 22.1 Add CSS animations


  - Implement scanning laser animation for auditing state
  - Implement pulse animation for connection status
  - Implement gradient animation for AI status text
  - Use CSS-only (no JavaScript)
  - _Requirements: 12.5_

- [x] 22.2 Add Framer Motion transitions


  - Add slide-up animation for action button
  - Add fade-in animation for bounding boxes
  - Add layout transitions for zone resizing
  - _Requirements: 12.6_

- [x] 22.3 Add hover effects


  - Add scale and glow effects to interactive elements
  - Use 300ms ease-in-out transitions
  - _Requirements: 12.7_

- [x] 22.4 Add confetti micro-interaction


  - Trigger confetti when score reaches ≥95%
  - Use lightweight confetti library or CSS particles
  - _Requirements: 6.10_

- [x] 21. Visual Checkpoint - Review complete dashboard layout




  - Run dev server with complete dashboard implementation
  - Test all five Bento Grid zones with real data
  - Verify glassmorphism effects, animations, and interactions
  - Test responsive behavior on different screen sizes
  - **PAUSE FOR USER FEEDBACK** - User should review complete layout before optimization
  - _Requirements: All_

- [x] 21.1 Final checkpoint - Ensure all tests pass


  - Ensure all tests pass, ask the user if questions arise.

- [x] 23. Integration testing





  - Write end-to-end tests for key workflows
  - _Requirements: All_

- [x] 23.1 Write integration test for generation workflow
  - Test: User submits prompt → sees generating state → sees completed image with audit
  - Use Playwright
  - _Requirements: 4.1-4.11, 5.1-5.13, 9.1-9.10_

- [x] 23.2 Write integration test for violation interaction
  - Test: User clicks violation → corresponding bounding box highlights
  - Use Playwright
  - _Requirements: 5.12, 6.8_

- [x] 23.3 Write integration test for version navigation
  - Test: User clicks version thumbnail → previous version loads
  - Use Playwright
  - _Requirements: 5.13, 10.7_

- [x] 23.4 Write integration test for multi-turn session
  - Test: User submits multiple prompts → session history grows → can navigate versions
  - Use Playwright
  - _Requirements: 10.1-10.7_

- [x] 24. Performance optimization





  - Optimize bundle size and runtime performance
  - _Requirements: All_


- [x] 24.1 Implement code splitting

  - Lazy load VisX chart components
  - Split dashboard into separate chunk
  - _Requirements: All_


- [x] 24.2 Add memoization

  - Use React.memo() for Canvas and ComplianceGauge
  - Use useMemo() for expensive calculations
  - Use useCallback() for event handlers
  - _Requirements: All_


- [x] 24.3 Optimize animations

  - Ensure CSS transforms are GPU-accelerated
  - Debounce input changes (300ms)
  - Debounce window resize events
  - _Requirements: 12.1-12.7_


- [x] 25.1 Run accessibility audit
  - Use axe-core to scan for accessibility issues
  - Fix any violations
  - _Requirements: 14.1-14.8_


- [x] 25.2 Run visual regression tests
  - Use Playwright to capture screenshots
  - Compare against baseline
  - Fix any visual regressions
  - _Requirements: 12.1-12.7_


- [x] 25.4 Test on mobile devices
  - Test on iOS and Android
  - Fix any mobile-specific issues
  - _Requirements: 11.1-11.7_

- [x] 27. Documentation and deployment preparation





  - Document component usage and deployment process

  - _Requirements: All_

- [x] 27.1 Write component documentation

  - Document all public component APIs
  - Add usage examples
  - Create Storybook stories
  - _Requirements: All_


- [x] 27.2 Update README

  - Document new design system
  - Add setup instructions
  - Add development guidelines
  - _Requirements: All_


- [x] 27.3 Prepare deployment configuration

  - Set up environment variables
  - Configure build optimizations
  - Test production build
  - _Requirements: All_

- [x] 26. Remove old Industrial design system



  - Complete replacement of UI/UX with Luminous design system

  - _Requirements: All_


- [x] 26.1 Remove Industrial design system files
  - Delete `frontend/src/design-system/` directory and all contents
  - Remove Industrial token imports from Tailwind config
  - Remove Industrial utilities and plugins from Tailwind config

  - _Requirements: All_

- [x] 26.2 Remove Industrial components
  - Delete all Industrial component files that are no longer used
  - Search for and remove any remaining Industrial component imports
  - Removed: monitoring/, layout/, persona/, physical/ folders
  - Removed: Workbench.tsx, Onboarding.tsx views
  - _Requirements: All_

- [x] 26.3 Update imports and references
  - Search codebase for any remaining references to Industrial design system
  - Update all imports to use Luminous components
  - Remove any Industrial-specific CSS classes from components
  - Simplified App.tsx to only use Dashboard
  - _Requirements: All_

- [x] 26.4 Clean up Tailwind configuration
  - Tailwind config already uses only Luminous tokens
  - Removed Industrial-specific comments from CSS
  - _Requirements: All_

- [x] 26.5 Verify complete removal
  - Run build to ensure no broken imports ✓
  - Search for any remaining "industrial" references in codebase
  - Test that application runs without Industrial design system ✓
  - _Requirements: All_
