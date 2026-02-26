import { api } from "@/shared/api/client";
import type { Patient, PatientStatus } from "./model";

export function listPatients(params: { status?: PatientStatus; limit?: number; offset?: number }) {
    const q = new URLSearchParams();
    if (params.status) q.set("status", params.status);
    if (params.limit) q.set("limit", String(params.limit));
    if (params.offset) q.set("offset", String(params.offset));
    return api<Patient[]>(`/patients/?${q.toString()}`);
}

export function getPatient(id: number) {
    return api<Patient>(`/patients/${id}`);
}