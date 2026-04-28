 import React from "react"; 
import PageHeader from "@/components/PageHeader";
import { MessageSquareQuote, Brain , TrendingDown, Clock, CheckCircle, Landmark, Users,
  MessageSquare
 } from "lucide-react";
import Bayse from "./components/bayse";
import Active from "./components/active";
import Decision from "./components/decision";
import Five from "./components/five";
import Weeks from "./components/weeks";
import Zelta from "./components/zelta";
function page() {
  return (
      <div>
       <section>
  <PageHeader
    title={
      <span className="font-bold text-gray-800 text-2xl sm:text-3xl lg:text-4xl">
        Behavioral Snapshot
      </span>
    }
    description={
      <span className="font-light text-gray-500 text-sm sm:text-base">
        Deep dive into your behavioral bias patterns
      </span>
    }
  />
</section>

       <Bayse/>

       <Active/>

       <Decision/>

        <Five/>

        <Weeks/>

        <Zelta/>
       
    </div>
    
  );
}

export default page;