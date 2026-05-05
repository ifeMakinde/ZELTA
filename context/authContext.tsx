"use client";

import React, { createContext, useContext, useState } from "react";
import { useRouter } from "next/navigation";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
} from "firebase/auth";
import { getFirebaseAuth } from "../firebase/index";

type AuthContextType = {
  email: string;
  setEmail: React.Dispatch<React.SetStateAction<string>>;
  password: string;
  setPassword: React.Dispatch<React.SetStateAction<string>>;
  handleLogin: (event: React.FormEvent<HTMLFormElement>) => Promise<void>;
  handleSignUp: (event: React.FormEvent<HTMLFormElement>) => Promise<void>;
  authenticationError: string | null;
  loading: boolean;
};

const AuthContext = createContext<AuthContextType | null>(null);

function AuthProvider({ children }: { children: React.ReactNode }) {
  const navigate = useRouter();
  const auth = getFirebaseAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authenticationError, setAuthenticationError] = useState<string | null>(
    null
  );
  const [loading, setLoading] = useState(false);

  const clearErrorLater = (ms: number = 2500) => {
    window.setTimeout(() => setAuthenticationError(null), ms);
  };

  const handleSignUp = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!auth) {
      setAuthenticationError("Firebase auth is not initialized.");
      clearErrorLater();
      return;
    }

    setLoading(true);
    setAuthenticationError(null);

    try {
      const response = await createUserWithEmailAndPassword(auth, email, password);
      if (response.user) {
        navigate.push("/form");
        return;
      }
    } catch (error: unknown) {
      const firebaseError = error as { code?: string };

      if (firebaseError.code === "auth/email-already-in-use") {
        setAuthenticationError("This email is already in use.");
      } else if (firebaseError.code === "auth/weak-password") {
        setAuthenticationError("Password is too weak.");
      } else if (firebaseError.code === "auth/invalid-email") {
        setAuthenticationError("Please enter a valid email address.");
      } else {
        setAuthenticationError("Unable to create account. Please try again.");
      }

      clearErrorLater();
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!auth) {
      setAuthenticationError("Firebase auth is not initialized.");
      clearErrorLater();
      return;
    }

    setLoading(true);
    setAuthenticationError(null);

    try {
      const response = await signInWithEmailAndPassword(auth, email, password);

      if (response.user) {
        navigate.push("/form");
        return;
      }

      setAuthenticationError("Please enter a valid email and password.");
      clearErrorLater(2000);
    } catch (error: unknown) {
      const firebaseError = error as { code?: string };

      if (firebaseError.code === "auth/invalid-credential") {
        setAuthenticationError("Invalid email or password.");
      } else if (firebaseError.code === "auth/too-many-requests") {
        setAuthenticationError("Too many attempts. Try again later.");
      } else if (firebaseError.code === "auth/user-disabled") {
        setAuthenticationError("This account has been disabled.");
      } else if (firebaseError.code === "auth/invalid-email") {
        setAuthenticationError("Please enter a valid email address.");
      } else {
        setAuthenticationError("An error occurred. Please try again.");
      }

      clearErrorLater();
    } finally {
      setLoading(false);
    }
  };

  const value: AuthContextType = {
    email,
    setEmail,
    password,
    setPassword,
    handleLogin,
    handleSignUp,
    authenticationError,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within the AuthProvider!");
  }
  return context;
};

export { useAuth, AuthProvider };