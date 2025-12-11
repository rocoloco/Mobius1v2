/**
 * Industrial User Avatar - Matches Industrial Design System
 * 
 * Professional user avatar component that fits the industrial aesthetic
 * with neumorphic styling and manufacturing details.
 */

import React from 'react';
import { Shield, Wrench, UserCircle } from 'lucide-react';
import { PolishedIndustrialCard } from '../../design-system/components/PolishedIndustrialCard';
import { IndustrialIndicator } from '../../design-system/components/IndustrialIndicator';
import { industrialTokens } from '../../design-system/tokens';

interface IndustrialUserAvatarProps {
  size?: 'sm' | 'md' | 'lg';
  initials?: string;
  role?: 'operator' | 'admin' | 'engineer' | 'user';
  status?: 'online' | 'offline' | 'busy';
  className?: string;
  onClick?: () => void;
}

export const IndustrialUserAvatar: React.FC<IndustrialUserAvatarProps> = ({
  size = 'md',
  initials,
  role = 'operator',
  status = 'online',
  className = '',
  onClick
}) => {
  const sizeConfig = {
    sm: { width: 32, height: 32, fontSize: '10px', iconSize: 14 },
    md: { width: 36, height: 36, fontSize: '12px', iconSize: 16 },
    lg: { width: 48, height: 48, fontSize: '16px', iconSize: 20 }
  };

  const config = sizeConfig[size];

  // Role-based icons and colors
  const roleConfig = {
    operator: { icon: UserCircle, color: industrialTokens.colors.text.primary },
    admin: { icon: Shield, color: '#dc2626' }, // Red for admin
    engineer: { icon: Wrench, color: '#2563eb' }, // Blue for engineer
    user: { icon: UserCircle, color: industrialTokens.colors.text.secondary }
  };

  const roleInfo = roleConfig[role];
  const RoleIcon = roleInfo.icon;

  // Status indicator mapping
  const statusMapping = {
    online: 'on' as const,
    offline: 'off' as const,
    busy: 'warning' as const
  };

  return (
    <div className="relative">
      <PolishedIndustrialCard
        variant="elevated"
        size="sm"
        neumorphic={true}
        manufacturing={{
          bolts: false, // Keep it clean for avatar
          texture: 'brushed'
        }}
        className={`flex items-center justify-center cursor-pointer ${className}`}
        onClick={onClick}
        style={{
          width: `${config.width}px`,
          height: `${config.height}px`,
          borderRadius: '50%',
          padding: 0,
          minWidth: `${config.width}px`,
          backgroundColor: industrialTokens.colors.surface.secondary,
          border: `2px solid ${industrialTokens.colors.surface.primary}`,
          overflow: 'hidden'
        }}
      >
        {initials ? (
          <span 
            className="font-bold font-mono uppercase tracking-wider"
            style={{ 
              fontSize: config.fontSize,
              color: roleInfo.color
            }}
          >
            {initials}
          </span>
        ) : (
          <RoleIcon 
            size={config.iconSize} 
            style={{ color: roleInfo.color }}
            strokeWidth={2.5}
          />
        )}
      </PolishedIndustrialCard>

      {/* Status Indicator */}
      <div 
        className="absolute -bottom-0.5 -right-0.5"
        style={{ zIndex: 10 }}
      >
        <IndustrialIndicator
          status={statusMapping[status]}
          size="sm"
          glow={status === 'online'}
          diffused={true}
        />
      </div>
    </div>
  );
};

export default IndustrialUserAvatar;