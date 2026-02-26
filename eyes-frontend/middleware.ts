import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { ROLE_DEFAULT_ROUTE, ROUTE_RULES } from "@/shared/config/roles";
import jwtDecode from "jwt-decode";
import type { JwtPayload } from "@/entities/user/model";

function getToken(req: NextRequest) {
    return req.cookies.get("access_token")?.value ?? null;
}

export function middleware(req: NextRequest) {
    const { pathname } = req.nextUrl;

    // публичные страницы
    if (pathname.startsWith("/login") || pathname.startsWith("/role") || pathname.startsWith("/_next")) {
        return NextResponse.next();
    }

    const token = getToken(req);
    if (!token) {
        return NextResponse.redirect(new URL("/login", req.url));
    }

    let role: JwtPayload["role"] | null = null;
    try {
        role = jwtDecode<JwtPayload>(token).role;
    } catch {
        return NextResponse.redirect(new URL("/login", req.url));
    }

    // правила доступа
    const rule = ROUTE_RULES.find(r => pathname.startsWith(r.prefix));
    if (rule && !rule.allow.includes(role)) {
        const to = ROLE_DEFAULT_ROUTE[role];
        return NextResponse.redirect(new URL(to, req.url));
    }

    return NextResponse.next();
}

export const config = {
    matcher: ["/app/:path*", "/patient/:path*"],
};