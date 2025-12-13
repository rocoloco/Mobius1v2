# Requirements Document: Luminous Structuralism Dashboard (UI v2.5)

## Introduction

The Mobius Brand Governance Engine requires a complete UI redesign to implement a "Bento Grid" dashboard that embodies "Luminous Structuralism" - a design philosophy combining precision engineering, deep dark mode aesthetics, translucent glass layers, and neon data accents. The core principle is that the UI serves as a neutral stage where brand assets are the star, avoiding chromatic interference with generated content.

This redesign replaces the existing industrial component library entirely, preserving only the API client layer and type definitions while rebuilding all UI components from scratch.

## Glossary

- **System**: The Mobius Brand Governance Engine frontend application
- **Director**: The multi-turn chat interface component for AI prompt interaction
- **Canvas**: The central viewport displaying generated images with compliance annotations
- **Compliance Gauge**: The radial chart component showing overall brand compliance scores
- **Context Deck**: The constraint visualization panel showing active brand rules
- **Twin Data**: The panel displaying detected visual tokens (colors, fonts) from analysis
- **Version Scrubber**: The horizontal timeline component showing generation history
- **Bento Grid**: The CSS Grid layout dividing the dashboard into five distinct zones
- **Glassmorphism**: The visual effect using backdrop blur and translucent surfaces
- **Bounding Box**: Visual overlay rectangles indicating compliance violations on the Canvas
- **Session**: A multi-turn generation workflow identified by session_id
- **Job**: A single generation request identified by job_id
- **Supabase Realtime**: The WebSocket-based real-time database subscription system
- **Audit**: The compliance checking process that analyzes generated images

## Requirements

### Requirement 1: Design Token System

**User Story:** As a frontend developer, I want a centralized design token system, so that visual consistency is maintained across all components and future updates are streamlined.

#### Acceptance Criteria

1. THE System SHALL define background color as `#101012` (Deep Charcoal)
2. THE System SHALL define glass panel surfaces as `rgba(255, 255, 255, 0.03)` with `backdrop-filter: blur(12px)`
3. THE System SHALL define subtle borders as `rgba(255, 255, 255, 0.08)`
4. THE System SHALL define primary accent gradient as `linear-gradient(135deg, #7C3AED 0%, #2563EB 100%)`
5. THE System SHALL define compliance pass color as `#10B981` for scores ≥95%
6. THE System SHALL define compliance review color as `#F59E0B` for scores 70-95%
7. THE System SHALL define compliance critical color as `#EF4444` for scores <70%
8. THE System SHALL use Inter or Geist Sans font family with weights 400, 600, and 700
9. THE System SHALL use JetBrains Mono or Fira Code for monospace data display
10. THE System SHALL define body text color as `#94A3B8` (Slate-400)
11. THE System SHALL define high contrast text color as `#F1F5F9`
12. THE System SHALL define glow effect as `box-shadow: 0 0 20px rgba(37, 99, 235, 0.15)`

### Requirement 2: Universal App Shell

**User Story:** As a user, I want a persistent navigation header, so that I can access global utilities and see connection status while working in the dashboard.

#### Acceptance Criteria

1. THE System SHALL render a fixed top navigation bar with height 64px (h-16)
2. THE System SHALL apply glassmorphism styling: `bg-white/5 backdrop-blur-md border-b border-white/10`
3. THE System SHALL position Mobius logo and "Brand Governance Engine" text at left side of header
4. THE System SHALL display connection status indicator as colored dot at right side of header
5. WHEN WebSocket is connected, THE System SHALL display green connection pulse dot
6. WHEN WebSocket is disconnected, THE System SHALL display red connection pulse dot
7. THE System SHALL render Settings icon (cog) in right utilities section
8. THE System SHALL render user profile avatar as circle in right utilities section
9. THE System SHALL offset main content area by 64px (pt-16) to account for fixed header
10. THE System SHALL maintain header visibility during scroll (position: fixed)

### Requirement 3: Bento Grid Layout Architecture

**User Story:** As a user, I want a structured dashboard layout, so that I can simultaneously monitor chat, canvas, compliance, and context information without switching views.

#### Acceptance Criteria

1. THE System SHALL implement a CSS Grid layout spanning calc(100vh - 64px) to account for header
2. THE System SHALL divide the layout into five distinct zones: Director, Context Deck, Canvas, Compliance Gauge, and Twin Data
3. THE System SHALL position Director zone at top-left spanning 2 rows
4. THE System SHALL position Context Deck zone at bottom-left spanning 1 row
5. THE System SHALL position Canvas zone at center spanning 3 rows
6. THE System SHALL position Compliance Gauge zone at top-right spanning 1 row
7. THE System SHALL position Twin Data zone at bottom-right spanning 2 rows
8. WHEN viewport width is below tablet breakpoint, THE System SHALL collapse grid to single-column layout
9. WHEN viewport is mobile, THE System SHALL stack zones in order: Director, Canvas, Compliance Gauge, Twin Data, Context Deck

