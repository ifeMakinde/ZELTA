import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import PageTransitionLoader from "@/components/PageTransitionLoader";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Zelta AI",
  description: "Behavioural Quantitative Intelligence",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">
        <PageTransitionLoader />
        {children}
      </body>
    </html>
  );
}