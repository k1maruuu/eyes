"use client";

import { useEffect, useState } from "react";
import { api } from "@/shared/api/client";
import { useParams } from "next/navigation";

export default function PatientDetail() {
  const params = useParams<{ id: string }>();
  const id = Number(params.id);
  const [p, setP] = useState<any>(null);
  const [cases, setCases] = useState<any[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api(`/patients/${id}`),
      api(`/cases`).then((d: any) => d.items as any[]),
    ])
      .then(([patient, items]) => {
        setP(patient);
        setCases(items.filter((c) => c.patient_id === id));
      })
      .catch((e) => setErr(String(e.message ?? e)));
  }, [id]);

  if (err) return <div className="text-red-600">{err}</div>;
  if (!p) return <div className="text-slate-500">Загрузка...</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">{p.full_name}</h1>
      <div className="rounded-2xl bg-white border border-slate-200 p-4">
        <div className="text-sm text-slate-600">ID: {p.id}</div>
        <div className="text-sm text-slate-600">Дата рождения: {p.birth_date ?? "-"}</div>
        <div className="text-sm text-slate-600">Пол: {p.sex ?? "-"}</div>
      </div>

      <div className="rounded-2xl bg-white border border-slate-200 p-4">
        <div className="font-medium">Кейсы (заявки)</div>
        <pre className="mt-2 text-xs bg-slate-50 p-3 rounded-xl overflow-auto">{JSON.stringify(cases, null, 2)}</pre>
      </div>
    </div>
  );
}
