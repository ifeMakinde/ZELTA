import { AuthProvider } from "@/context/authContext";
import { JSX } from "react";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}): JSX.Element {
  return (
    <main>
      <AuthProvider>{children}</AuthProvider>
    </main>
  );
}