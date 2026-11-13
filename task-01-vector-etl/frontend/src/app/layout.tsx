import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Datheon | Enterprise Vector ETL",
  description:
    "Enterprise document ingestion, vector search and analytics dashboard.",
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
