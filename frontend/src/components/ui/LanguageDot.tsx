import React from 'react';
import { getLanguageColor } from '@/lib/utils';

export default function LanguageDot({ language }: { language: string }) {
  const color = getLanguageColor(language);
  return (
    <span 
      className="inline-block w-3 h-3 rounded-full mr-1.5"
      style={{ backgroundColor: color }}
      title={language}
    />
  );
}
