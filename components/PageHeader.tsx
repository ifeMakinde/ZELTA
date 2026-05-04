"use client";
import React from "react";
// import Button from "./Button";

interface PageHeaderProps {
  title: string;
  description: string;
  children?: React.ReactNode;
}

function PageHeader({ title, description, children }: PageHeaderProps) {
  return (
    <div className={`flex justify-between `}>
      <div>
        <h2 className="font-bold text-2xl xl:text-4xl md:text-3xl lg:text-4xl">
          {title}
        </h2>
        <p className="text-[#444] text-[14px] lg:text-base md:text-lg mt-1 ">
          {description}
        </p>
      </div>
      {children}
    </div>
  );
}

export default PageHeader;
