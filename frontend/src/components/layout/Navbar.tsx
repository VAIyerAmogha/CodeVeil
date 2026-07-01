"use client";

import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import { User } from '@/types/user';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { useState } from 'react';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const userData = user as User & { picture?: string };
  const router = useRouter();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <header className="sticky top-0 z-50 w-full backdrop-blur-xl bg-black/60 border-b border-green-500/20 shadow-[0_4px_30px_rgba(0,255,0,0.05)]">
      <div className="max-w-[1400px] mx-auto px-4 md:px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="group-hover:scale-110 transition-transform duration-300">
            <Image
              src="/CodeVeil_logo1.png"
              alt="CodeVeil Logo"
              width={32}
              height={32}
              className="md:w-[40px] md:h-[40px]"
            />
          </div>
          <span className="text-lg md:text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-emerald-600 tracking-tight">CodeVeil</span>
        </Link>
        
        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-4 md:gap-6 text-sm font-medium">
          <Link href="/" className="text-green-100/70 hover:text-green-400 transition-colors">Home</Link>
          <Link href="/dashboard" className="text-green-100/70 hover:text-green-400 transition-colors">Dashboard</Link>
          {isAuthenticated && userData ? (
            <div className="flex items-center gap-3 md:gap-4">
              <div className="flex items-center gap-2 border-r border-green-500/20 pr-3 md:pr-4">
                <span className="text-green-100/90">{userData.name}</span>
                {userData.picture ? (
                  <img src={userData.picture} alt={userData.name} className="w-8 h-8 rounded-full border border-green-500/30 object-cover" />
                ) : (
                  <div className="w-8 h-8 rounded-full bg-green-900/50 border border-green-500/30 flex items-center justify-center text-green-400 font-bold">
                    {userData.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                )}
              </div>
              <button
                onClick={handleLogout}
                className="text-red-400/80 hover:text-red-400 transition-colors"
              >
                Log Out
              </button>
            </div>
          ) : (
            <Link href="/auth/login" className="px-4 py-2 rounded-md bg-green-500/10 border border-green-500/30 text-green-400 hover:bg-green-500/20 hover:shadow-[0_0_15px_rgba(34,197,94,0.3)] transition-all duration-300">
              Sign In
            </Link>
          )}
        </nav>

        {/* Mobile Hamburger Button */}
        <button 
          className="md:hidden text-green-400 hover:text-green-300 focus:outline-none"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {isMenuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      {/* Mobile Nav Menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-black/95 border-t border-green-500/20 px-4 py-4 space-y-4">
          <Link href="/" className="block text-green-100/70 hover:text-green-400" onClick={() => setIsMenuOpen(false)}>Home</Link>
          <Link href="/dashboard" className="block text-green-100/70 hover:text-green-400" onClick={() => setIsMenuOpen(false)}>Dashboard</Link>
          {isAuthenticated && userData ? (
            <div className="pt-4 border-t border-green-500/20">
              <div className="flex items-center gap-3 mb-4">
                {userData.picture ? (
                  <img src={userData.picture} alt={userData.name} className="w-8 h-8 rounded-full border border-green-500/30 object-cover" />
                ) : (
                  <div className="w-8 h-8 rounded-full bg-green-900/50 border border-green-500/30 flex items-center justify-center text-green-400 font-bold">
                    {userData.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                )}
                <span className="text-green-100/90">{userData.name}</span>
              </div>
              <button onClick={() => { setIsMenuOpen(false); handleLogout(); }} className="text-red-400/80 hover:text-red-400 w-full text-left">Log Out</button>
            </div>
          ) : (
            <div className="pt-4 border-t border-green-500/20">
              <Link href="/auth/login" onClick={() => setIsMenuOpen(false)} className="block w-full text-center py-2 rounded-md bg-green-500/10 border border-green-500/30 text-green-400">
                Sign In
              </Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
