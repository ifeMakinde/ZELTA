import { Landmark, Users, Clock, TrendingDown, CheckCircle } from "lucide-react"
export default function Five(){
    return(
        <div>
            <div className="p-2 lg:p-0">
  <h2 className="text-2xl font-bold text-gray-800 ml-4 mt-5">
    Five Behavioral Biases Tracked
  </h2>

  {/* First Row - Stacks on mobile, side-by-side on lg */}
  <section className="flex flex-col lg:flex-row mt-3 justify-start lg:ml-5 gap-5">
    <div className="w-full h-auto lg:h-37 bg-white border border-orange-400/30 rounded-2xl pb-4 lg:pb-0">
      <div className="flex justify-start mt-5 ml-5 gap-2">
        <div className="bg-orange-100 w-10 h-10 rounded-full shrink-0">
          <TrendingDown className="relative w-5 h-5 text-orange-400 left-2.5 top-2" />
        </div>
        <h2 className="text-gray-800 font-bold">Loss Conversion</h2>
        <div className="bg-orange-100 font-bold text-orange-400 text-center px-3 lg:w-[15%] rounded-full h-6 text-sm flex items-center justify-center">
          ACTIVE
        </div>
      </div>

      <p className="text-gray-500 ml-17 text-sm relative lg:bottom-2 pr-4 lg:pr-0">
        Prioritizing avoiding losses over potential gains during Bayse
        <br className="hidden lg:block" /> fear spikes
      </p>

      <div className="flex justify-between lg:justify-start ml-17 pr-5 lg:pr-0">
        <p className="text-gray-500 text-sm">Current Strength</p>
        <p className="text-orange-400 font-bold text-sm lg:ml-55">72% HIGH</p>
      </div>
    </div>

    <div className="bg-white w-full h-auto lg:h-37 border-gray-100 border-2 rounded-2xl pb-4 lg:pb-0">
      <div className="flex justify-start mt-5 ml-5 gap-2">
        <div className="bg-gray-100 w-10 h-10 rounded-full shrink-0">
          <Clock className="relative w-5 h-5 text-gray-500 left-2.5 top-2.5" />
        </div>
        <h2 className="text-gray-800 font-bold">Present Bias</h2>
      </div>
      <p className="text-gray-500 ml-17 text-sm relative lg:bottom-2 pr-4 lg:pr-0">
        Tendency to prefer immediate rewards over delayed benefits
      </p>
      <div className="flex justify-between lg:justify-start ml-17 pr-5 lg:pr-0">
        <p className="text-gray-500 text-sm">Current Strength</p>
        <p className="text-gray-500 font-bold text-sm lg:ml-55">18% LOW</p>
      </div>
    </div>
  </section>

  {/* Second Row - Stacks on mobile, side-by-side on lg */}
  <section className="mt-5 lg:mt-3 flex flex-col lg:flex-row lg:ml-5 justify-start gap-5">
    <div className="bg-white w-full h-auto lg:h-37 border-gray-100 border-2 rounded-2xl pb-4 lg:pb-0">
      <div className="flex justify-start mt-5 ml-5 gap-2">
        <div className="bg-gray-100 w-10 h-10 rounded-full shrink-0">
          <CheckCircle className="relative w-5 h-5 text-gray-500 left-2.5 top-2.5" />
        </div>
        <h2 className="text-gray-800 font-bold">Overconfidence</h2>
      </div>
      <p className="text-gray-500 ml-17 text-sm relative lg:bottom-2 pr-4 lg:pr-0">
        Overestimating ability to predict outcomes when stress is low
      </p>
      <div className="flex justify-between lg:justify-start ml-17 pr-5 lg:pr-0">
        <p className="text-gray-500 text-sm">Current Strength</p>
        <p className="text-gray-500 font-bold text-sm lg:ml-55">12% LOW</p>
      </div>
    </div>

    <div className="bg-white w-full h-auto lg:h-37 border-gray-100 border-2 rounded-2xl pb-4 lg:pb-0">
      <div className="flex justify-start mt-5 ml-5 gap-2">
        <div className="bg-gray-100 w-10 h-10 rounded-full shrink-0">
          <Users className="relative w-5 h-5 text-gray-500 left-2.5 top-2.5" />
        </div>
        <h2 className="text-gray-800 font-bold">Herd Behavior</h2>
      </div>
      <p className="text-gray-500 ml-17 text-sm relative lg:bottom-2 pr-4 lg:pr-0">
        Following peer decisions without independent analysis
      </p>
      <div className="flex justify-between lg:justify-start ml-17 pr-5 lg:pr-0">
        <p className="text-gray-500 text-sm">Current Strength</p>
        <p className="text-gray-500 font-bold text-sm lg:ml-55">24% LOW</p>
      </div>
    </div>
  </section>

  {/* Fifth Bias - Full width original design */}
  <div className="bg-white w-full lg:w-[98%] lg:ml-5 mt-5 lg:mt-3 h-auto lg:h-37 border-gray-100 border-2 rounded-2xl pb-4 lg:pb-0">
    <div className="flex justify-start mt-5 ml-5 gap-2">
      <div className="bg-gray-100 w-10 h-10 rounded-full shrink-0">
        <Landmark className="relative w-5 h-5 text-gray-500 left-2.5 top-2.5" />
      </div>
      <h2 className="text-gray-800 font-bold">Mental Accounting</h2>
    </div>
    <p className="text-gray-500 ml-17 text-sm relative lg:bottom-2 pr-4 lg:pr-0">
      Treating money differently based on source (parents vs side hustle vs bursary)
    </p>
    <div className="flex justify-between lg:justify-start ml-17 pr-5 lg:pr-0">
      <p className="text-gray-500 text-sm">Current Strength</p>
      <p className="text-gray-500 font-bold text-sm lg:ml-170">31% MODERATE</p>
    </div>
  </div>
</div>
        </div>
    )
}