import { http } from "./http";

export type LoginRequest = { email: string; password: string };
export type LoginResponse = { access_token: string; token_type: "bearer" };
export type AuthUser = {
  user_id: number;
  prenom: string;
  nom: string;
  email: string;
  organisation_id: number;
  role?: string;
};

const DESKTOP_TOKEN_KEY = "desktop_access_token";

function isDesktopTauri() {
  return typeof window !== "undefined" && "__TAURI_INTERNALS__" in window;
}

async function invokeDesktop<T>(command: string, args?: Record<string, unknown>) {
  const { invoke } = await import("@tauri-apps/api/core");
  return invoke<T>(command, args);
}

export async function login(payload: LoginRequest) {
  if (isDesktopTauri()) {
    return invokeDesktop<LoginResponse>("desktop_login", { payload });
  }
  const { data } = await http.post<LoginResponse>("/auth/login", payload);
  return data;
}

export async function refresh() {
  if (isDesktopTauri()) {
    const token = localStorage.getItem(DESKTOP_TOKEN_KEY);
    return invokeDesktop<LoginResponse>("desktop_refresh", { token });
  }
  const { data } = await http.post<LoginResponse>("/auth/refresh");
  return data;
}

export async function logout() {
  if (isDesktopTauri()) {
    await invokeDesktop<void>("desktop_logout");
    return;
  }
  await http.post("/auth/logout");
}

export async function me() {
  if (isDesktopTauri()) {
    return invokeDesktop<AuthUser>("desktop_me");
  }
  const { data } = await http.get("/auth/me");
  return data;
}
