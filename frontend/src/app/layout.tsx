import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Nigeria Election Analytics",
  description: "Next.js and FastAPI dashboard for Nigerian election analysis.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
