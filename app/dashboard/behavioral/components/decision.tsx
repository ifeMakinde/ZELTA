import { Brain } from "lucide-react";
export default function Decision(){
    return(
        <div>
            <div className="w-full mt-3 h-auto lg:h-108 bg-white border-gray-100 border-2 rounded-2xl pb-6 lg:pb-0">
  {/* Header Section */}
  <div className="flex justify-start gap-1">
    <div className="bg-green-100 w-10 h-10 mt-7 relative left-5 rounded-full shrink-0">
      <Brain className="relative w-5 h-5 text-green-400 left-2.5 top-2" />
    </div>
    <div className="mt-7 ml-7">
      <h2 className="text-gray-800 font-bold text-lg">Decision Confident Score</h2>
      <p className="text-gray-500 text-md">Current rational vs behavioral split</p>
    </div>
  </div>

  {/* Cards Container - Stacked on mobile, side-by-side on lg */}
  <section className="flex flex-col lg:flex-row justify-center items-center mt-10 gap-5 px-4 lg:px-0">
    
    {/* Rational Card */}
    <div className="w-full lg:w-115 h-auto lg:h-35 bg-green-50 rounded-2xl pb-4 lg:pb-0">
      <span className="flex justify-between lg:justify-start mt-5 px-5 lg:px-0 lg:ml-5">
        <h2 className="text-gray-800 font-bold text-md">Rational</h2>
        <p className="text-green-600 font-bold lg:ml-65 text-4xl">58%</p>
      </span>
      <div className="w-[90%] lg:w-[86%] h-3 mx-auto lg:ml-4 mt-3 bg-green-100 rounded-full">
        <div className="w-[50%] h-3 bg-[#10b981] rounded-l-full"></div>
      </div>
      <p className="text-gray-500 mt-3 ml-5 text-md pr-4 lg:pr-0">
        Decisions based on Bayesian model & kelly sizing
      </p>
    </div>

    {/* Behavioral Card */}
    <div className="w-full lg:w-115 h-auto lg:h-35 bg-orange-50 rounded-2xl pb-4 lg:pb-0">
      <span className="flex justify-between lg:justify-start mt-5 px-5 lg:px-0 lg:ml-5">
        <h2 className="text-gray-800 flex justify-start font-bold gap-1 text-md">
          Behavioral <span>Impulse</span>
        </h2>
        <p className="text-green-600 font-bold lg:ml-50 text-4xl">42%</p>
      </span>
      <div className="w-[90%] lg:w-[90%] h-3 mx-auto lg:ml-4 mt-3 bg-green-100 rounded-full">
        <div className="w-[40%] h-3 bg-[#10b981] rounded-l-full"></div>
      </div>
      <p className="text-gray-500 mt-3 ml-5 text-sm pr-4 lg:pr-0">
        Driven by stress, fear and market panic
      </p>
    </div>
  </section>

  {/* Confidence Gap Footer */}
  <div className="bg-orange-200/20 border-orange-400/30 border w-[92%] lg:w-[94%] mx-auto lg:ml-7 mt-10 h-auto lg:h-25 rounded-2xl pb-4 lg:pb-0">
    <div className="flex flex-row">
      <div className="border-orange-300 border-2 mt-5 ml-5 rounded-full text-orange-300 w-5 h-5 flex items-center justify-center shrink-0">
        <span className="text-sm font-bold">!</span>
      </div>
      <h1 className="text-gray-800 font-bold relative top-5 ml-2">
        Confidence Gap: 16%
      </h1>
    </div>

    <p className="text-gray-500 ml-5 mt-7 lg:mt-2 text-sm pr-4 lg:pr-0">
      |rational recommendation - behavioral impulse| = 
      <span className="font-bold text-gray-800"> where ZELTA adds the most value.</span> 
      Your decisions are being moderately influenced by Bayse crowd
      <br className="hidden lg:block" /> fear. ZELTA intervention is urgent.
    </p>
  </div>
</div>
        </div>
    )
}