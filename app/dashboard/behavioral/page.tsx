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
       <PageHeader
        title={`Behavioral Snapshot`}
        description="Deep dive into your behavioral bias patterns"
      ></PageHeader>

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
