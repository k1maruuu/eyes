"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/shared/api/client";

export default function CalcQueuePage() {
  const [items, setItems] = useState<any[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api<any>("/cases/calc-queue/list").then((d) => setItems(d.items)).catch((e) => setErr(String(e.message ?? e)));
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Очередь на расчёт</h1>
      {err && <div className="text-red-600 whitespace-pre-wrap">{err}</div>}
      <div className="rounded-2xl bg-white border border-slate-200 overflow-hidden">
        <div className="grid grid-cols-[80px_120px_160px_120px] gap-2 px-4 py-2 text-xs text-slate-500 border-b border-slate-200">
          <div>ID</div><div>Patient</div><div>Status</div><div>Open</div>
        </div>
        {items.map((c) => (
          <div key={c.id} className="grid grid-cols-[80px_120px_160px_120px] gap-2 px-4 py-3 border-b last:border-b-0 border-slate-100 text-sm">
            <div className="text-slate-500">{c.id}</div>
            <div className="text-slate-600">{c.patient_id}</div>
            <div className="font-medium">{c.status}</div>
            <Link className="underline" href={`/app/cases/${c.id}`}>Открыть</Link>
          </div>
        ))}
      </div>
    </div>
  );
}
