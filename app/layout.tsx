// "use client";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ZeltaProvider } from "@/context/zeltaContext";
import PageTransitionLoader from "@/components/PageTransitionLoader";
// import { ThemeContextProvider, UseTheme } from "../context/themeContext";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

// const openSans = Open_Sans({
//   subsets: ["latin"],
//   display: "swap",
//   variable: "--font-open-sans",
// });

export const metadata: Metadata = {
  title: "Zelta AI",
  description: "behavioural quantitative intelligence",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">
        <PageTransitionLoader />
        <ZeltaProvider>{children}</ZeltaProvider>
      </body>
    </html>
  );
}
