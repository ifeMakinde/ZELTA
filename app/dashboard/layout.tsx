import type { ReactNode } from "react";
import Sidebar from "./Sidebar";
import DashboardHeader from "@/components/DashboardHeader";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <div className="flex min-h-screen">
        {/* Desktop sidebar — fixed left rail, hidden on mobile */}
        <div className="hidden lg:block w-64 xl:w-60 shrink-0 border-r border-gray-200 bg-white">
          <div className="sticky top-0 h-screen">
            <Sidebar />
          </div>
        </div>

        {/* Main content */}
        <div className="flex flex-1 flex-col min-h-screen min-w-0">
          <DashboardHeader />
          {/* pb-20 on mobile leaves room above the fixed bottom nav */}
          <main className="flex-1 p-4 pb-24 lg:pb-6 lg:p-6">{children}</main>
        </div>
      </div>

      {/* Mobile bottom nav is rendered inside Sidebar but positioned fixed */}
      <div className="lg:hidden">
        <Sidebar />
      </div>
    </div>
  );
}