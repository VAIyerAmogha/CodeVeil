import { Sidebar } from "./Sidebar";
import Navbar from "./Navbar";

export function PageWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-transparent text-green-50">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-y-auto bg-transparent/95">
          {children}
        </main>
      </div>
    </div>
  );
}
