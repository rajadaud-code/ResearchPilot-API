import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ResearchPilot API — Autonomous Document Research Engine",
  description:
    "Production-grade AI backend & dashboard for autonomous document research, LangGraph multi-agent execution, vector similarity search, and real-time SSE token streaming.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased selection:bg-emerald-500/30 selection:text-emerald-300">
        {children}
      </body>
    </html>
  );
}