### Requirement 4: Director Chat Interface

**User Story:** As a user, I want to interact with the AI through a chat interface, so that I can iteratively refine generated brand assets through natural language.

#### Acceptance Criteria

1. THE System SHALL display chat message history in threaded view
2. THE System SHALL align user messages to the right with subtle background tint
3. THE System SHALL align system messages to the left
4. THE System SHALL provide a floating input field at the bottom of the Director zone
5. WHEN the AI is processing, THE System SHALL display "Gemini 3 Pro - Thinking..." with animated gradient text
6. WHEN user types in the input field, THE System SHALL trigger pulse effect on Canvas skeleton loader
7. THE System SHALL enforce a 1000 character limit on prompt input
8. THE System SHALL display Quick Action chips above input: "Fix Red Violations" and "Make it Witty"
9. WHEN user clicks Quick Action chip, THE System SHALL populate input field with corresponding prompt template
10. THE System SHALL load chat history from backend on component mount
11. THE System SHALL optimistically add user messages to chat history before backend confirmation

### Requirement 5: Canvas Image Viewport

**User Story:** As a user, I want to view generated images with compliance annotations, so that I can understand which brand guidelines are violated and where.

#### Acceptance Criteria

1. THE System SHALL display generated image centered with object-contain sizing
2. WHEN image is loading, THE System SHALL display skeleton loader with shimmering gradient
3. WHEN audit is in progress, THE System SHALL overlay "Scanning Compliance..." text with scanning laser animation
4. THE System SHALL render bounding boxes as absolute positioned div overlays
5. THE System SHALL style critical violation bounding boxes with 1px dashed `#EF4444` border
6. THE System SHALL style warning violation bounding boxes with 1px dashed `#F59E0B` border
7. THE System SHALL attach small label tags to bounding boxes displaying violation description
8. THE System SHALL render Version Scrubber as horizontal timeline at bottom of Canvas
9. THE System SHALL display thumbnails in Version Scrubber for all session history
10. WHEN compliance score is 70-95%, THE System SHALL display "Accept Auto-Correction" button with gold glow
11. WHEN compliance score is ≥95%, THE System SHALL display "Download / Export" button as primary action
12. WHEN user clicks violation in Compliance Gauge, THE System SHALL highlight corresponding bounding box and dim others
13. WHEN user clicks thumbnail in Version Scrubber, THE System SHALL load that version's image and audit data

### Requirement 6: Compliance Gauge Visualization

**User Story:** As a user, I want to see overall compliance score at a glance, so that I can quickly triage whether the generated asset needs review or is ready for approval.

#### Acceptance Criteria

1. THE System SHALL render compliance score as SVG radial donut chart
2. THE System SHALL display score value 0-100 in center of donut chart
3. WHEN score is ≥95%, THE System SHALL color gauge `#10B981` (Neon Mint)
4. WHEN score is 70-95%, THE System SHALL color gauge `#F59E0B` (Amber)
5. WHEN score is <70%, THE System SHALL color gauge `#EF4444` (Desaturated Red)
6. THE System SHALL display scrollable violation list below gauge
7. THE System SHALL render each violation with icon (Critical/Warning) and text description
8. WHEN user clicks violation item, THE System SHALL trigger focus effect on corresponding Canvas bounding box
9. THE System SHALL group violations by severity: Critical, Warning, Info
10. WHEN score reaches ≥95%, THE System SHALL trigger confetti micro-interaction

### Requirement 7: Context Deck Constraint Visualization

**User Story:** As a user, I want to see which brand constraints are active, so that I understand the rules governing the current generation context.

#### Acceptance Criteria

1. THE System SHALL display active constraints as vertical stack of pill-shaped cards
2. THE System SHALL fetch constraint data from `/brands/{id}/graph` endpoint on mount
3. THE System SHALL render Channel constraints with platform logo icon (e.g., LinkedIn)
4. THE System SHALL render Negative constraints with EyeOff icon
5. THE System SHALL render Voice constraints with Microphone icon and radar chart mini-visualization
6. THE System SHALL display voice vector values (Formal, Witty, Technical, Urgent) in radar chart
7. THE System SHALL highlight constraint cards when corresponding rule is triggered in audit
8. THE System SHALL render constraints as read-only (no toggle interaction)

### Requirement 8: Twin Data Inspector

**User Story:** As a user, I want to inspect detected visual tokens, so that I can verify which colors and fonts the AI identified in the generated image.

#### Acceptance Criteria

1. THE System SHALL display "Compressed Digital Twin" section header
2. THE System SHALL render color swatches as split pill components
3. THE System SHALL display detected color hex code on left half of split pill
4. THE System SHALL display nearest brand color hex code on right half of split pill
5. THE System SHALL show color distance metric in tooltip (e.g., "Distance: 1.2 (Pass)")
6. THE System SHALL render font detection results as text list
7. THE System SHALL display detected font family and weight (e.g., "Inter-Bold")
8. THE System SHALL indicate font compliance status: "(Allowed)" or "(Forbidden)"
9. THE System SHALL use monospace font (JetBrains Mono) for hex code display

