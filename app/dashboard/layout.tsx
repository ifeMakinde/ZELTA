import type { ReactNode } from "react";
import Sidebar from "./Sidebar";
import DashboardHeader from "@/components/DashboardHeader";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <div className="grid min-h-screen grid-rows-[1fr_auto] lg:grid-rows-none grid-cols-none lg:grid-cols-[25%_75%] xl:grid-cols-[20%_80%]">
        {/* Sidebar */}
        <div className="border-r border-r-gray-300 bg-white order-2 lg:order-1">
          <Sidebar />
        </div>

        {/* Main content area with sticky header */}
        <div className="order-1 lg:order-2 flex flex-col min-h-screen">
          <DashboardHeader />
          <main className="flex-1 p-4 lg:p-6">{children}</main>
        </div>
      </div>
    </div>
  );
}