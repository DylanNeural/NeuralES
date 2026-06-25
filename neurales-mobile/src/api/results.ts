import client from "./client";

export interface SessionResult {
  session_id: number;
  mode: string;
  started_at: string | null;
  ended_at: string | null;
  notes: string | null;
}

export async function getMyResults(): Promise<SessionResult[]> {
  const res = await client.get<SessionResult[]>("/auth/patient/results");
  return res.data;
}

export async function getMyResult(id: number): Promise<SessionResult> {
  const res = await client.get<SessionResult>(`/auth/patient/results/${id}`);
  return res.data;
}
