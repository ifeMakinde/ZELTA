"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Button from "@/components/Button";

interface FormSection {
  id: number;
  heading: string;
  options: string[];
}

const formSections: FormSection[] = [
  {
    id: 0,
    heading: "Available Capital",
    options: ["₦0 - ₦10,000", "₦10,000 - ₦50,000", "₦50,000+"],
  },
  {
    id: 1,
    heading: "Risk Preference",
    options: ["Conservative", "Moderate", "Aggressive"],
  },
  {
    id: 2,
    heading: "Primary Goal",
    options: ["Build savings", "Generate Income", "Grow Wealth"],
  },
];

function Page() {
  const navigate = useRouter();
  const [name, setName] = useState("");
  const [selectedOptions, setSelectedOptions] = useState<
    Record<number, string>
  >(() => {
    return {};
  });

  const handleSelect = (sectionId: number, option: string) => {
    setSelectedOptions((prev) => ({
      ...prev,
      [sectionId]: option,
    }));
    console.log("Selected Options:", {
      ...selectedOptions,
      [sectionId]: option,
    });

    // options need to go to backend to generate personalized dashboard, so we can navigate to dashboard immediately after selection, or we can have a submit button that navigates to dashboard and sends data to backend. For now, we'll navigate immediately after selection.
  };

  return (
    <section className=" min-h-screen mx-auto w-[90%] md:w-[40%] lg:w-[30%] flex flex-col justify-center items-center ">
      <div className="mt-6 p-4 text-center ">
        <h2 className="font-bold text-[22px] lg:text-[26px] text-green-500 pb-1">
          {" "}
          ZELTA
        </h2>
        <p className="text-[14px] lg:text-base tracking-wide ">
          {`Let's get to know you`}
        </p>
      </div>

      <form
        action=""
        className="w-full text-start  "
        onSubmit={(e: React.FormEvent<HTMLFormElement>) => {
          e.preventDefault();

          navigate.push("/dashboard");
        }}
      >
        <div className="mb-6">
          <h4 className="mb-1 font-semibold ">Your Name</h4>
          <input
            type="text"
            required
            value={name}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
              setName(e.target.value);
            }}
            placeholder="Enter your name"
            className="w-full py-1.5 px-10 bg-transparent border border-gray-300 focus:border-green-500 focus:outline-none rounded-xl focus:outline-green-300  "
          />
        </div>

        {formSections.map((section, idx) => (
          <div key={idx} className="mb-6">
            <h3 className="mb-1 font-semibold text-[14px] lg:text-base">
              {section.heading}
            </h3>
            <ul className="flex flex-col justify-center gap-2.5 w-full font-medium text-[14px] ">
              {section.options.map((option, optIdx) => {
                const isActive = selectedOptions[section.id] === option;
                return (
                  <li
                    key={optIdx}
                    onClick={() => handleSelect(section.id, option)}
                    className={`cursor-pointer rounded-xl py-1.5 px-8 bg-gray-50 border border-gray-300 transition-colors dark:bg-transparent dark:border  ${
                      isActive
                        ? "list-disc marker:text-green-400 "
                        : "list-none  "
                    }`}
                  >
                    {option}
                  </li>
                );
              })}
            </ul>
          </div>
        ))}

        <Button className="bg-green-600 text-center p-2 rounded-xl w-full text-white mb-4">
          Continue to Dashboard
        </Button>
      </form>
    </section>
  );
}

export default Page;
