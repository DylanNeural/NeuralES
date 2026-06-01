import { http } from "./http";
import { desktopInvoke, isDesktopRuntime } from "@/utils/desktop-runtime";

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
	if (isDesktopRuntime()) {
		return desktopInvoke<SessionListItem[]>("list_sessions");
	}

	const { data } = await http.get<SessionListItem[]>("/results", { params });
	return data;
}

export async function getSessionById(sessionId: number) {
	if (isDesktopRuntime()) {
		return desktopInvoke<SessionDetail | null>("get_session_by_id", { sessionId });
	}

	const { data } = await http.get<SessionDetail>(`/results/${sessionId}`);
	return data;
}

export async function createSession(payload: Partial<SessionDetail>) {
	if (isDesktopRuntime()) {
		return desktopInvoke<SessionDetail>("create_session", { payload });
	}

	const { data } = await http.post<SessionDetail>("/results", payload);
	return data;
}

export async function updateSession(sessionId: number, payload: Partial<SessionDetail>) {
	if (isDesktopRuntime()) {
		return desktopInvoke<SessionDetail | null>("update_session", { sessionId, payload });
	}

	const { data } = await http.put<SessionDetail>(`/results/${sessionId}`, payload);
	return data;
}

export async function deleteSession(sessionId: number) {
	if (isDesktopRuntime()) {
		return desktopInvoke<boolean>("delete_session", { sessionId });
	}

	const { data } = await http.delete(`/results/${sessionId}`);
	return data;
}