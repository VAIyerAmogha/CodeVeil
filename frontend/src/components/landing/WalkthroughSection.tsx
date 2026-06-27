import React from 'react';

const steps = [
  {
    title: "Your Personalized Dashboard",
    description: "Keep all your indexed repositories in one place. Easily manage, add, or remove projects. The dashboard acts as your command center, offering quick insights into your codebase metrics.",
    reversed: false,
  },
  {
    title: "Deep Repository Analysis",
    description: "CodeVeil performs a deep AST-aware analysis of your code. Understand architectural dependencies, analyze complexities, and view exactly how files map out before making a single query.",
    reversed: true,
  },
  {
    title: "Intelligent AI Code Queries",
    description: "Ask natural language questions about your architecture, debug issues, or request refactoring ideas. Every answer is backed by exact file references and cited code snippets, giving you unparalleled confidence.",
    reversed: false,
  }
];

export default function WalkthroughSection() {
  return (
    <div className="w-full max-w-6xl mx-auto flex flex-col gap-24 py-16 px-4">
      <div className="text-center mb-4">
        <h2 className="text-3xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-emerald-600 mb-6">
          How CodeVeil Works
        </h2>
        <p className="text-green-100/60 text-lg md:text-xl max-w-2xl mx-auto">
          A seamless flow designed to bring immediate clarity to complex codebases.
        </p>
      </div>

      {steps.map((step, idx) => (
        <div key={idx} className={`flex flex-col md:flex-row gap-6 md:gap-12 items-center ${step.reversed ? 'md:flex-row-reverse' : ''}`}>
          <div className="flex-1 space-y-4 md:space-y-6 bg-black/40 border border-green-500/20 p-6 md:p-8 rounded-2xl shadow-[0_4px_30px_rgba(0,255,0,0.05)] w-full">
            <div className="inline-flex items-center justify-center w-10 h-10 md:w-12 md:h-12 rounded-full bg-green-500/10 border border-green-500/30 text-green-400 font-bold text-lg md:text-xl mb-2">
              {idx + 1}
            </div>
            <h3 className="text-2xl md:text-3xl font-bold text-zinc-100">{step.title}</h3>
            <p className="text-green-100/70 text-base md:text-lg leading-relaxed">
              {step.description}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
