import { MessageSquareQuote } from "lucide-react";
export default function Active(){
     return(
        <div>
    <div className="p-2 lg:p-0">
      <section
        className="w-full mt-5 h-auto lg:h-143 bg-orange-200/20 border-orange-400/30 border
    rounded-2xl pb-6 lg:pb-0"
      >
        {/* Header Section */}
        <div className="flex justify-start ml-4 lg:ml-7 mt-7 gap-3">
          <div className="bg-orange-200 w-10 h-10 rounded-2xl shrink-0">
            <MessageSquareQuote className="relative w-5 h-5 text-orange-400 left-2.5 top-2" />
          </div>
          <div>
            <h2 className="text-gray-800 font-bold text-lg">Active Bias Detected</h2>
            <p className="text-sm text-gray-500">Based on Biase signals + wallet patterns</p>
          </div>
        </div>

        {/* Main Card */}
        <div className="w-[94%] mx-auto lg:mx-0 h-auto lg:h-85 bg-white rounded-2xl mt-5 lg:ml-7 pb-6 lg:pb-0">
          <h1 className="text-3xl lg:text-4xl text-orange-400 ml-5 relative top-5 font-bold uppercase">
            Loss Aversion
          </h1>
          <p className="text-gray-500 text-md mt-10 lg:mt-7 ml-5 pr-4 lg:pr-0">
            You withdrew ₦10,000 cash last Tuesday during a stress spike. That cash is sitting idle.
            Bayse crowd fear was 74% that day — our<br className="hidden lg:block" />
            model said 54%. <span className="font-bold text-gray-800">The crowd was wrong</span>. 
            Your hoarding was driven by market panic, not real risk.
          </p>

          {/* Progress Label */}
          <div className="flex justify-between lg:justify-start ml-5 mt-6 lg:mt-3 lg:gap-40 pr-5 lg:pr-0">
            <p className="text-gray-500">Bias Strength</p>
            <p className="text-orange-400 font-bold text-sm lg:ml-145">HIGH</p>
          </div>

          {/* Progress Bar */}
          <div className="w-[90%] lg:w-[94%] h-3 mx-auto lg:ml-5 bg-green-100 rounded-full mt-2">
            <div className="w-[70%] h-3 bg-[#10b981] rounded-full"></div>
          </div>

          {/* Transaction Evidence Box */}
          <div className="w-[92%] lg:w-[95%] h-auto lg:h-35 bg-orange-200/20 border-orange-400/30 border mt-5 lg:mt-3 mx-auto lg:ml-5 rounded-2xl pb-4 lg:pb-0">
            <h2 className="text-gray-800 font-bold text-sm ml-5 mt-5">Evidence from Transactions</h2>
            
            <div className="space-y-2 mt-2">
              <div className="flex justify-start gap-2 ml-5">
                <div className="border-orange-300 rounded-full border-2 text-orange-300 w-5 h-5 flex items-center justify-center shrink-0">
                  <span className="text-sm leading-none mb-1">x</span>
                </div>
                <p className="text-gray-500 text-sm">Tuesday: Withdrew ₦10,000 cash during Bayse fear spike (74%)</p>
              </div>
              <div className="flex justify-start gap-2 ml-5">
                <div className="border-orange-300 border-2 rounded-full text-orange-300 w-5 h-5 flex items-center justify-center shrink-0">
                  <span className="text-sm leading-none mb-1">x</span>
                </div>
                <p className="text-gray-500 text-sm">Stress-spending detected: ₦2,400 above normal on food/transport</p>
              </div>
              <div className="flex justify-start gap-2 ml-5">
                <div className="border-orange-300 border-2 rounded-full text-orange-300 w-5 h-5 flex items-center justify-center shrink-0">
                  <span className="text-sm leading-none mb-1">x</span>
                </div>
                <p className="text-gray-500 text-sm">Hoarding cash under mattress instead of productive allocation</p>
              </div>
            </div>
          </div>
        </div>

        {/* Correction Box */}
        <div className="bg-white w-[94%] mx-auto lg:mx-0 lg:ml-7 mt-5 h-auto lg:h-25 rounded-2xl p-5 lg:p-0">
          <h1 className="text-gray-800 font-bold lg:relative lg:top-2 lg:ml-5">
            ZELTA Correction Applied:
          </h1>
          <p className="text-gray-500 text-sm mt-3 lg:ml-5">
            You're 2.8× more sensitive to losses than gains right now. ZELTA will cap your side hustle reinvestment 
            at 25% of free cash when stress is HIGH (60+)<br className="hidden lg:block" />
            and recommend protective allocations until Bayse signals calm.
          </p>
        </div>
      </section>
    </div>
    </div>
)
}