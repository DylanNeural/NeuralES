import { http } from "./http";

export type LoginRequest = { email: string; password: string };
export type LoginResponse = { access_token: string; token_type: "bearer" };

export async function login(payload: LoginRequest) {
  const { data } = await http.post<LoginResponse>("/auth/login", payload);
  return data;
}

export async function me() {
  const { data } = await http.get("/auth/me");
  return data;
}
