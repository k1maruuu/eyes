"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/shared/api/client";
import { Input } from "@/shared/ui/Input";

type Patient = { id: number; full_name: string; birth_date?: string | null; sex?: string | null };

export default function PatientsPage() {
  const [items, setItems] = useState<Patient[]>([]);
  const [search, setSearch] = useState("");
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    setErr(null);
    try {
      const q = search ? `?search=${encodeURIComponent(search)}` : "";
      const data = await api<{ items: Patient[] }>(`/patients${q}`);
      setItems(data.items);
    } catch (e: any) {
      setErr(String(e.message ?? e));
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Пациенты</h1>

      <div className="flex gap-2 max-w-xl">
        <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Поиск по ФИО" />
        <button onClick={load} className="rounded-xl px-4 py-2 border border-slate-200 bg-white">Найти</button>
      </div>

      {err && <div className="text-red-600">{err}</div>}

      <div className="rounded-2xl bg-white border border-slate-200 overflow-hidden">
        <div className="grid grid-cols-[80px_1fr_140px_80px] gap-2 px-4 py-2 text-xs text-slate-500 border-b border-slate-200">
          <div>ID</div><div>ФИО</div><div>Дата рождения</div><div>Пол</div>
        </div>
        {items.map(p => (
          <Link key={p.id} href={`/app/patients/${p.id}`} className="grid grid-cols-[80px_1fr_140px_80px] gap-2 px-4 py-3 hover:bg-slate-50 border-b last:border-b-0 border-slate-100 text-sm">
            <div className="text-slate-500">{p.id}</div>
            <div className="font-medium">{p.full_name}</div>
            <div className="text-slate-600">{p.birth_date ?? "-"}</div>
            <div className="text-slate-600">{p.sex ?? "-"}</div>
          </Link>
        ))}
      </div>
    </div>
  );
}
