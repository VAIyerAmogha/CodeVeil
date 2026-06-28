import React from "react";
import Image from "next/image";

const steps = [
  {
    title: "Your Personalized Dashboard",
    description:
      "Keep all your indexed repositories in one place. Easily manage, add, or remove projects. The dashboard acts as your command center, offering quick insights into your codebase metrics.",
    reversed: false,
  },
  {
    title: "Deep Repository Analysis",
    description:
      "CodeVeil performs a deep AST-aware analysis of your code. Understand architectural dependencies, analyze complexities, and view exactly how files map out before making a single query.",
    reversed: true,
  },
  {
    title: "Intelligent AI Code Queries",
    description:
      "Ask natural language questions about your architecture, debug issues, or request refactoring ideas. Every answer is backed by exact file references and cited code snippets, giving you unparalleled confidence.",
    reversed: false,
  },
];

const images = [
  "/Landing_1.jpeg",
  "/Landing_2.jpeg",
  "/Landing_3.jpeg",
];

export default function WalkthroughSection() {
  return (
    <div className="w-full max-w-6xl mx-auto flex flex-col gap-24 py-16 px-4">
      <div className="text-center mb-4">
        <h2 className="text-3xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-emerald-600 mb-6">
          How CodeVeil Works
        </h2>

        <p className="text-green-100/60 text-lg md:text-xl max-w-2xl mx-auto">
          A seamless flow designed to bring immediate clarity to complex
          codebases.
        </p>
      </div>

      {steps.map((step, idx) => (
        <div
          key={idx}
          className={`flex flex-col md:flex-row items-center gap-8 md:gap-14 ${step.reversed ? "md:flex-row-reverse" : ""
            }`}
        >
          {/* Content */}
          <div className="flex-1 bg-black/40 border border-green-500/20 rounded-2xl p-6 md:p-8 shadow-[0_4px_30px_rgba(0,255,0,0.05)]">
            <div className="inline-flex items-center justify-center w-11 h-11 rounded-full bg-green-500/10 border border-green-500/30 text-green-400 font-bold text-lg mb-5">
              {idx + 1}
            </div>

            <h3 className="text-2xl md:text-3xl font-bold text-zinc-100 mb-4">
              {step.title}
            </h3>

            <p className="text-green-100/70 leading-relaxed text-base md:text-lg">
              {step.description}
            </p>
          </div>

          {/* Illustration */}
          <div className="relative flex-1 w-full h-[260px] md:h-[340px]">
            <Image
              src={images[idx]}
              alt={step.title}
              fill
              priority={idx === 0}
              className="object-contain rounded-2xl"
              sizes="(max-width: 768px) 100vw, 50vw"
            />
          </div>
        </div>
      ))}
    </div>
  );
}