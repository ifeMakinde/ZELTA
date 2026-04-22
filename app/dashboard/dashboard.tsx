"use client";
import { useSearchParams } from "next/navigation";
import PageHeader from "@/components/PageHeader";
import Widget from "@/components/widget";
import {
  TrendingDown,
  ArrowDownRight,
  Brain,
  Activity,
  TargetIcon,
} from "lucide-react";
import Button from "@/components/Button";

const time = new Date().toLocaleString("en-US", {
  hour: "numeric",
  minute: "numeric",
  hour12: true,
});

console.log(time);
function Dashboard() {
  const searchParam = useSearchParams();
  const name = searchParam.get("username");
  return (
    <section className="space-y-6">
      {/*  PAGE HEADER */}
      <PageHeader
        title={`${time.includes("AM") ? "Good Morning" : "Good Evening"},\n ${name}`}
        description="here's your financial intelligence for today"
      />

    
      
      {/*  DASHBOARD HOMEPAGE WIWDGET 3 */}
      {/* Add dashboard widgets and cards here. The dashboard layout splits sidebar 30% / content 70%. */}
      <Widget className="w-full p-3 lg:pl-10 rounded-2xl bg-orange-50 flex items-center gap-3 text-[#444]">
        {/* some data comes from backend here */}
        <span>
          <Activity color="orange" size={24} />
        </span>
        <p className="text-[14px] text-base font-semibold">
          Bayse Market USD/NGN crowd pricing 68% fear
        </p>
      </Widget>

      {/*  DASHBOARD HOMEPAGE WIWDGET 2 */}
      <Widget className="mt-4 bg-white flex flex-col justify-center p-10 w-full rounded-xl">
        {/* these data from backend, each stress level probably has an assigened % */}
        <div className="mb-4 flex flex-col gap-2">
          <div className="flex justify-between items-center">
            <p className="text-[#444] font-bold uppercase">
              {" "}
              student stress index
            </p>

            <span className="p-2 bg-[#d3f7eb] rounded-lg">
              <TrendingDown strokeWidth={2} size={28} color="green" />
            </span>
          </div>
          <h3 className="text-3xl lg:text-5xl font-bold text-[#10b981]">
            34/100
          </h3>
          <p className="p-2 rounded-xl uppercase bg-[#e7f8f2] w-[45%] sm:w-[30%] lg:w-[20%]  text-green-500 font-bold text-[14px] lg:text-base ">
            calm.moderate
          </p>
        </div>

        <div className="mt-6 text-[#444]">
          <span className="flex justify-between items-center">
            <p className="text-[#444] font-medium">Bayse Primary Signal</p>
            <p>
              {/* comes from API */}
              X%
            </p>
          </span>
          <progress
            value={34}
            max={100}
            className="w-full bg-transparent h-2.5 rounded-xl [&::-webkit-progress-bar]:bg-green-50 [&::-webkit-progress-value]:bg-green-500 [&::-webkit-progress-value]:rounded-xl"
          ></progress>

          <p className="text-[#444] text-[12px] lg:text-[14px] lg:max-w-[80%]">
            Nigerian financial markets are anxious right now. Bayse market crowd
            are pricing naira weakness at 68%. Your spending this week may be
            driven by fear, so be mindful of your financial decisions.
          </p>
        </div>

        <div className=" mt-6 w-full flex justify-evenly items-start gap-4 text-[#444] ">
          <div className="bg-white text-[#444] lg:p-4  p-2 rounded-xl w-[50%] lg:w-[70%]">
            <h4 className="font-semibold text-[#444]">Bayse Crowd</h4>
            <p className="text-orange-400">x%</p>
          </div>
          <div className="bg-white text-[#444] lg:p-4 p-2 rounded-xl w-[50%] lg:w-[70%]">
            <h4 className="font-semibold text-[#444]">Zelta Mode</h4>
            <p className="text-green-400">x%</p>
          </div>
        </div>
      </Widget>

      {/*  DASHBOARD HOMEPAGE WIWDGET 3 */}
      <Widget className="p-10 flex justify-self-auto gap-4 bg-orange-50 rounded-xl">
        <span className=" rounded-xl">
          <Brain strokeWidth={2} color="orange" size={30} />
        </span>

        <div className="flex flex-col gap-2">
          <p className=" text-[#444] font-bold">Active Bias Dectection</p>
          <h2 className="uppercase text-orange-400 font-bold text-2xl lg:text-4xl">
            loss detection
          </h2>

          <p className="text-[12px] lg:text-[14px] max-w-150">
            You withdraw ₦10,000 cash last Tuesday, that cash is sitting idle.
            Bayse crowd fear was 74% that day, Our model said 54%. Your hoarding
            was driven by market panic not real risk{" "}
          </p>
        </div>
      </Widget>

      {/* DASHBOARD HOME WODGET 4 */}

      <Widget className="mt-4 bg-white flex flex-col justify-center p-10 w-full rounded-xl">
        {/* these data from backend, each stress level probably has an assigened % */}

        <div className="flex justify-between items-center">
          <p className="text-[#444] font-bold uppercase">
            {" "}
            Decision Confidence Score
          </p>
          <span>
            <ArrowDownRight />
          </span>
        </div>

        <div className="mt-6 text-[#444]">
          <span className="flex justify-between items-center">
            <p className="text-[#444] font-medium">Rational</p>
            <p className=" font-bold">
              {/* comes from API */}
              X%
            </p>
          </span>
          <progress
            value={42} //get max and min value from api
            max={100}
            className="w-full bg-transparent h-2.5 rounded-xl [&::-webkit-progress-bar]:bg-gray-100 [&::-webkit-progress-value]:bg-green-500 [&::-webkit-progress-value]:rounded-xl"
          ></progress>
        </div>
        <div className="mt-6 text-[#444]">
          <span className="flex justify-between items-center">
            <p className="text-[#444] font-medium">Impulse</p>
            <p className="font-bold">
              {/* comes from API */}
              X%
            </p>
          </span>
          <progress
            value={58}
            max={100}
            className="w-full bg-transparent h-2.5 rounded-xl [&::-webkit-progress-bar]:bg-gray-100 [&::-webkit-progress-value]:bg-orange-400 [&::-webkit-progress-value]:rounded-xl"
          ></progress>
        </div>

        <div className=" bg-[#e7f8f2] mt-6 w-full rounded-2xl text-[#444] p-3 ">
          {/* compute confidence gap value from API */}
          <p className="text-[14px] lg:text-base">
            <span className="font-medium ">Confidence Gap: 16%</span> - ZELTA
            intervention is moderately urgent
          </p>
        </div>
      </Widget>

      {/* DASHBOARD HOME 5 */}
      <Widget className="p-10 mt-4 flex flex-col justify-center w-full rounded-xl bg-[#10b981]">
        <div className="flex gap-4 item-center">
          <span className="rounded-lg">
            <TargetIcon strokeWidth={2} color="orange" size={30} />
          </span>

          <div className="flex flex-col justify-center gap-2 text-white">
            <h2 className="uppercase font-bold text-[18px] ">
              {" "}
              ZELTA Weekly Verdict
            </h2>
            <p className="text-[14px] lg:text-base">
              Based on Bayse Market signal + Baysian engine + Kelly allocation
            </p>
          </div>
        </div>

        <div className="w-full lg:w-[80%] p-8 pl-0 bg-transparent mt-3 text-white">
          <h4 className="text-gray-100 uppercase text-[12px] mb-1  lg:text-[14px] ">
            recommendations
          </h4>

          <div className="">
            <h2 className="uppercase mb-2 text-white font-bold text-[24px] lg:text-[30px]">
              invest as low as ₦5,300
            </h2>

            <p className="text-[14px] lg:text-base tracking-wide lg:tracking-normal">
              the bayse crowd fear index fear hit 74% on Tuesday - that is what
              triggered your loss aversion. The real risk was 54%. Our
              simulation says ₦8000 generates a strong return, but your stress
              index is still 34%. kelly adjusted amount is ₦5300
            </p>
          </div>
        </div>

        <div className=" mt-6 w-full flex flex-col justify-center gap-4 text-white ">
          <div className="flex justify-center items-center gap-3 ">
            <div className="lg:p-4 p-2 rounded-xl w-[50%] lg:w-[70%] border border-gray-50">
              <h4 className="font-light  text-[14px] lg:text-[15px] uppercase tracking-wide text-gray-50 ">
                Save this week
              </h4>
              <p className="font-bold">₦X,000</p>
            </div>
            <div className="lg:p-4 p-2 text-[14px] lg:text-[15px] rounded-xl w-[50%] lg:w-[70%] border  border-gray-50">
              <h4 className="font-light uppercase tracking-wide text-gray-50 ">
                Hold Cash
              </h4>
              <p className="font-bold">₦X,000</p>
            </div>
          </div>

          <Button className="text-green-600 text-center p-2 rounded-xl w-full lg:w-[50%] mx-auto bg-white mb-5">
            Run Full Simulation
          </Button>
        </div>
      </Widget>
    </section>
  
    
  );
}

export default Dashboard;
