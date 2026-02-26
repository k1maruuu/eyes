export type UserRole = "ADMIN" | "DISTRICT_DOCTOR" | "SURGEON" | "PATIENT";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}
export function setToken(t: string) {
  localStorage.setItem("access_token", t);
}
export function clearToken() {
  localStorage.removeItem("access_token");
}
