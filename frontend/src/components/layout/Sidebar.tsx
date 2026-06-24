import Link from "next/link";

export function Sidebar() {
  return (
    <div className="w-64 bg-gray-900 h-full border-r border-gray-800 flex flex-col">
      <div className="p-4 border-b border-gray-800">
        <h1 className="text-primary text-2xl font-bold font-inter">CodeVeil</h1>
      </div>
      <nav className="flex-1 p-4 flex flex-col gap-2">
        <Link href="/dashboard" className="text-gray-300 hover:text-white hover:bg-gray-800 px-3 py-2 rounded-md transition-colors">
          Dashboard
        </Link>
        <Link href="/profile" className="text-gray-300 hover:text-white hover:bg-gray-800 px-3 py-2 rounded-md transition-colors">
          Profile
        </Link>
      </nav>
    </div>
  );
}
