"use client";

import React from 'react';
import IndexingForm from '../indexing/IndexingForm';

export default function HeroSection() {
  return (
    <div className="flex flex-col items-center justify-center text-center max-w-3xl w-full px-4">
      <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white mb-6">
        Understand Any Codebase. Instantly.
      </h1>
      <p className="text-lg md:text-xl text-zinc-400 mb-10 max-w-2xl">
        AST-aware retrieval, hybrid search, and cited AI answers with exact file:line references.
      </p>
      
      <IndexingForm />
    </div>
  );
}
