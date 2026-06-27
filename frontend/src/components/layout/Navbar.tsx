"use client";

import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import { User } from '@/types/user';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const userData = user as User & { picture?: string };
  const router = useRouter();

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
        <nav className="flex items-center gap-4 md:gap-6 text-xs md:text-sm font-medium">
          <Link href="/dashboard" className="text-green-100/70 hover:text-green-400 transition-colors hidden sm:block">Dashboard</Link>
          {isAuthenticated && userData ? (
            <div className="flex items-center gap-3 md:gap-4">
              <div className="flex items-center gap-2 border-r border-green-500/20 pr-3 md:pr-4">
                <span className="text-green-100/90 hidden md:inline">{userData.name}</span>
                {userData.picture ? (
                  <img src={userData.picture} alt={userData.name} className="w-7 h-7 md:w-8 md:h-8 rounded-full border border-green-500/30 object-cover" />
                ) : (
                  <div className="w-7 h-7 md:w-8 md:h-8 rounded-full bg-green-900/50 border border-green-500/30 flex items-center justify-center text-green-400 font-bold">
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
            <Link href="/auth/login" className="px-3 py-1.5 md:px-4 md:py-2 rounded-md bg-green-500/10 border border-green-500/30 text-green-400 hover:bg-green-500/20 hover:shadow-[0_0_15px_rgba(34,197,94,0.3)] transition-all duration-300">
              Sign In
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
