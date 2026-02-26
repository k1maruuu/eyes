export type UserRole = "admin" | "feldsher" | "surgeon" | "patient";

export type JwtPayload = {
    sub: string;      // email (в бэке кладётся как sub)
    role: UserRole;   // бэк кладёт role в payload
    exp: number;
    iat: number;
};