"use client";

import { useQuery } from "@tanstack/react-query";
import { listPatients } from "@/entities/patient/api";

export default function PatientsPage() {
    const { data, isLoading, error } = useQuery({
        queryKey: ["patients", { status: null }],
        queryFn: () => listPatients({ limit: 50, offset: 0 }),
    });

    if (isLoading) return <div className="p-6">Загрузка...</div>;
    if (error) return <div className="p-6">Ошибка: {(error as Error).message}</div>;

    return (
        <div className="p-6 space-y-4">
            <h1 className="text-xl font-semibold">Пациенты</h1>

            <div className="grid gap-3">
                {data?.map(p => (
                    <a key={p.id} href={`/app/patients/${p.id}`} className="rounded-2xl border p-4 hover:bg-gray-50">
                        <div className="font-medium">{p.fio}</div>
                        <div className="text-sm text-gray-600">Статус: {p.status}</div>
                    </a>
                ))}
            </div>
        </div>
    );
}