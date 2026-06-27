import React from 'react';

export default function TechBadges() {
  const badges = [
    'tree-sitter',
    'ChromaDB',
    'Groq',
    'BM25',
    'cross-encoder',
    'bge-small'
  ];

  return (
    <div className="flex flex-wrap justify-center gap-3">
      {badges.map((badge) => (
        <span
          key={badge}
          className="bg-green-900/20 border-green-500/20 text-green-100/80 text-xs rounded-full px-3 py-1 font-medium"
        >
          {badge}
        </span>
      ))}
    </div>
  );
}
