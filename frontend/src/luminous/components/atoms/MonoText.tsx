import { luminousTokens } from '../../tokens';

interface MonoTextProps {
  children: string;
  className?: string;
}

/**
 * MonoText - Monospace text component
 * 
 * Applies monospace font (JetBrains Mono) with high contrast text color.
 * Used for displaying hex codes, data values, and technical information.
 * 
 * @param children - Text content to display
 * @param className - Additional CSS classes to apply
 */
export function MonoText({ children, className = '' }: MonoTextProps) {
  return (
    <span
      className={`font-mono text-slate-100 ${className}`}
      style={{
        fontFamily: luminousTokens.typography.fontFamily.mono,
        color: luminousTokens.colors.text.high,
      }}
    >
      {children}
    </span>
  );
}
