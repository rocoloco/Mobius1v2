import type { Config } from 'tailwindcss'
import { industrialTokens } from './src/design-system/tokens'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Enhanced Industrial Color System
        background: industrialTokens.colors.surface.primary,
        surface: {
          primary: industrialTokens.colors.surface.primary,
          secondary: industrialTokens.colors.surface.secondary,
          tertiary: industrialTokens.colors.surface.tertiary,
        },
        
        // Text colors
        ink: industrialTokens.colors.text.primary,
        "ink-muted": industrialTokens.colors.text.secondary,
        "ink-subtle": industrialTokens.colors.text.muted,

        // Shadow colors
        "shadow-light": industrialTokens.colors.shadows.light,
        "shadow-dark": industrialTokens.colors.shadows.dark,

        // The "Braun" Accent - Safety Orange
        accent: {
          DEFAULT: industrialTokens.colors.shadows.accent,
          hover: "#ff6b81",
        },

        // LED Status Colors
        led: {
          off: industrialTokens.colors.led.off,
          on: industrialTokens.colors.led.on,
          error: industrialTokens.colors.led.error,
          warning: industrialTokens.colors.led.warning,
        },

        // Legacy status colors (maintained for compatibility)
        success: "#2ed573",
        warning: "#ffa502",
        danger: "#ff4757",
      },
      
      boxShadow: {
        // Enhanced Neumorphic Shadow System
        'neumorphic-raised-subtle': industrialTokens.shadows.neumorphic.raised.subtle,
        'neumorphic-raised-normal': industrialTokens.shadows.neumorphic.raised.normal,
        'neumorphic-raised-deep': industrialTokens.shadows.neumorphic.raised.deep,
        'neumorphic-recessed-subtle': industrialTokens.shadows.neumorphic.recessed.subtle,
        'neumorphic-recessed-normal': industrialTokens.shadows.neumorphic.recessed.normal,
        'neumorphic-recessed-deep': industrialTokens.shadows.neumorphic.recessed.deep,
        
        // LED Glow Effects
        'led-glow': industrialTokens.shadows.glow.led,
        'accent-glow': industrialTokens.shadows.glow.accent,
        
        // Legacy shadows (maintained for compatibility)
        'soft': '9px 9px 16px rgb(163,177,198,0.6), -9px -9px 16px rgba(255,255,255, 0.5)',
        'soft-sm': '5px 5px 10px rgb(163,177,198,0.6), -5px -5px 10px rgba(255,255,255, 0.5)',
        'pressed': 'inset 6px 6px 10px 0 rgba(163,177,198, 0.7), inset -6px -6px 10px 0 rgba(255,255,255, 0.8)',
        'recessed': 'inset 4px 4px 8px 0 rgba(163,177,198, 0.6), inset -4px -4px 8px 0 rgba(255,255,255, 0.8)',
        'glow': '0 0 15px rgba(255, 71, 87, 0.6)',
        'glow-success': '0 0 8px rgba(46, 213, 115, 0.8)',
        'glow-warning': '0 0 8px rgba(255, 165, 2, 0.8)',
        'glow-danger': '0 0 8px rgba(255, 71, 87, 0.8)',
      },
      
      fontFamily: {
        sans: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
        secondary: ['"IBM Plex Sans"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      
      // Enhanced Animation System
      animation: {
        // Mechanical animations
        'mechanical-press': 'mechanicalPress 100ms cubic-bezier(0.34, 1.56, 0.64, 1)',
        'mechanical-release': 'mechanicalRelease 100ms cubic-bezier(0.34, 1.56, 0.64, 1)',
        'led-pulse': 'ledPulse 2s cubic-bezier(0.25, 0.46, 0.45, 0.94) infinite',
        'mechanical-slide-in': 'mechanicalSlideIn 250ms cubic-bezier(0.34, 1.56, 0.64, 1)',
        'mechanical-fade-in': 'mechanicalFadeIn 250ms cubic-bezier(0.34, 1.56, 0.64, 1)',
        'screw-rotate': 'screwRotate 500ms cubic-bezier(0.34, 1.56, 0.64, 1)',
        
        // Legacy animations (maintained for compatibility)
        'in': 'animate-in 0.3s ease-out',
        'slide-in-from-bottom': 'slide-in-from-bottom 0.3s ease-out',
        'slide-in-from-top': 'slide-in-from-top 0.2s ease-out',
        'fade-in': 'fade-in 0.2s ease-out',
      },
      
      keyframes: {
        // Mechanical keyframes
        'mechanicalPress': {
          '0%': { transform: 'translateY(0)' },
          '100%': { transform: 'translateY(2px)' },
        },
        'mechanicalRelease': {
          '0%': { transform: 'translateY(2px)' },
          '100%': { transform: 'translateY(0)' },
        },
        'ledPulse': {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.7', transform: 'scale(0.95)' },
        },
        'mechanicalSlideIn': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'mechanicalFadeIn': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'screwRotate': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        
        // Legacy keyframes (maintained for compatibility)
        'animate-in': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-from-bottom': {
          '0%': { opacity: '0', transform: 'translateY(40px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-from-top': {
          '0%': { opacity: '0', transform: 'translateY(-8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      
      // Mechanical easing functions
      transitionTimingFunction: {
        'mechanical': industrialTokens.animations.mechanical.easing,
        'mechanical-spring': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'mechanical-dampened': 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        'mechanical-heavy': 'cubic-bezier(0.55, 0.085, 0.68, 0.53)',
        'mechanical-light': 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
      },
      
      // Industrial spacing system
      spacing: {
        'screw': industrialTokens.manufacturing.screws.size,
        'vent': industrialTokens.manufacturing.vents.slotSpacing,
      },
      
      // Manufacturing detail utilities
      backgroundImage: {
        'vent-horizontal': `repeating-linear-gradient(90deg, transparent 0, transparent ${industrialTokens.manufacturing.vents.slotSpacing}, ${industrialTokens.manufacturing.vents.color} ${industrialTokens.manufacturing.vents.slotSpacing}, ${industrialTokens.manufacturing.vents.color} calc(${industrialTokens.manufacturing.vents.slotSpacing} + ${industrialTokens.manufacturing.vents.slotWidth}))`,
        'vent-vertical': `repeating-linear-gradient(0deg, transparent 0, transparent ${industrialTokens.manufacturing.vents.slotSpacing}, ${industrialTokens.manufacturing.vents.color} ${industrialTokens.manufacturing.vents.slotSpacing}, ${industrialTokens.manufacturing.vents.color} calc(${industrialTokens.manufacturing.vents.slotSpacing} + ${industrialTokens.manufacturing.vents.slotWidth}))`,
        'surface-brushed': 'linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.1) 100%)',
        'surface-textured': 'radial-gradient(circle at 1px 1px, rgba(0,0,0,0.05) 1px, transparent 0)',
      },
      
      backgroundSize: {
        'surface-textured': '8px 8px',
      },
    },
  },
  plugins: [
    // Industrial Design System Plugin
    function({ addUtilities, theme }) {
      const newUtilities = {
        // Manufacturing detail utilities
        '.screw': {
          width: theme('spacing.screw'),
          height: theme('spacing.screw'),
          backgroundColor: industrialTokens.manufacturing.screws.color,
          borderRadius: '50%',
          boxShadow: industrialTokens.manufacturing.screws.shadow,
          position: 'absolute',
        },
        '.screw-tl': {
          top: '8px',
          left: '8px',
        },
        '.screw-tr': {
          top: '8px',
          right: '8px',
        },
        '.screw-bl': {
          bottom: '8px',
          left: '8px',
        },
        '.screw-br': {
          bottom: '8px',
          right: '8px',
        },
        
        // Press physics utilities
        '.press-physics': {
          transition: `transform ${industrialTokens.animations.press.duration} ${industrialTokens.animations.mechanical.easing}, box-shadow ${industrialTokens.animations.press.duration} ${industrialTokens.animations.mechanical.easing}`,
        },
        '.press-physics:active': {
          transform: industrialTokens.animations.press.transform,
        },
        
        // LED indicator utilities
        '.led-indicator': {
          borderRadius: '50%',
          transition: `all ${industrialTokens.animations.mechanical.duration.normal} ${industrialTokens.animations.mechanical.easing}`,
        },
        
        // Surface texture utilities
        '.surface-smooth': {},
        '.surface-brushed': {
          backgroundImage: theme('backgroundImage.surface-brushed'),
        },
        '.surface-textured': {
          backgroundImage: theme('backgroundImage.surface-textured'),
          backgroundSize: theme('backgroundSize.surface-textured'),
        },
      }
      
      addUtilities(newUtilities)
    }
  ],
} satisfies Config