### Requirement 9: Real-Time State Synchronization

**User Story:** As a user, I want the dashboard to update in real-time as generation and audit progress, so that I receive immediate feedback without manual refreshing.

#### Acceptance Criteria

1. THE System SHALL subscribe to Supabase Realtime updates on jobs table
2. WHEN job status changes to 'generating', THE System SHALL display skeleton loader on Canvas
3. WHEN job status changes to 'auditing', THE System SHALL display "Scanning Compliance..." overlay
4. WHEN job status changes to 'completed', THE System SHALL load image and audit results
5. WHEN job status changes to 'failed', THE System SHALL display error state with retry option
6. THE System SHALL update Compliance Gauge reactively when audit results arrive
7. THE System SHALL update bounding boxes reactively when violation data arrives
8. THE System SHALL update Twin Data panel reactively when token analysis arrives
9. THE System SHALL maintain WebSocket connection throughout session
10. WHEN WebSocket connection fails, THE System SHALL fall back to polling mode

### Requirement 10: Multi-Turn Session Management

**User Story:** As a user, I want to iteratively refine generated assets through multiple prompts, so that I can achieve the desired result through conversational tweaking.

#### Acceptance Criteria

1. THE System SHALL preserve session_id across multiple generation requests
2. WHEN user submits new prompt, THE System SHALL include session_id in API request
3. THE System SHALL add new thumbnail to Version Scrubber when new version is generated
4. THE System SHALL automatically scroll Version Scrubber to newest thumbnail
5. THE System SHALL maintain chat history across all turns in session
6. THE System SHALL pass previous_image_bytes to backend for context-aware generation
7. WHEN user clicks historical thumbnail, THE System SHALL restore that version's complete state (image, audit, chat context)

### Requirement 11: Responsive Mobile Layout

**User Story:** As a mobile user, I want the dashboard to adapt to smaller screens, so that I can monitor and interact with brand governance on any device.

#### Acceptance Criteria

1. WHEN viewport width is <768px, THE System SHALL collapse Bento Grid to single column
2. THE System SHALL stack zones in mobile order: Director, Canvas, Compliance Gauge, Twin Data, Context Deck
3. THE System SHALL reduce Director height to 40vh on mobile
4. THE System SHALL make Canvas full-width on mobile
5. THE System SHALL collapse Version Scrubber to vertical scrolling on mobile
6. THE System SHALL maintain touch-friendly tap targets (minimum 44x44px)
7. THE System SHALL enable horizontal swipe gesture on Version Scrubber thumbnails

### Requirement 12: Glassmorphism Visual Effects

**User Story:** As a user, I want the interface to have a premium, modern aesthetic, so that the tool feels professional and visually cohesive with the brand governance mission.

#### Acceptance Criteria

1. THE System SHALL apply glassmorphism effect to all panel components
2. THE System SHALL use `bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl` classes for glass panels
3. THE System SHALL apply glow effect to active/focused elements
4. THE System SHALL animate gradient text for AI status indicators
5. THE System SHALL use CSS-only scanning laser animation (no JavaScript)
6. THE System SHALL implement smooth transitions for state changes (300ms ease-in-out)
7. THE System SHALL apply subtle hover effects to interactive elements (scale 1.02, glow increase)

### Requirement 13: API Integration and Error Handling

**User Story:** As a developer, I want robust API integration with proper error handling, so that the application gracefully handles network failures and backend errors.

#### Acceptance Criteria

1. THE System SHALL use existing apiClient from `frontend/src/api/client.ts`
2. THE System SHALL preserve existing type definitions from `frontend/src/api/types.ts`
3. WHEN generation request fails, THE System SHALL display error message in Director chat
4. WHEN audit service is unavailable, THE System SHALL show grey Compliance Gauge with "Audit Unavailable" message
5. WHEN audit fails but image generated successfully, THE System SHALL display image with warning toast
6. THE System SHALL allow download of image even when audit is unavailable
7. THE System SHALL implement retry mechanism with exponential backoff for failed requests
8. THE System SHALL display user-friendly error messages (no raw stack traces)
9. THE System SHALL log detailed errors to console for debugging

### Requirement 14: Accessibility Compliance

**User Story:** As a user with accessibility needs, I want the dashboard to be keyboard navigable and screen reader compatible, so that I can use the tool effectively regardless of ability.

#### Acceptance Criteria

1. THE System SHALL support keyboard navigation for all interactive elements
2. THE System SHALL provide ARIA labels for icon-only buttons
3. THE System SHALL maintain focus indicators with 2px outline in accent color
4. THE System SHALL provide alt text for generated images
5. THE System SHALL announce state changes to screen readers via aria-live regions
6. THE System SHALL ensure color contrast ratios meet WCAG AA standards (4.5:1 for text)
7. THE System SHALL support reduced motion preferences (disable animations when prefers-reduced-motion is set)
8. THE System SHALL make violation list keyboard navigable with arrow keys
