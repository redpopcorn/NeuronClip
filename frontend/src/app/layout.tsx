import type { Metadata } from "next";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClipNeuron — AI Clip Studio",
  description: "Generate viral podcast clips with AI-grade precision.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased dark">
      <body className="min-h-full bg-[#08090D] text-white flex flex-col">
        {children}
        <Toaster richColors theme="dark" />
      </body>
    </html>
  );
}
