import type { ReactNode } from "react";
import Sidebar from "./Sidebar";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen ">
      <div className="grid min-h-screen grid-rows-[90%_10%] lg:grid-rows-none grid-cols-none lg:grid-cols-[25%_75%] xl:grid-cols-[20%_80%] grid-row-r">
        <div className="border-r border-slate-200 bg-white order-2 lg:order-1">
          <Sidebar />
        </div>
        <main className=" p-6 lg:p-8 order-1 lg:order-2">{children}</main>
      </div>
    </div>
  );
}
