import type { Config } from 'tailwindcss'
import { luminousTokens } from './src/luminous/tokens'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Luminous Design System Colors
        luminous: {
          void: luminousTokens.colors.void,
          glass: luminousTokens.colors.glass,
          border: luminousTokens.colors.border,
          accent: {
            purple: luminousTokens.colors.accent.purple,
            blue: luminousTokens.colors.accent.blue,
          },
          compliance: {
            pass: luminousTokens.colors.compliance.pass,
            review: luminousTokens.colors.compliance.review,
            critical: luminousTokens.colors.compliance.critical,
          },
          text: {
            body: luminousTokens.colors.text.body,
            high: luminousTokens.colors.text.high,
            muted: luminousTokens.colors.text.muted,
          },
        },
        
        // Primary background and surface colors (Luminous)
        background: luminousTokens.colors.void,
        surface: {
          primary: luminousTokens.colors.void,
          secondary: 'rgba(255, 255, 255, 0.03)',
          tertiary: 'rgba(255, 255, 255, 0.05)',
        },
        
        // Text colors (Luminous)
        ink: luminousTokens.colors.text.high,
        "ink-muted": luminousTokens.colors.text.body,
        "ink-subtle": luminousTokens.colors.text.muted,
        
        // Accent colors (Luminous)
        accent: {
          DEFAULT: luminousTokens.colors.accent.purple,
          hover: luminousTokens.colors.accent.blue,
        },
        
        // Status colors (Luminous compliance)
        success: luminousTokens.colors.compliance.pass,
        warning: luminousTokens.colors.compliance.review,
        danger: luminousTokens.colors.compliance.critical,
      },
      
      boxShadow: {
        // Luminous Glow Effects
        'luminous-glow': luminousTokens.effects.glow,
        'luminous-glow-strong': luminousTokens.effects.glowStrong,
        
        // General glow effects
        'glow': luminousTokens.effects.glow,
        'glow-success': `0 0 8px ${luminousTokens.colors.compliance.pass}80`,
        'glow-warning': `0 0 8px ${luminousTokens.colors.compliance.review}80`,
        'glow-danger': `0 0 8px ${luminousTokens.colors.compliance.critical}80`,
      },
      
      fontFamily: {
        sans: luminousTokens.typography.fontFamily.sans.split(',').map(f => f.trim()),
        mono: luminousTokens.typography.fontFamily.mono.split(',').map(f => f.trim()),
        'luminous-sans': luminousTokens.typography.fontFamily.sans.split(',').map(f => f.trim()),
        'luminous-mono': luminousTokens.typography.fontFamily.mono.split(',').map(f => f.trim()),
      },
      
      // Luminous Animation System
      animation: {
        'scanning-laser': 'scanningLaser 2s ease-in-out infinite',
        'connection-pulse': 'connectionPulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'gradient-pan': 'gradientPan 3s linear infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite',
        'slide-up': 'slideUp 300ms cubic-bezier(0.4, 0, 0.2, 1)',
        'fade-in-up': 'fadeInUp 300ms cubic-bezier(0.4, 0, 0.2, 1)',
        'scale-in': 'scaleIn 200ms cubic-bezier(0.4, 0, 0.2, 1)',
        'in': 'animate-in 0.3s ease-out',
        'slide-in-from-bottom': 'slide-in-from-bottom 0.3s ease-out',
        'slide-in-from-top': 'slide-in-from-top 0.2s ease-out',
        'fade-in': 'fade-in 0.2s ease-out',
      },
      
      keyframes: {
        // Luminous keyframes
        'scanningLaser': {
          '0%, 100%': { transform: 'translateX(-100%)' },
          '50%': { transform: 'translateX(250%)' },
        },
        'connectionPulse': {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.6', transform: 'scale(1.1)' },
        },
        'gradientPan': {
          '0%': { backgroundPosition: '0% center' },
          '100%': { backgroundPosition: '200% center' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'glowPulse': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(37, 99, 235, 0.15)' },
          '50%': { boxShadow: '0 0 30px rgba(37, 99, 235, 0.3)' },
        },
        'slideUp': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fadeInUp': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'scaleIn': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'gradient-shift': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
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
      
      // Luminous background images
      backgroundImage: {
        'luminous-gradient': luminousTokens.colors.accent.gradient,
      },
    },
  },
  plugins: [
    // Luminous Design System Plugin
    function({ addUtilities }) {
      const newUtilities = {
        // Luminous glassmorphism utilities
        '.glass-panel': {
          backgroundColor: luminousTokens.colors.glass,
          backdropFilter: luminousTokens.effects.backdropBlur,
          borderColor: luminousTokens.colors.border,
          borderWidth: '1px',
          borderRadius: '1rem',
        },
        '.glass-panel-glow': {
          boxShadow: luminousTokens.effects.glow,
        },
        
        // Luminous gradient text utilities
        '.gradient-text': {
          backgroundImage: luminousTokens.colors.accent.gradient,
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          color: 'transparent',
        },
        '.gradient-text-animated': {
          backgroundImage: luminousTokens.colors.accent.gradient,
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          color: 'transparent',
          backgroundSize: '200% 200%',
          animation: 'gradient-shift 3s ease infinite',
        },
        
        // Accessibility focus utilities
        '.focus-visible-luminous': {
          '&:focus-visible': {
            outline: `2px solid ${luminousTokens.colors.accent.blue}`,
            outlineOffset: '2px',
          },
        },
        '.focus-ring-luminous': {
          '&:focus': {
            outline: 'none',
            boxShadow: `0 0 0 2px ${luminousTokens.colors.accent.blue}`,
          },
        },
        
        // Hover effect utilities
        '.hover-scale': {
          transition: 'transform 300ms ease-in-out, box-shadow 300ms ease-in-out',
          '&:hover': {
            transform: 'scale(1.02)',
          },
        },
        '.hover-glow': {
          transition: 'box-shadow 300ms ease-in-out',
          '&:hover': {
            boxShadow: luminousTokens.effects.glowStrong,
          },
        },
        '.hover-scale-glow': {
          transition: 'transform 300ms ease-in-out, box-shadow 300ms ease-in-out',
          '&:hover': {
            transform: 'scale(1.02)',
            boxShadow: luminousTokens.effects.glowStrong,
          },
        },
        '.hover-lift': {
          transition: 'transform 300ms ease-in-out, box-shadow 300ms ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)',
          },
        },
        
        // Reduced motion utilities
        '.motion-safe': {
          '@media (prefers-reduced-motion: no-preference)': {
            // Animations only apply when motion is not reduced
          },
        },
        '.motion-reduce': {
          '@media (prefers-reduced-motion: reduce)': {
            animation: 'none !important',
            transition: 'none !important',
          },
        },
        
        // GPU-accelerated transform utilities for performance
        '.gpu-accelerated': {
          transform: 'translateZ(0)',
          backfaceVisibility: 'hidden',
          perspective: '1000px',
        },
        '.will-change-transform': {
          willChange: 'transform',
        },
        '.will-change-opacity': {
          willChange: 'opacity',
        },
        '.will-change-auto': {
          willChange: 'auto',
        },
        
        // Composite layer hints for animations
        '.composite-layer': {
          transform: 'translate3d(0, 0, 0)',
          willChange: 'transform, opacity',
        },
        
        // Smooth scrolling with GPU acceleration
        '.smooth-scroll': {
          scrollBehavior: 'smooth',
          WebkitOverflowScrolling: 'touch',
        },
      }
      
      addUtilities(newUtilities)
    }
  ],
} satisfies Config
