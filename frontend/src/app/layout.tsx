import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Plum OPD ClaimGuard — AI-Powered Claim Adjudication",
  description: "Intelligent automation for OPD insurance claim processing. Upload documents, get instant AI-powered decisions.",
  keywords: "OPD, insurance, claims, AI, adjudication, Plum",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
      </head>
      <body className="antialiased min-h-screen">
        <Navbar />
        <main className="pt-20">{children}</main>
      </body>
    </html>
  );
}
