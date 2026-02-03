import { http } from "./http";

export type StartAcqResponse = { session_id: string };
export type LiveMetrics = { fatigue_score: number; quality: number; timestamp: string };

export async function startAcquisition() {
  const { data } = await http.post<StartAcqResponse>("/acquisition/start");
  return data;
}

export async function stopAcquisition(session_id: string) {
  const { data } = await http.post("/acquisition/stop", { session_id });
  return data;
}

// soit websocket, soit polling:
export async function getLive(session_id: string) {
  const { data } = await http.get<LiveMetrics>(`/acquisition/${session_id}/live`);
  return data;
}
