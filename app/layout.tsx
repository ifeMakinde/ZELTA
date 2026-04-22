// "use client";
import type { Metadata } from "next";
import { Open_Sans } from "next/font/google";
import "./globals.css";

// import { ThemeContextProvider, UseTheme } from "../context/themeContext";
// const inter = Inter({
//   variable: "--font-inter",
//   subsets: ["latin"],
// });

const openSans = Open_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-open-sans",
});

export const metadata: Metadata = {
  title: "Zelta",
  description: "behavioural quantitative intelligence",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${openSans.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
