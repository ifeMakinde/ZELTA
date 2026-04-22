"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginForm() {
  const navigate = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <section className=" w-full md:w-[50%] lg:w-[40%] xl:w-[25%] mx-auto p-6 rounded-xl flex flex-col justify-center items-between  pt-2 ">
      <h1 className="text-[22px] font-semibold mb-4 text-center ">
        Welcome Back!
      </h1>

      <form
        className="space-y-4 flex flex-col justify-center "
        onSubmit={(event) => {
          event.preventDefault();
          // send login information to backend, if successful, navigate to dashboard, if not, show error message. For now, we'll just navigate to dashboard.
          if (!email || !password) {
            alert("Please enter both email and password");
            return;
          }
          navigate.push("/form");
        }}
      >
        <label className="block text-md font-medium">
          Email
          <input
            type="email"
            value={email}
            onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
              setEmail(event.target.value)
            }
            className=" w-full mt-1 block rounded-lg border border-gray-300 px-8 py-1.5 focus:border-green-500 focus:outline-none"
            placeholder="you@gmail.com"
          />
        </label>

        <label className="block text-md font-medium">
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full mt-1 block rounded-lg text-start border border-gray-300 px-8 py-1.5 focus:border-green-500 focus:outline-none"
            placeholder="Enter your password"
          />
        </label>

        <button
          // type="submit"
          className="rounded-xl bg-[#10b981] text-white px-6 py-2 hover:bg-[#0b825a]"
        >
          Continue
        </button>
      </form>
    </section>
  );
}
