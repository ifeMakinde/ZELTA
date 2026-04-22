import { Suspense } from "react";
import PageHeader from "@/components/PageHeader"; 
import Dashboard from "@/app/dashboard/dashboard";

const time = new Date().toLocaleString("en-US", {
  hour: "numeric",
  minute: "numeric",
  hour12: true,
});


function Page() {
  return (
<section className="space-y-6">
      {/*  PAGE HEADER */}
      <PageHeader
        title={`${time.includes("AM") ? "Good Morning" : "Good Evening"},\n ${name}`}
        description="here's your financial intelligence for today"
      />
 <Suspense fallback={<div>Loading dashboard...</div>}>
        <Dashboard/>
        </Suspense>
 </section>
  );
}

export default Page;
