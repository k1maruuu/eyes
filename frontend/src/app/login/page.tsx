"use client";

import { useState } from "react";
import { Button } from "@/shared/ui/Button";
import { Input } from "@/shared/ui/Input";
import { setToken } from "@/shared/lib/auth";

const API = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function LoginPage() {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit() {
    setErr(null);
    setLoading(true);
    try {
      const body = new URLSearchParams();
      body.set("username", email);
      body.set("password", password);

      const res = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setToken(data.access_token);
      window.location.href = "/app/dashboard";
    } catch (e: any) {
      setErr(e?.message ?? "Ошибка");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-sm border border-slate-200">
        <h1 className="text-xl font-semibold">Вход</h1>
        <p className="text-sm text-slate-500 mt-1">Демо-аккаунты: admin/doctor/surgeon/patient</p>

        <div className="mt-4 space-y-3">
          <div>
            <div className="text-xs text-slate-500 mb-1">Email</div>
            <Input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="email" />
          </div>
          <div>
            <div className="text-xs text-slate-500 mb-1">Пароль</div>
            <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="password" />
          </div>

          {err && <div className="text-sm text-red-600 whitespace-pre-wrap">{err}</div>}

          <Button className="w-full" disabled={loading} onClick={onSubmit}>
            {loading ? "Входим..." : "Войти"}
          </Button>

          <div className="text-xs text-slate-500">
            Подсказка: admin@example.com / admin123, doctor@example.com / doctor123, surgeon@example.com / surgeon123, patient@example.com / patient123
          </div>
        </div>
      </div>
    </div>
  );
}
