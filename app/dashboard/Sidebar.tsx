import Link from "next/link";
import {
  Home,
  Wallet,
  Brain,
  Sparkles,
  MessageSquare,
  User,
  History,
} from "lucide-react";

const navItems = [
  { icon: <Home strokeWidth={1} />, label: "Home", href: "/dashboard" },
  {
    icon: <Wallet strokeWidth={1} />,
    label: "Wallet",
    href: "/dashboard/wallet",
  },
  {
    icon: <Brain strokeWidth={1} />,
    label: "Behavioral",
    href: "/dashboard/behavioral",
  },
  {
    icon: <Sparkles strokeWidth={1} />,
    label: "Simulation",
    href: "/dashboard/simulations",
  },
  {
    icon: <MessageSquare strokeWidth={1} />,
    label: "Co-Pilot",
    href: "/dashboard/co-pilot",
  },
  {
    icon: <History strokeWidth={1} />,
    label: "History",
    href: "/dashboard/history",
  },
  {
    icon: <User strokeWidth={1} />,
    label: "Profile",
    href: "/dashboard/profile",
  },
];

export default function Sidebar() {
  return (
    <aside className="flex h-full flex-col justify-between p-4 lg:p-6">
      <div className="">
        <div className="mb-8 px-2 hidden lg:block">
          <p className="text-lg font-bold text-green-600">ZELTA</p>
          <p className="text-sm text-slate-500">Financial Intelligence</p>
        </div>

        <nav className="lg:space-y-2 flex justify-center items-center sm:gap-3 md:gap-8 lg:block ">
          {navItems.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className="rounded-2xl px-3 py-3 text-md font-bold text-gray-600 hover:text-white transition hover:bg-[#10b981] flex flex-col lg:flex-row gap-2  lg:gap-4 items-center "
            >
              <span>{item.icon}</span>
              <span className="hidden lg:block">{item.label} </span>
            </Link>
          ))}
        </nav>
      </div>

      <div className=" hidden lg:block rounded-2xl border border-slate-200 bg-green-50 p-4 text-sm text-slate-700">
        <p className="font-semibold text-slate-900">Dashboard info</p>
        <p className="mt-2 text-slate-600">
          Use the sidebar to switch sections. The right side renders selected
          dashboard content.
        </p>
      </div>
    </aside>
  );
}
