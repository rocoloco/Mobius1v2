/**
 * Generation History Panel - Shows recent asset generations
 * 
 * Matches the industrial design of the DataPlate but sized to viewport height.
 * Provides quick access to previous generations for iteration and refinement.
 */

import React, { useState } from 'react';
import { PolishedIndustrialCard } from '../../design-system/components/PolishedIndustrialCard';
import { IndustrialIndicator } from '../../design-system/components/IndustrialIndicator';
import { Clock, Download, RefreshCw } from 'lucide-react';

interface GenerationItem {
  id: string;
  prompt: string;
  imageUrl: string;
  timestamp: Date;
  complianceScore: number;
  status: 'completed' | 'processing' | 'failed';
}

interface GenerationHistoryProps {
  className?: string;
}

// Mock data for demonstration
const mockGenerations: GenerationItem[] = [
  {
    id: '1',
    prompt: 'LinkedIn post for Q3 earnings',
    imageUrl: '/api/placeholder/120/80',
    timestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
    complianceScore: 94,
    status: 'completed'
  },
  {
    id: '2', 
    prompt: 'Twitter announcement for new feature',
    imageUrl: '/api/placeholder/120/80',
    timestamp: new Date(Date.now() - 15 * 60 * 1000), // 15 minutes ago
    complianceScore: 87,
    status: 'completed'
  },
  {
    id: '3',
    prompt: 'Instagram story for product launch',
    imageUrl: '/api/placeholder/120/80', 
    timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
    complianceScore: 91,
    status: 'completed'
  },
  {
    id: '4',
    prompt: 'Blog header for technical tutorial',
    imageUrl: '/api/placeholder/120/80',
    timestamp: new Date(Date.now() - 45 * 60 * 1000), // 45 minutes ago
    complianceScore: 89,
    status: 'completed'
  }
];

export const GenerationHistory: React.FC<GenerationHistoryProps> = ({ className = '' }) => {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const formatTimeAgo = (timestamp: Date) => {
    const minutes = Math.floor((Date.now() - timestamp.getTime()) / (1000 * 60));
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  const getComplianceColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className={className}>
      <PolishedIndustrialCard
        variant="status"
        size="sm"
        neumorphic={true}
        manufacturing={{
          bolts: 'torx',
          texture: 'brushed'
        }}
        className="w-full opacity-60 hover:opacity-100 transition-all duration-300"
        style={{ maxHeight: 'calc(100vh - 12rem)' }}
      >
        <div className="h-full flex flex-col">
          {/* Header */}
          <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-300/50">
            <Clock size={10} className="text-gray-600" />
            <span className="font-mono text-[8px] uppercase tracking-widest text-gray-600">
              Generation History
            </span>
            <IndustrialIndicator status="on" size="sm" glow={true} />
          </div>

          {/* History List */}
          <div className="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
            {mockGenerations.map((item) => (
              <div
                key={item.id}
                className={`
                  group cursor-pointer p-2 rounded-lg border transition-all duration-200
                  ${selectedId === item.id
                    ? 'border-blue-400/50 bg-blue-50/30'
                    : 'border-gray-300/30 hover:border-gray-400/50 hover:bg-gray-50/30'
                  }
                `}
                onClick={() => setSelectedId(selectedId === item.id ? null : item.id)}
              >
                {/* Thumbnail and Info */}
                <div className="flex gap-2">
                  <div className="relative flex-shrink-0">
                    <div
                      className="w-12 h-9 bg-gray-200 rounded border border-gray-300/50"
                      style={{
                        backgroundImage: `url(${item.imageUrl})`,
                        backgroundSize: 'cover',
                        backgroundPosition: 'center'
                      }}
                    />
                    {/* Compliance Score Badge */}
                    <div className={`
                      absolute -top-1 -right-1 w-4 h-4 rounded-full text-[7px] font-bold
                      flex items-center justify-center border border-white
                      ${item.complianceScore >= 90 ? 'bg-green-500 text-white' :
                        item.complianceScore >= 80 ? 'bg-yellow-500 text-white' : 'bg-red-500 text-white'}
                    `}>
                      {item.complianceScore}
                    </div>
                  </div>

                  <div className="flex-1 min-w-0">
                    <p className="text-[9px] font-medium text-gray-800 truncate mb-1">
                      {item.prompt}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-[8px] text-gray-500 font-mono">
                        {formatTimeAgo(item.timestamp)}
                      </span>
                      <span className={`text-[8px] font-bold ${getComplianceColor(item.complianceScore)}`}>
                        {item.complianceScore}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Expanded Actions */}
                {selectedId === item.id && (
                  <div className="mt-3 pt-3 border-t border-gray-300/30 flex gap-2">
                    <button className="flex-1 flex items-center justify-center gap-1 px-2 py-1 text-[8px] font-medium text-gray-600 hover:text-gray-800 transition-colors">
                      <RefreshCw size={10} />
                      Refine
                    </button>
                    <button className="flex-1 flex items-center justify-center gap-1 px-2 py-1 text-[8px] font-medium text-gray-600 hover:text-gray-800 transition-colors">
                      <Download size={10} />
                      Export
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Footer Stats */}
          <div className="mt-3 pt-2 border-t border-gray-300/50">
            <div className="grid grid-cols-2 gap-2 text-center">
              <div>
                <div className="text-[9px] font-bold text-gray-800">4</div>
                <div className="text-[7px] text-gray-500 uppercase tracking-wider">Today</div>
              </div>
              <div>
                <div className="text-[9px] font-bold text-gray-800">91%</div>
                <div className="text-[7px] text-gray-500 uppercase tracking-wider">Avg Score</div>
              </div>
            </div>
          </div>
        </div>
      </PolishedIndustrialCard>
    </div>
  );
};

export default GenerationHistory;