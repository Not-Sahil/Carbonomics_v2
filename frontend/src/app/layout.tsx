import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CARBONOMICS v3 — Intelligent Carbon Intelligence & Green Infrastructure",
  description: "Enterprise AI-powered carbon intelligence, digital infrastructure monitoring, predictive analytics, and sustainability optimization platform.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-carbon-bg text-carbon-text antialiased selection:bg-carbon-primary/30 selection:text-carbon-primary">
        {children}
      </body>
    </html>
  );
}

