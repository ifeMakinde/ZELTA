"use client";
import React from "react";
import { useRouter } from "next/navigation";
import PageHeader from "@/components/PageHeader";
export default function NotFound(){
    const navigate = useRouter();
    React.useEffect(() => {
     const timer =  setTimeout(() => {
         navigate.replace("/dashboard/simulations")
      }, 3000);
      return () => clearTimeout(timer)
    }, [navigate])
    return(
        <div style={{backgroundColor: "rgb(249, 250, 251)", fontSize: "40px"}} 
        className="text-gray-800 flex justify-center min-h-screen font-bold translate-y-50">
         <PageHeader title="Ooops: 404-Page Not Found"
         description= "Redirecting in 3 seconds..." />
        </div>
    )
}