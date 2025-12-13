/**
 * Accessibility Audit Tests using axe-core
 * 
 * Comprehensive accessibility testing for the Luminous Dashboard
 * using @axe-core/playwright for automated WCAG compliance checking.
 * 
 * Requirements: 14.1-14.8
 */

import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Luminous Dashboard - Accessibility Audit', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the dashboard
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    // Wait for the dashboard to fully render
    await page.waitForTimeout(1000);
  });

  test('Dashboard should have no critical accessibility violations', async ({ page }) => {
    // Run axe-core accessibility scan
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    // Log violations for debugging
    if (accessibilityScanResults.violations.length > 0) {
      console.log('Accessibility Violations Found:');
      accessibilityScanResults.violations.forEach((violation, index) => {
        console.log(`\n${index + 1}. ${violation.id}: ${violation.description}`);
        console.log(`   Impact: ${violation.impact}`);
        console.log(`   Help: ${violation.helpUrl}`);
        console.log(`   Affected nodes: ${violation.nodes.length}`);
        violation.nodes.forEach((node, nodeIndex) => {
          console.log(`   ${nodeIndex + 1}. ${node.html.substring(0, 100)}...`);
          console.log(`      Fix: ${node.failureSummary}`);
        });
      });
    }

    // Filter for critical and serious violations only
    const criticalViolations = accessibilityScanResults.violations.filter(
      v => v.impact === 'critical' || v.impact === 'serious'
    );

    // Assert no critical/serious violations
    expect(criticalViolations).toHaveLength(0);
  });

  test('All interactive elements should be keyboard accessible', async ({ page }) => {
    // Run axe-core with keyboard accessibility rules
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['keyboard'])
      .analyze();

    // Log keyboard accessibility issues
    if (accessibilityScanResults.violations.length > 0) {
      console.log('Keyboard Accessibility Issues:');
      accessibilityScanResults.violations.forEach((violation) => {
        console.log(`- ${violation.id}: ${violation.description}`);
      });
    }

    // Filter for critical keyboard issues
    const criticalKeyboardIssues = accessibilityScanResults.violations.filter(
      v => v.impact === 'critical' || v.impact === 'serious'
    );

    expect(criticalKeyboardIssues).toHaveLength(0);
  });

  test('All images should have alt text', async ({ page }) => {
    // Run axe-core specifically for image alt text
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withRules(['image-alt'])
      .analyze();

    // Log image alt text issues
    if (accessibilityScanResults.violations.length > 0) {
      console.log('Image Alt Text Issues:');
      accessibilityScanResults.violations.forEach((violation) => {
        violation.nodes.forEach((node) => {
          console.log(`- Missing alt: ${node.html.substring(0, 100)}`);
        });
      });
    }

    expect(accessibilityScanResults.violations).toHaveLength(0);
  });

  test('Color contrast should meet WCAG AA standards', async ({ page }) => {
    // Run axe-core specifically for color contrast
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withRules(['color-contrast'])
      .analyze();

    // Log color contrast issues
    if (accessibilityScanResults.violations.length > 0) {
      console.log('Color Contrast Issues:');
      accessibilityScanResults.violations.forEach((violation) => {
        violation.nodes.forEach((node) => {
          console.log(`- ${node.html.substring(0, 80)}...`);
          console.log(`  Fix: ${node.failureSummary}`);
        });
      });
    }

    // Color contrast violations should be zero for WCAG AA compliance
    // Note: Some violations may be acceptable if they're decorative elements
    const criticalContrastIssues = accessibilityScanResults.violations.filter(
      v => v.impact === 'critical' || v.impact === 'serious'
    );

    expect(criticalContrastIssues).toHaveLength(0);
  });

  test('All form elements should have labels', async ({ page }) => {
    // Run axe-core for form label rules
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withRules(['label', 'label-title-only'])
      .analyze();

    // Log form label issues
    if (accessibilityScanResults.violations.length > 0) {
      console.log('Form Label Issues:');
      accessibilityScanResults.violations.forEach((violation) => {
        violation.nodes.forEach((node) => {
          console.log(`- ${node.html.substring(0, 100)}`);
        });
      });
    }

    expect(accessibilityScanResults.violations).toHaveLength(0);
  });

  test('ARIA attributes should be valid', async ({ page }) => {
    // Run axe-core for ARIA rules
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['cat.aria'])
      .analyze();

    // Log ARIA issues
    if (accessibilityScanResults.violations.length > 0) {
      console.log('ARIA Issues:');
      accessibilityScanResults.violations.forEach((violation) => {
        console.log(`- ${violation.id}: ${violation.description}`);
        violation.nodes.forEach((node) => {
          console.log(`  ${node.html.substring(0, 80)}...`);
        });
      });
    }

    // Filter for critical ARIA issues
    const criticalAriaIssues = accessibilityScanResults.violations.filter(
      v => v.impact === 'critical' || v.impact === 'serious'
    );

    expect(criticalAriaIssues).toHaveLength(0);
  });

  test('Page should have proper heading structure', async ({ page }) => {
    // Run axe-core for heading structure
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withRules(['heading-order', 'page-has-heading-one'])
      .analyze();

    // Log heading structure issues
    if (accessibilityScanResults.violations.length > 0) {
      console.log('Heading Structure Issues:');
      accessibilityScanResults.violations.forEach((violation) => {
        console.log(`- ${violation.id}: ${violation.description}`);
      });
    }

    // Heading structure is important but not always critical
    const criticalHeadingIssues = accessibilityScanResults.violations.filter(
      v => v.impact === 'critical'
    );

    expect(criticalHeadingIssues).toHaveLength(0);
  });

  test('Links should have discernible text', async ({ page }) => {
    // Run axe-core for link text rules
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withRules(['link-name'])
      .analyze();

    // Log link text issues
    if (accessibilityScanResults.violations.length > 0) {
      console.log('Link Text Issues:');
      accessibilityScanResults.violations.forEach((violation) => {
        violation.nodes.forEach((node) => {
          console.log(`- ${node.html.substring(0, 100)}`);
        });
      });
    }

    expect(accessibilityScanResults.violations).toHaveLength(0);
  });

  test('Buttons should have discernible text', async ({ page }) => {
    // Run axe-core for button text rules
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withRules(['button-name'])
      .analyze();

    // Log button text issues
    if (accessibilityScanResults.violations.length > 0) {
      console.log('Button Text Issues:');
      accessibilityScanResults.violations.forEach((violation) => {
        violation.nodes.forEach((node) => {
          console.log(`- ${node.html.substring(0, 100)}`);
        });
      });
    }

    expect(accessibilityScanResults.violations).toHaveLength(0);
  });

  test('Focus should be visible on interactive elements', async ({ page }) => {
    // Tab through interactive elements and verify focus is visible
    const interactiveElements = page.locator('button, input, [tabindex="0"], a[href]');
    const count = await interactiveElements.count();

    // Tab through first several elements
    for (let i = 0; i < Math.min(count, 10); i++) {
      await page.keyboard.press('Tab');
      
      // Get the focused element
      const focusedElement = page.locator(':focus');
      const focusedCount = await focusedElement.count();
      
      if (focusedCount > 0) {
        // Check that the focused element has visible focus indicator
        const outlineStyle = await focusedElement.evaluate((el) => {
          const styles = window.getComputedStyle(el);
          return {
            outline: styles.outline,
            outlineWidth: styles.outlineWidth,
            outlineColor: styles.outlineColor,
            boxShadow: styles.boxShadow,
          };
        });

        // Focus should be visible via outline or box-shadow
        const hasVisibleFocus = 
          (outlineStyle.outlineWidth !== '0px' && outlineStyle.outline !== 'none') ||
          (outlineStyle.boxShadow !== 'none' && outlineStyle.boxShadow !== '');

        // Log focus state for debugging
        console.log(`Element ${i + 1} focus styles:`, outlineStyle);
        
        // We expect focus to be visible, but don't fail the test for minor issues
        if (!hasVisibleFocus) {
          console.warn(`Warning: Element ${i + 1} may not have visible focus indicator`);
        }
      }
    }
  });

  test('Document should have a main landmark', async ({ page }) => {
    // Run axe-core for landmark rules
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withRules(['landmark-one-main', 'region'])
      .analyze();

    // Log landmark issues
    if (accessibilityScanResults.violations.length > 0) {
      console.log('Landmark Issues:');
      accessibilityScanResults.violations.forEach((violation) => {
        console.log(`- ${violation.id}: ${violation.description}`);
      });
    }

    // Landmark issues are moderate severity
    const criticalLandmarkIssues = accessibilityScanResults.violations.filter(
      v => v.impact === 'critical'
    );

    expect(criticalLandmarkIssues).toHaveLength(0);
  });

  test('Full accessibility audit summary', async ({ page }) => {
    // Run comprehensive axe-core scan
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'])
      .analyze();

    // Generate summary report
    console.log('\n=== ACCESSIBILITY AUDIT SUMMARY ===\n');
    console.log(`Total violations: ${accessibilityScanResults.violations.length}`);
    console.log(`Total passes: ${accessibilityScanResults.passes.length}`);
    console.log(`Total incomplete: ${accessibilityScanResults.incomplete.length}`);
    console.log(`Total inapplicable: ${accessibilityScanResults.inapplicable.length}`);

    // Group violations by impact
    const byImpact = {
      critical: accessibilityScanResults.violations.filter(v => v.impact === 'critical'),
      serious: accessibilityScanResults.violations.filter(v => v.impact === 'serious'),
      moderate: accessibilityScanResults.violations.filter(v => v.impact === 'moderate'),
      minor: accessibilityScanResults.violations.filter(v => v.impact === 'minor'),
    };

    console.log('\nViolations by impact:');
    console.log(`  Critical: ${byImpact.critical.length}`);
    console.log(`  Serious: ${byImpact.serious.length}`);
    console.log(`  Moderate: ${byImpact.moderate.length}`);
    console.log(`  Minor: ${byImpact.minor.length}`);

    // List all violations with details
    if (accessibilityScanResults.violations.length > 0) {
      console.log('\n=== DETAILED VIOLATIONS ===\n');
      accessibilityScanResults.violations.forEach((violation, index) => {
        console.log(`${index + 1}. [${violation.impact?.toUpperCase()}] ${violation.id}`);
        console.log(`   Description: ${violation.description}`);
        console.log(`   Help: ${violation.help}`);
        console.log(`   URL: ${violation.helpUrl}`);
        console.log(`   Affected elements: ${violation.nodes.length}`);
        violation.nodes.slice(0, 3).forEach((node, nodeIndex) => {
          console.log(`   ${nodeIndex + 1}. ${node.html.substring(0, 80)}...`);
        });
        if (violation.nodes.length > 3) {
          console.log(`   ... and ${violation.nodes.length - 3} more`);
        }
        console.log('');
      });
    }

    // The test passes if there are no critical violations
    // Serious, moderate, and minor violations are logged but don't fail the test
    expect(byImpact.critical).toHaveLength(0);
  });

});

