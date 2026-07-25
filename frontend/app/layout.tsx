import type { Metadata, Viewport } from "next";
import "./globals.css";
import Hero3D from "@/components/Hero3D";

export const metadata: Metadata = {
  title: "Adaptive Offers — Decision Console",
  description:
    "Console de decisão de ofertas financeiras com multi-armed bandits. FIAP 7MLET — Grupo 74.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#000000",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-br">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <Hero3D />
        {children}
      </body>
    </html>
  );
}
