import { Activity } from "lucide-react";
export default function Bayse(){
    return(
        <div>
           <section className="w-full h-auto lg:h-45 bg-orange-200/20 border-orange-400/30 border mt-5 rounded-2xl p-5 lg:p-0">
  <div className="flex flex-col lg:flex-row justify-start lg:ml-5 lg:mt-7 gap-3">
    {/* Icon Container */}
    <div className="bg-orange-200 w-10 h-10 rounded-full shrink-0">
      <Activity className="relative w-5 h-5 text-orange-400 left-2.5 top-2" />
    </div>

    {/* Content Area */}
    <div className="w-full">
      <h2 className="text-gray-800 font-bold text-lg">Bayse vs ZELTA Model</h2>
      
      {/* Stats Container - Mobile Stack / LG original gap */}
      <div className="flex flex-col sm:flex-row justify-start gap-8 lg:gap-40 mt-4 lg:mt-0">
        <div>
          <p className="text-gray-500 mt-2 font-light text-sm">Bayse Crowd Fear(Tuesday)</p>
          <p className="text-orange-400 font-bold text-3xl">74%</p>
        </div>

        <div className="lg:ml-40">
          <p className="text-gray-500 mt-2 font-light text-sm">ZELTA Relational Model</p>
          <p className="text-green-500 font-bold text-3xl">54%</p>
        </div>
      </div>
    </div>
  </div>

  {/* Description - Alignment adjusted for mobile flow */}
  <p className="text-gray-500 mt-4 lg:mt-2.5 lg:ml-17 text-sm sm:text-xs">
    The Bayse crowd was 14% more fearful than the data warranted. This is the behavioral panic gap that ZELTA corrects.
  </p>
</section>
        </div>
    )

}