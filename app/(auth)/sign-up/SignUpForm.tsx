"use client";
import Button from "@/components/Button";
import { useRouter } from "next/navigation";

interface Props {
  email: string;
  setEmail: React.Dispatch<React.SetStateAction<string>>;
  password: string;
  setPassword: React.Dispatch<React.SetStateAction<string>>;
  handleSignUp: (event: React.FormEvent<HTMLFormElement>) => Promise<void>;
  authenticationError: string | null;
  loading: boolean;
}

export default function SignUpForm({
  email,
  password,
  setEmail,
  setPassword,
  handleSignUp,
  authenticationError,
  loading,
}: Props) {
  const navigate = useRouter();

  return (
    <section className=" w-[80%] md:w-[50%] lg:w-[40%] xl:w-[25%] mx-auto p-6 rounded-xl flex flex-col justify-center items-between  pt-2 ">
      <h1 className="text-[22px] font-semibold mb-4 text-center">
        Create An Account
      </h1>

      <form
        className="space-y-4 flex flex-col justify-center "
        onSubmit={handleSignUp}
      >
        <label className="block text-md font-medium">
          Email
          <input
            type="email"
            value={email}
            onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
              setEmail(event.target.value)
            }
            className="mt-1 block w-full rounded-lg border border-gray-300 px-8 py-2 focus:border-green-500 focus:outline-none"
            placeholder="you@gmail.com"
          />
        </label>

        <label className="block text-md font-medium">
          Password
          <input
            type="password"
            value={password}
            onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
              setPassword(event.target.value)
            }
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-green-500 focus:outline-none"
            placeholder="Create a password"
          />
        </label>

        {authenticationError && (
          <div className="error-message">
            <p className="text-red-500 text-center text-[14px]">
              {authenticationError}
            </p>
          </div>
        )}

        <Button
          className="w-full rounded-xl bg-[#10b981] text-white px-4 py-2 hover:bg-[#0b825a] disabled:opacity-50"
          disabled={loading}
        >
          {loading ? "Creating account..." : "Sign Up"}
        </Button>

        <div className="text-center">
          <p>
            Have an account ?{" "}
            <Button
              className="text-green-600"
              onClick={() => {
                navigate.push("/login");
              }}
            >
              Sign In{" "}
            </Button>
          </p>
        </div>
      </form>
    </section>
  );
}