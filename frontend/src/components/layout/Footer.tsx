export default function Footer() {
  return (
    <footer className="w-full backdrop-blur-md bg-black/40 border-t border-green-500/20 mt-auto">
      <div className="max-w-[1400px] mx-auto px-6 py-6 flex items-center justify-between text-xs text-green-500/50">
        <p>&copy; {new Date().getFullYear()} CodeVeil. All rights reserved.</p>
        <div className="flex gap-4">
          <a href="#" className="hover:text-green-400 transition-colors">Privacy</a>
          <a href="#" className="hover:text-green-400 transition-colors">Terms</a>
        </div>
      </div>
    </footer>
  );
}