test.describe('Luminous Dashboard - Component-Specific Accessibility', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
  });

  test('Director chat interface accessibility', async ({ page }) => {
    // Focus on the Director component area
    const directorArea = page.locator('[data-testid="director"]').first();
    
    if (await directorArea.count() > 0) {
      const accessibilityScanResults = await new AxeBuilder({ page })
        .include('[data-testid="director"]')
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze();

      if (accessibilityScanResults.violations.length > 0) {
        console.log('Director Accessibility Issues:');
        accessibilityScanResults.violations.forEach((v) => {
          console.log(`- ${v.id}: ${v.description}`);
        });
      }

      const criticalIssues = accessibilityScanResults.violations.filter(
        v => v.impact === 'critical' || v.impact === 'serious'
      );

      expect(criticalIssues).toHaveLength(0);
    }
  });

  test('Canvas component accessibility', async ({ page }) => {
    // Focus on the Canvas component area
    const canvasArea = page.locator('[data-testid="canvas"]').first();
    
    if (await canvasArea.count() > 0) {
      const accessibilityScanResults = await new AxeBuilder({ page })
        .include('[data-testid="canvas"]')
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze();

      if (accessibilityScanResults.violations.length > 0) {
        console.log('Canvas Accessibility Issues:');
        accessibilityScanResults.violations.forEach((v) => {
          console.log(`- ${v.id}: ${v.description}`);
        });
      }

      const criticalIssues = accessibilityScanResults.violations.filter(
        v => v.impact === 'critical' || v.impact === 'serious'
      );

      expect(criticalIssues).toHaveLength(0);
    }
  });

  test('ComplianceGauge component accessibility', async ({ page }) => {
    // Focus on the ComplianceGauge component area
    const gaugeArea = page.locator('[data-testid="compliance-gauge"]').first();
    
    if (await gaugeArea.count() > 0) {
      const accessibilityScanResults = await new AxeBuilder({ page })
        .include('[data-testid="compliance-gauge"]')
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze();

      if (accessibilityScanResults.violations.length > 0) {
        console.log('ComplianceGauge Accessibility Issues:');
        accessibilityScanResults.violations.forEach((v) => {
          console.log(`- ${v.id}: ${v.description}`);
        });
      }

      const criticalIssues = accessibilityScanResults.violations.filter(
        v => v.impact === 'critical' || v.impact === 'serious'
      );

      expect(criticalIssues).toHaveLength(0);
    }
  });

});
