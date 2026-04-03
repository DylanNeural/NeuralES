import { http } from "./http";

export type SessionListItem = {
	session_id: number;
	mode: string;
	started_at: string;
	ended_at?: string | null;
	patient_id?: number | null;
	device_id?: number | null;
};

export type SessionDetail = {
	session_id: number;
	mode: string;
	started_at: string;
	ended_at?: string | null;
	notes?: string | null;
	app_version?: string | null;
	device_id?: number | null;
	consent_id?: number | null;
	patient_id?: number | null;
	created_by_user_id: number;
	organisation_id: number;
};

export async function listSessions(params?: { limit?: number; offset?: number }) {
	const { data } = await http.get<SessionListItem[]>("/results", { params });
	return data;
}

export async function getSessionById(sessionId: number) {
	const { data } = await http.get<SessionDetail>(`/results/${sessionId}`);
	return data;
}