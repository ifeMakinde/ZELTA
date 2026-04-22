import React from "react";
// import PagesHeading from "./PagesHeading";

interface PageHeaderProps {
  title: string;
  description: string;
}

function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <div>
      <h2 className="text-[22px] lg:text-3xl font-bold xl:text-4xl">{title}</h2>
      <p className="text-[#444] text-[14px] lg:text-base md:text-lg mt-1 ">
        {description}
      </p>
    </div>
  );
}

export default PageHeader;
