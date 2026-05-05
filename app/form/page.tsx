"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Button from "@/components/Button";
import { apiFetch } from "@/hooks/useFetch";

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

const RISK_MAP: Record<string, "low" | "moderate" | "high"> = {
  Conservative: "low",
  Moderate: "moderate",
  Aggressive: "high",
};

function Page() {
  const navigate = useRouter();
  const [name, setName] = useState("");
  const [selectedOptions, setSelectedOptions] = useState<Record<number, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSelect = (sectionId: number, option: string) => {
    setSelectedOptions((prev) => ({ ...prev, [sectionId]: option }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      // Save onboarding data to the profile before entering dashboard
      await apiFetch("/api/profile", {
        method: "PATCH",
        body: JSON.stringify({
          name: name.trim() || undefined,
          financial: {
            capital_range: selectedOptions[0] || null,
            risk_tolerance: RISK_MAP[selectedOptions[1]] ?? "moderate",
          },
          preferences: {
            primary_goal: selectedOptions[2] || null,
          },
        }),
      });
    } catch {
      // Non-fatal — profile can be filled in later from the Profile page
      console.warn("[Form] Could not save onboarding profile, continuing...");
    } finally {
      setSubmitting(false);
      navigate.push("/dashboard");
    }
  };

  return (
    <section className="min-h-screen mx-auto w-[90%] md:w-[40%] lg:w-[30%] space-y-5">
      <div className="mt-4 p-3 text-center">
        <h2 className="font-bold text-[22px] lg:text-[26px] text-[#10b981] pb-1">
          ZELTA
        </h2>
        <p className="text-[14px] lg:text-base tracking-wide">
          {`Let's get to know you`}
        </p>
      </div>

      <form className="w-full text-start" onSubmit={handleSubmit}>
        <div className="mb-4">
          <h4 className="mb-1 font-semibold">Your Name</h4>
          <input
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter your name"
            className="w-full py-1.5 px-10 bg-transparent border border-gray-300 focus:border-green-500 focus:outline-none rounded-xl focus:outline-green-300"
          />
        </div>

        {formSections.map((section, idx) => (
          <div key={idx} className="mb-4">
            <h3 className="mb-1 font-semibold text-[14px] lg:text-base">
              {section.heading}
            </h3>
            <ul className="flex flex-col justify-center gap-2.5 w-full font-medium text-[14px]">
              {section.options.map((option, optIdx) => {
                const isActive = selectedOptions[section.id] === option;
                return (
                  <li
                    key={optIdx}
                    onClick={() => handleSelect(section.id, option)}
                    className={`cursor-pointer rounded-xl py-1.5 px-8 bg-gray-50 border transition-colors ${
                      isActive
                        ? "border-green-500 bg-green-50 text-green-700 font-semibold"
                        : "border-gray-300"
                    }`}
                  >
                    {option}
                  </li>
                );
              })}
            </ul>
          </div>
        ))}

        {error && (
          <p className="text-red-500 text-sm mb-3">{error}</p>
        )}

        <Button
          className="bg-[#10b981] text-center p-2 rounded-xl w-full text-white mb-4 disabled:opacity-50"
          disabled={submitting}
        >
          {submitting ? "Saving..." : "Continue to Dashboard"}
        </Button>
      </form>
    </section>
  );
}

export default Page;