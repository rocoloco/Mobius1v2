# Visual Testing with Playwright

## Overview
This project uses Playwright for comprehensive visual regression testing of the Industrial Design System. The testing suite captures screenshots of components and layouts to detect visual changes over time.

## Test Structure

### 1. Full System Tests (`industrial-design-system.spec.ts`)
- Full page screenshots
- Section-by-section visual validation
- Interactive state testing (hover, focus, pressed)
- Cross-browser consistency checks
- Responsive design validation

### 2. Component Isolation Tests (`component-isolation.spec.ts`)
- Individual component screenshots
- Detailed component variations
- Layout measurement validation
- Typography and spacing checks

### 3. Performance & Accessibility Tests (`performance-accessibility.spec.ts`)
- Performance metrics validation
- Accessibility compliance checks
- Keyboard navigation testing
- Color contrast validation
- Screen reader compatibility

## Running Tests

### Basic Commands
```bash
# Run all visual tests
npm run test:visual

# Run with UI mode for debugging
npm run test:visual:ui

# Run in debug mode
npm run test:visual:debug

# Update baseline screenshots
npm run test:visual:update
```

### Specific Test Runs
```bash
# Run only Chromium tests
npx playwright test --project=chromium

# Run specific test file
npx playwright test tests/visual/industrial-design-system.spec.ts

# Run tests matching pattern
npx playwright test --grep "Button hover"
```

## Browser Coverage
- **Chromium** (Desktop Chrome)
- **Firefox** (Desktop Firefox)
- **WebKit** (Desktop Safari)
- **Mobile Chrome** (Pixel 5)
- **Mobile Safari** (iPhone 12)

## Viewport Testing
- **Desktop**: 1280x720, 1920x1080
- **Tablet**: 768x1024
- **Mobile Portrait**: 375x667
- **Mobile Landscape**: 667x375

## Generated Artifacts

### Screenshots
- Baseline screenshots stored in `tests/visual/*-snapshots/`
- Failed test screenshots in `test-results/`
- Cross-browser comparison screenshots

### Reports
- HTML report: `playwright-report/index.html`
- JSON results: `test-results/visual-test-results.json`
- Video recordings for failed tests

## Best Practices

### 1. Consistent Testing
- Animations are disabled during tests for consistent screenshots
- Fixed viewport sizes ensure reproducible results
- Network idle state ensures complete page loading

### 2. Baseline Management
- Run `npm run test:visual:update` after intentional visual changes
- Review screenshot diffs carefully before approving changes
- Use version control to track baseline changes

### 3. Debugging Failed Tests
- Use `npm run test:visual:ui` for interactive debugging
- Check generated screenshots in `test-results/`
- Review video recordings for dynamic failures

## CI/CD Integration
The tests are configured for CI environments with:
- Retry logic for flaky tests
- Parallel execution control
- Artifact collection for failed tests
- Threshold-based visual comparison (0.2 pixel difference tolerance)

## Maintenance
- Update baselines when design changes are intentional
- Add new tests for new components
- Review and update viewport sizes as needed
- Monitor test execution time and optimize as necessary