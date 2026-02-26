"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/shared/api/client";
import { clearToken } from "@/shared/lib/auth";

type Me = { id: number; email: string; full_name: string; role: string; organization_id?: number | null };

export default function AppLayout({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<Me | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api<Me>("/auth/me")
      .then(setMe)
      .catch((e) => {
        setErr(String(e?.message ?? e));
        clearToken();
        window.location.href = "/login";
      });
  }, []);

  return (
    <div className="min-h-screen grid grid-cols-[260px_1fr]">
      <aside className="border-r border-slate-200 bg-white p-4">
        <div className="font-semibold">Eyes v2</div>
        <div className="text-xs text-slate-500 mt-1">{me ? `${me.full_name} • ${me.role}` : "..."}</div>

        <nav className="mt-6 space-y-1 text-sm">
          <NavLink href="/app/dashboard" label="Дашборд" />
          <NavLink href="/app/patients" label="Пациенты" />
          <NavLink href="/app/cases" label="Заявки (кейсы)" />
          <NavLink href="/app/calc-queue" label="Очередь на расчёт" />
        </nav>

        <button
          onClick={() => {
            clearToken();
            window.location.href = "/login";
          }}
          className="mt-6 text-sm text-slate-600 underline"
        >
          Выйти
        </button>

        {err && <div className="mt-4 text-xs text-red-600 whitespace-pre-wrap">{err}</div>}
      </aside>

      <main className="p-6">{children}</main>
    </div>
  );
}

function NavLink({ href, label }: { href: string; label: string }) {
  return (
    <Link className="block rounded-xl px-3 py-2 hover:bg-slate-50 border border-transparent hover:border-slate-200" href={href}>
      {label}
    </Link>
  );
}
