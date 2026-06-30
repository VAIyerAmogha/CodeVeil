import React from 'react';

export default function RiskScoreGauge({ score, grade }: { score: number, grade: string }) {
  let color = '#22C55E'; // green
  if (score < 35) color = '#EF4444'; // red
  else if (score < 65) color = '#F97316'; // orange
  else if (score < 80) color = '#F59E0B'; // yellow
  
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-6 glass-panel border border-green-500/20 rounded-xl mb-6 relative">
      <h3 className="text-zinc-300 font-medium mb-4">Security Score</h3>
      <div className="relative w-40 h-40">
        {/* Background circle */}
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 140 140">
          <circle
            cx="70"
            cy="70"
            r={radius}
            fill="transparent"
            stroke="rgba(34, 197, 94, 0.1)"
            strokeWidth="12"
          />
          {/* Progress circle */}
          <circle
            cx="70"
            cy="70"
            r={radius}
            fill="transparent"
            stroke={color}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold" style={{ color }}>{score}</span>
          <span className="text-sm font-medium text-zinc-400 mt-1">Grade {grade}</span>
        </div>
      </div>
    </div>
  );
}
