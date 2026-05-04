import { AuthProvider } from "@/context/authContext";
import { JSX } from "react";

// const BASE_URL = "https://zelta-878473667930.us-central1.run.app/";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}): JSX.Element {
  return (
    <main>
      <AuthProvider>{children}</AuthProvider>;<div></div>
    </main>
  );
}
