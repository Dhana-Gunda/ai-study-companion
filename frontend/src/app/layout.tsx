import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "The Lenny Growth Assistant",
  description: "Enterprise RAG copilot grounded in Lenny's Podcast transcripts with Claude-style Artifacts & Ship 30 for 30 skill.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-zinc-950 text-zinc-100 antialiased h-screen w-screen overflow-hidden">
        {children}
      </body>
    </html>
  );
}
