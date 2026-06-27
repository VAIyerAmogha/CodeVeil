import Link from 'next/link';

import Image from "next/image";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full backdrop-blur-xl bg-black/60 border-b border-green-500/20 shadow-[0_4px_30px_rgba(0,255,0,0.05)]">
      <div className="max-w-[1400px] mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="group-hover:scale-110 transition-transform duration-300">
            <Image
              src="/CodeVeil_logo1.png"
              alt="CodeVeil Logo"
              width={40}
              height={40}
              priority
            />
          </div>
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-emerald-600 tracking-tight">CodeVeil</span>
        </Link>
        <nav className="flex items-center gap-6 text-sm font-medium">
          <Link href="/dashboard" className="text-green-100/70 hover:text-green-400 transition-colors">Dashboard</Link>
          <Link href="/auth/login" className="px-4 py-2 rounded-md bg-green-500/10 border border-green-500/30 text-green-400 hover:bg-green-500/20 hover:shadow-[0_0_15px_rgba(34,197,94,0.3)] transition-all duration-300">
            Sign In
          </Link>
        </nav>
      </div>
    </header>
  );
}
