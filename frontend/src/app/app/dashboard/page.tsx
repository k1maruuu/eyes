"use client";

import { useEffect, useState } from "react";
import { api } from "@/shared/api/client";

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api<any>("/dashboard/summary").then(setData).catch((e) => setErr(String(e.message ?? e)));
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Дашборд</h1>
      {err && <div className="text-red-600">{err}</div>}
      {!data ? (
        <div className="text-slate-500">Загрузка...</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          <Card title="Статусы заявок">
            <pre className="text-xs bg-slate-50 p-3 rounded-xl overflow-auto">{JSON.stringify(data.counts, null, 2)}</pre>
          </Card>
          <Card title="Ближайшие записи">
            <pre className="text-xs bg-slate-50 p-3 rounded-xl overflow-auto">{JSON.stringify(data.upcoming, null, 2)}</pre>
          </Card>
        </div>
      )}
    </div>
  );
}

function Card({ title, children }: { title: string; children: any }) {
  return (
    <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-4">
      <div className="font-medium">{title}</div>
      <div className="mt-3">{children}</div>
    </div>
  );
}
