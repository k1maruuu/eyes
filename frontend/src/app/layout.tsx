import "./globals.css";
import type { ReactNode } from "react";

export const metadata = { title: "Eyes v2", description: "Clinic workflow" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ru">
      <body className="min-h-screen bg-slate-50 text-slate-900">{children}</body>
    </html>
  );
}
