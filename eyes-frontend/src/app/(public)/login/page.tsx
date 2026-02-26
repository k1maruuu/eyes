"use client";

import { useState } from "react";
import { login } from "@/features/auth/api";
import { setTokenCookie } from "@/shared/lib/auth";
import { useRouter } from "next/navigation";

export default function LoginPage() {
    const r = useRouter();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [err, setErr] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    async function onSubmit(e: React.FormEvent) {
        e.preventDefault();
        setErr(null);
        setLoading(true);
        try {
            const data = await login(email, password);
            setTokenCookie(data.access_token);
            r.push("/role");
        } catch (e: any) {
            setErr(e?.message ?? "Login error");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center p-6">
            <form onSubmit={onSubmit} className="w-full max-w-md rounded-2xl border p-6 space-y-4">
                <h1 className="text-xl font-semibold">Вход</h1>

                <input className="w-full border rounded-xl px-3 py-2"
                    placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />

                <input className="w-full border rounded-xl px-3 py-2"
                    placeholder="Пароль" type="password" value={password} onChange={e => setPassword(e.target.value)} />

                {err && <div className="text-sm text-red-600">{err}</div>}

                <button disabled={loading} className="w-full rounded-xl bg-black text-white py-2">
                    {loading ? "Входим..." : "Войти"}
                </button>
            </form>
        </div>
    );
}