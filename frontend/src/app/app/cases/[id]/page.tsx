"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/shared/api/client";
import { Button } from "@/shared/ui/Button";
import { Input } from "@/shared/ui/Input";

export default function CaseDetail() {
  const params = useParams<{ id: string }>();
  const id = Number(params.id);
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);

  const [axial, setAxial] = useState("");
  const [k1, setK1] = useState("");
  const [k2, setK2] = useState("");
  const [note, setNote] = useState("");

  async function load() {
    setErr(null);
    try {
      const d = await api<any>(`/cases/${id}`);
      setData(d);
      const meas = (d.items || []).find((x: any) => x.kind === "MEASUREMENT")?.value_json;
      if (meas) {
        setAxial(String(meas.axial_length_mm ?? ""));
        setK1(String(meas.k1_d ?? ""));
        setK2(String(meas.k2_d ?? ""));
        setNote(String(meas.note ?? ""));
      }
    } catch (e: any) {
      setErr(String(e.message ?? e));
    }
  }

  useEffect(() => { load(); }, [id]);

  async function saveMeasurements() {
    setErr(null);
    try {
      await api(`/cases/${id}/measurements`, {
        method: "PUT",
        body: JSON.stringify({
          axial_length_mm: axial ? Number(axial) : null,
          k1_d: k1 ? Number(k1) : null,
          k2_d: k2 ? Number(k2) : null,
          note: note || null,
        }),
      });
      await load();
    } catch (e: any) {
      setErr(String(e.message ?? e));
    }
  }

  async function calc() {
    setErr(null);
    try {
      await api(`/cases/${id}/calculate`, { method: "POST" });
      await load();
    } catch (e: any) {
      setErr(String(e.message ?? e));
    }
  }

  if (err) return <div className="text-red-600 whitespace-pre-wrap">{err}</div>;
  if (!data) return <div className="text-slate-500">Загрузка...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Кейс #{data.id}</h1>

      <div className="grid gap-4 md:grid-cols-2">
        <Card title="Основное">
          <div className="text-sm text-slate-700">Пациент: {data.patient_id}</div>
          <div className="text-sm text-slate-700">Статус: <span className="font-medium">{data.status}</span></div>
          <div className="text-sm text-slate-700">Прогресс: {data.progress_percent}%</div>
        </Card>

        <Card title="Результат расчёта">
          <pre className="text-xs bg-slate-50 p-3 rounded-xl overflow-auto">{JSON.stringify(data.calc_result, null, 2)}</pre>
          <Button className="mt-3" onClick={calc}>Рассчитать</Button>
        </Card>
      </div>

      <Card title="Замеры / биометрия">
        <div className="grid gap-3 md:grid-cols-2">
          <div>
            <div className="text-xs text-slate-500 mb-1">Axial length (mm)</div>
            <Input value={axial} onChange={(e) => setAxial(e.target.value)} />
          </div>
          <div>
            <div className="text-xs text-slate-500 mb-1">K1 (D)</div>
            <Input value={k1} onChange={(e) => setK1(e.target.value)} />
          </div>
          <div>
            <div className="text-xs text-slate-500 mb-1">K2 (D)</div>
            <Input value={k2} onChange={(e) => setK2(e.target.value)} />
          </div>
          <div>
            <div className="text-xs text-slate-500 mb-1">Комментарий</div>
            <Input value={note} onChange={(e) => setNote(e.target.value)} />
          </div>
        </div>
        <Button className="mt-3" onClick={saveMeasurements}>Сохранить замеры</Button>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card title="Чеклист / пункты">
          <pre className="text-xs bg-slate-50 p-3 rounded-xl overflow-auto">{JSON.stringify(data.items, null, 2)}</pre>
        </Card>
        <Card title="История / operation_log">
          <pre className="text-xs bg-slate-50 p-3 rounded-xl overflow-auto">{JSON.stringify(data.history, null, 2)}</pre>
        </Card>
      </div>

      <Card title="Комментарии">
        <pre className="text-xs bg-slate-50 p-3 rounded-xl overflow-auto">{JSON.stringify(data.comments, null, 2)}</pre>
      </Card>
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
