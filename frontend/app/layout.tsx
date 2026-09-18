import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "WasteWise AI - Restaurant Demand Forecasting & Food-Waste Reduction",
  description: "AI-powered dish demand forecasting and margin-aware kitchen preparation planning built for the Bharat Build First Commit Hackathon.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-slate-950 text-slate-100 antialiased min-h-screen flex flex-col`}>
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-400">
          WasteWise AI &copy; 2026 Bharat Build First Commit Hackathon | AWS Architecture Demo (S3, DynamoDB, Lambda, Bedrock)
        </footer>
      </body>
    </html>
  );
}
