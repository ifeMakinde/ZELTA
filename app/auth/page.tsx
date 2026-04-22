"use client";

import { useState } from "react";
import LoginForm from "./LoginForm";
import SignUpForm from "./SignUpForm";

export default function AuthPage() {
  // add google auth later and remove default state login. maybe diffrent pages instead of components
  const [isLogin, setIsLogin] = useState(true);

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-10">
      {/* flex flex-col items-center */}
      {/* <div> */}
      {isLogin ? <LoginForm /> : <SignUpForm />}

      <p className="text-center text-sm text-gray-600">
        {isLogin ? "Don't have an account? " : "Already have an account? "}
        <button
          onClick={() => setIsLogin(!isLogin)}
          className="text-green-800 font-semibold hover:underline cursor-pointer"
        >
          {isLogin ? "Sign up" : "Sign In"}
        </button>
      </p>
      {/* </div> */}
    </main>
  );
}
