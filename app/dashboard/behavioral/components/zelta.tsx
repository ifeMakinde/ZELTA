import { Brain, MessageSquare } from "lucide-react";
export default function Zelta(){
    return(
        <div>
            <div className="w-full lg:w-[98%] h-auto lg:h-50 mt-3 lg:ml-5 border-green-400/30 border bg-green-50 rounded-2xl pb-6 lg:pb-0">
  {/* Header */}
  <div className="ml-5 lg:ml-7 mt-5 flex justify-start gap-2">
    <Brain className="w-3 h-3 text-green-400 mt-2 shrink-0" />
    <h2 className="font-bold text-gray-800 text-lg">ZELTA Recommendation</h2>
  </div>

  {/* Description */}
  <p className="text-gray-500 ml-5 lg:ml-12 mt-2 text-md pr-4 lg:pr-0">
    Your loss aversion is being triggered by Bayse crowd fear spikes that don't match actual risk. 
    When you see Bayse signals above 70%,<br className="hidden lg:block" />
    wait 24 hours before making cash withdrawal decisions. The crowd panic typically corrects within 48 hours.
  </p>
  {/* Tags - Wraps on mobile, stays exact % on lg */}
  <div className="flex flex-wrap lg:flex-row gap-2 mt-4 lg:mt-3 ml-5 lg:ml-12 pr-4 lg:pr-0">
    <div className="w-auto lg:w-[17.5%] h-6 px-3 lg:px-0 rounded-full bg-green-100 font-bold text-green-400 text-sm flex items-center">
      <span className="lg:ml-2 whitespace-nowrap">Bayse-Aware Decisions</span>
    </div>
    
    <div className="w-auto lg:w-[11%] h-6 px-3 lg:px-0 bg-green-100 rounded-full font-bold text-green-400 text-sm flex items-center">
      <span className="lg:ml-2 whitespace-nowrap">24-Hour Rule</span>
    </div>
    
    <div className="w-auto lg:w-[21%] h-6 px-3 lg:px-0 bg-green-100 rounded-full text-green-400 font-bold text-sm flex items-center">
      <span className="lg:ml-2 whitespace-nowrap">Loss Aversion Management</span>
    </div>
  </div>

  {/* Floating Button */}
  <button className="fixed bottom-10 right-5 lg:right-10 bg-emerald-500 rounded-full w-12 h-12 lg:w-15 lg:h-15 z-50 flex items-center justify-center shadow-lg">
    <MessageSquare className="text-white w-4 h-4 lg:w-5 lg:h-5" />
  </button>
</div>
            
                   </div>
                   
    )
}