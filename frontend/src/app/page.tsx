import React from 'react';
import HeroSection from '../components/landing/HeroSection';
import FeatureGrid from '../components/landing/FeatureGrid';
import TechBadges from '../components/landing/TechBadges';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-black via-black to-green-950 flex flex-col items-center pt-24 pb-16 px-4 md:px-8 font-sans">
      <div className="w-full max-w-6xl mx-auto flex flex-col items-center gap-16 md:gap-24">
        <HeroSection />
        <TechBadges />
        <FeatureGrid />
      </div>
    </main>
  );
}
