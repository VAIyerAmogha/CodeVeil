import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import AuthHydrator from '@/components/layout/AuthHydrator';

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "CodeVeil",
  description: "Understand Any Codebase. Instantly.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} min-h-screen flex flex-col bg-black text-green-50`}>
        <AuthHydrator>
          <Navbar />
          <main className="flex-grow flex flex-col relative z-10 w-full">
            {children}
          </main>
          <Footer />
        </AuthHydrator>
      </body>
    </html>
  );
}
