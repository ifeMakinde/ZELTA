"use client";
import React from "react";
import PageHeader from "@/components/PageHeader";
import { Activity, Sparkles, MessageSquare } from "lucide-react";

function page() {
  const [amount, setAmount] = React.useState<string>("");
  const [amountph, setAmountPh] = React.useState<string>("Enter amount (₦)");

  function handleAmountChange(e: React.ChangeEvent<HTMLInputElement>): void {
    setAmount(e.target.value);
  };

  return (
    <div className="px-3 lg:px-0">
        {/* HEADER */}
       <PageHeader
        title={`Portfolio Simulations`}
        description="Practice before you commit — Bayesian Monte Carlo projection"
      ></PageHeader>

      {/* HEADER */}
    

      {/* STATS */}
      <div className="bg-white/5 border-2 border-gray-100 mt-3 w-full rounded-2xl p-4">
        <h2 className="text-gray-800 font-bold text-sm md:text-md">
          Current Financial State
        </h2>

        {/* MOBILE: grid | DESKTOP: keep your flex feel */}
        <section className="grid grid-cols-2 gap-3 mt-4 lg:flex lg:gap-2">

          {[
            { title: "Free Cash", value: "₦26,500", color: "text-gray-800" },
            { title: "Stress Index", value: "34/100", color: "text-emerald-500" },
            { title: "Bayse Fear", value: "68%", color: "text-orange-400" },
            { title: "ZELTA Model", value: "54%", color: "text-emerald-500" },
          ].map((item, i) => (
            <div
              key={i}
              className="border-2 border-gray-100 bg-white rounded-2xl p-3 flex flex-col justify-center lg:w-[40%]"
            >
              <h3 className="text-gray-500 text-xs md:text-sm">
                {item.title}
              </h3>
              <p className={`font-bold text-lg md:text-xl ${item.color}`}>
                {item.value}
              </p>
            </div>
          ))}
        </section>
      </div>

      {/* SIMULATOR */}
      <section className="mt-3 bg-white border-2 border-gray-100 rounded-2xl p-4 lg:p-6">

        {/* HEADER */}
        <div className="flex gap-3 items-start">
          <div className="bg-green-100 rounded-full w-10 h-10 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-emerald-400" />
          </div>

          <div>
            <h1 className="text-gray-800 font-bold text-lg md:text-xl">
              Side Hustle Simulator
            </h1>
            <p className="text-gray-500 text-sm md:text-md">
              Catering business reinvestment projection
            </p>
          </div>
        </div>

        {/* INPUT */}
        <h3 className="text-gray-800 mt-6 font-bold text-sm md:text-base">
          How much do you want to invest?
        </h3>

        <input
          type="number"
          value={amount}
          placeholder={amountph}
          onChange={handleAmountChange}
          onFocus={() => setAmountPh("")}
          onBlur={() => setAmountPh("Enter amount (₦)")}
          className="bg-gray-100 w-full h-12 mt-2 px-4 outline-none rounded-2xl focus:ease-in-out
          focus:border-emerald-500 focus:border-2 focus:transition-all focus:duration-300"
        />

        <p className="text-gray-500 text-xs md:text-sm mt-1">
          Available free cash: ₦26,500 (after locked hostel fee)
        </p>

        {/* OPTIONS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-5">

          {[
            { title: "Time Horizon", value: "3 Weeks" },
            { title: "Business Type", value: "Catering" },
            { title: "Risk Level", value: "Moderate" },
          ].map((item, i) => (
            <div
              key={i}
              className="bg-gray-100/40 rounded-2xl p-4"
            >
              <h3 className="text-gray-500 font-bold text-xs md:text-sm">
                {item.title}
              </h3>
              <p className="text-gray-800 text-lg font-bold mt-1">
                {item.value}
              </p>
            </div>
          ))}
        </div>

        {/* BUTTON */}
        <button
          className="mt-5 w-full cursor-pointer hover:bg-emerald-400 
          h-12 bg-emerald-500 text-white font-bold rounded-2xl 
          flex items-center justify-center gap-2 transition-all"
        >
          <Sparkles className="w-5 h-5" />
          Run Bayesian Simulation
        </button>
      </section>

      {/* INFO */}
      <div className="border-2 border-gray-100 w-full mt-3 bg-white/5 rounded-2xl p-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-gray-500" />
          <h2 className="text-sm md:text-md font-bold text-gray-800">
            How Portfolio Simulation Works
          </h2>
        </div>

        <p className="text-gray-500 mt-2 text-xs md:text-sm leading-relaxed">
          ZELTA runs Bayesian Monte Carlo projections (1,000 simulations) using your side hustle variables.
          Kelly Criterion then sizes the safe allocation based on current Bayse crowd signals and your stress index.
          The simulation adjusts in real-time when Bayse market prices shift.
        </p>
      </div>

      {/* FLOATING BUTTON */}
      <button className="fixed bottom-6 right-6 bg-emerald-500 rounded-full w-14 h-14 z-50 flex items-center justify-center shadow-lg">
        <MessageSquare className="text-white w-5 h-5" />
      </button>
    </div>
  );
}

export default page;
