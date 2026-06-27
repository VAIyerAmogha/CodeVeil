"use client";

import React from 'react';
import Link from 'next/link';

export default function HeroSection() {
  return (
    <div className="flex flex-col items-center justify-center text-center max-w-3xl w-full px-4">
      <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-green-50 mb-6">
        Understand Any Codebase. Instantly.
      </h1>
      <p className="text-lg md:text-xl text-green-100/60 mb-10 max-w-2xl">
        An AI-powered assistant that reads your code, understands its architecture, and answers your questions with exact references. Built for developers to explore and master any project effortlessly.
      </p>
      
      <Link href="/dashboard" className="bg-green-600 hover:bg-green-500 text-green-50 font-medium px-8 py-4 rounded-lg transition-colors text-lg shadow-[0_0_20px_rgba(34,197,94,0.3)]">
        Get Started
      </Link>
    </div>
  );
}
