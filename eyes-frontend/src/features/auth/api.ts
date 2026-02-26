const API_URL = process.env.NEXT_PUBLIC_API_URL!;

export async function login(email: string, password: string): Promise<{ access_token: string; token_type: string }> {
    const body = new URLSearchParams();
    body.set("email", email);
    body.set("password", password);

    const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
    });

    if (!res.ok) throw new Error(await res.text());
    return res.json();
}