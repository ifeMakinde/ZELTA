import { Suspense } from "react";
//import PageHeader from "@/components/PageHeader"; 
import Dashboard from "@/app/dashboard/dashboard";

function Page() {
  return (
<section className="space-y-6">
 <Suspense fallback={<div>Loading dashboard...</div>}>
        <Dashboard/>
        </Suspense>
 </section>
  );
}

export default Page;
