import type { UserRole } from "@/entities/user/model";

export const ROLE_DEFAULT_ROUTE: Record<UserRole, string> = {
    admin: "/app/dashboard",
    feldsher: "/app/dashboard",
    surgeon: "/app/dashboard",
    patient: "/patient",
};

export const ROUTE_RULES: Array<{ prefix: string; allow: UserRole[] }> = [
    { prefix: "/app/calc-queue", allow: ["surgeon", "admin"] },
    { prefix: "/app", allow: ["feldsher", "surgeon", "admin"] },
    { prefix: "/patient", allow: ["patient"] },
];