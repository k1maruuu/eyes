import jwtDecode from "jwt-decode";
import type { JwtPayload } from "@/entities/user/model";

export function getTokenFromCookie(): string | null {
    if (typeof document === "undefined") return null;
    const m = document.cookie.match(/(?:^|;\s*)access_token=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : null;
}

export function setTokenCookie(token: string) {
    document.cookie = `access_token=${encodeURIComponent(token)}; path=/; max-age=${60 * 60 * 24 * 7}`;
}

export function clearTokenCookie() {
    document.cookie = `access_token=; path=/; max-age=0`;
}

export function getRoleFromToken(token: string): JwtPayload["role"] | null {
    try {
        const payload = jwtDecode<JwtPayload>(token);
        return payload.role ?? null;
    } catch {
        return null;
    }
}