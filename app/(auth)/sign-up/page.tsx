"use client";

import SignUpForm from "./SignUpForm";
import { useAuth } from "@/context/authContext";

function Signup() {
  const { email, password, setEmail, setPassword, handleSignUp, authenticationError, loading } = useAuth();
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-10">
      {
        <SignUpForm
          email={email}
          password={password}
          setEmail={setEmail}
          setPassword={setPassword}
          handleSignUp={handleSignUp}
          authenticationError={authenticationError}
          loading={loading}
        />
      }
    </div>
  );
}

export default Signup;