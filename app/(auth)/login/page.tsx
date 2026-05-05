"use client";

import { useAuth } from "@/context/authContext";
import LoginForm from "./LoginForm";

export default function Login() {
  const {
    email,
    password,
    setEmail,
    setPassword,
    handleLogin,
    authenticationError,
    loading,
  } = useAuth();

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <LoginForm
        email={email}
        password={password}
        setEmail={setEmail}
        setPassword={setPassword}
        handleLogin={handleLogin}
        authenticationError={authenticationError}
        loading={loading}
      />
    </main>
  );
}