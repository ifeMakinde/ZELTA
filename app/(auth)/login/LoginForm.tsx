"use client";

import { useRouter } from "next/navigation";
import Button from "@/components/Button";

interface Props {
  email: string;
  setEmail: React.Dispatch<React.SetStateAction<string>>;
  password: string;
  setPassword: React.Dispatch<React.SetStateAction<string>>;
  handleLogin: (event: React.FormEvent<HTMLFormElement>) => Promise<void>;
  authenticationError: string | null;
}

export default function LoginForm({
  email,
  setEmail,
  password,
  setPassword,
  handleLogin,
  authenticationError,
}: Props) {
  const router = useRouter();

  return (
    <section className="mx-auto flex w-full flex-col items-center justify-center rounded-xl p-6 pt-2 md:w-[50%] lg:w-[40%] xl:w-[25%]">
      <h1 className="mb-4 text-center text-[22px] font-semibold">
        Welcome Back!
      </h1>

      <form className="flex flex-col justify-center space-y-4" onSubmit={handleLogin}>
        <label className="block text-md font-medium">
          Email
          <input
            type="email"
            value={email}
            onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
              setEmail(event.target.value)
            }
            className="mt-1 block w-full rounded-lg border border-gray-300 px-8 py-1.5 focus:border-green-500 focus:outline-none"
            placeholder="you@gmail.com"
          />
        </label>

        <label className="block text-md font-medium">
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 block w-full rounded-lg border border-gray-300 px-8 py-1.5 text-start focus:border-green-500 focus:outline-none"
            placeholder="Enter your password"
          />
        </label>

        {authenticationError && (
          <div>
            <p className="text-center text-[14px] text-red-500">
              {authenticationError}
            </p>
          </div>
        )}

        <Button
          type="submit"
          className="rounded-xl bg-[#10b981] px-6 py-2 text-white hover:bg-[#0b825a]"
        >
          Continue
        </Button>

        <div className="text-center">
          <p>
            New?{" "}
            <Button
              type="button"
              className="text-green-600"
              onClick={() => router.push("/sign-up")}
            >
              Sign up
            </Button>
          </p>
        </div>
      </form>
    </section>
  );
}