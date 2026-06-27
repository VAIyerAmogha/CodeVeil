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
          className="bg-zinc-800 text-zinc-300 text-xs rounded-full px-3 py-1 font-medium"
        >
          {badge}
        </span>
      ))}
    </div>
  );
}
