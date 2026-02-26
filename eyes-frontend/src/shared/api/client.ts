const API_URL = process.env.NEXT_PUBLIC_API_URL!;

type HttpMethod = "GET" | "POST" | "PATCH" | "PUT" | "DELETE";

function getTokenClient(): string | null {
    if (typeof document === "undefined") return null;
    const m = document.cookie.match(/(?:^|;\s*)access_token=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : null;
}

export async function api<T>(
    path: string,
    opts: { method?: HttpMethod; body?: any; headers?: Record<string, string> } = {}
): Promise<T> {
    const token = getTokenClient();
    const headers: Record<string, string> = {
        ...(opts.headers ?? {}),
    };

    if (!(opts.body instanceof FormData)) {
        headers["Content-Type"] = headers["Content-Type"] ?? "application/json";
    }
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_URL}${path}`, {
        method: opts.method ?? "GET",
        headers,
        body: opts.body instanceof FormData ? opts.body : opts.body ? JSON.stringify(opts.body) : undefined,
    });

    if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(`API ${res.status}: ${text}`);
    }
    return (await res.json()) as T;
}