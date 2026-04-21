import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { http as api } from "@/api/http";
import { isDesktopRuntime } from "@/utils/desktop-runtime";

export interface Result {
  session_id: number;
  mode: string;
  started_at: string;
  ended_at?: string;
  notes?: string;
  app_version?: string;
  device_id?: number;
  patient_id?: number;
  organisation_id: number;
  created_by_user_id?: number;
  consent_id?: number;
}

export interface SessionCreatePayload {
  mode: string;
  started_at: string;
  ended_at?: string;
  notes?: string;
  app_version?: string;
  device_id?: number;
  patient_id?: number;
  created_by_user_id?: number;
  consent_id?: number;
}

export const useResultsStore = defineStore("results", () => {
  const STORAGE_KEY = "neurales_desktop_results";

  const items = ref<Result[]>([]);
  const current = ref<Result | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const isEmpty = computed(() => items.value.length === 0);

  function loadDesktopItems(): Result[] {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try {
        return JSON.parse(raw) as Result[];
      } catch {
        // ignore corrupted cache
      }
    }

    const demo: Result[] = [
      {
        session_id: 1,
        mode: "Démo",
        started_at: new Date(Date.now() - 86400000).toISOString(),
        ended_at: new Date(Date.now() - 86340000).toISOString(),
        notes: "Session locale de démonstration",
        app_version: "desktop-local",
        device_id: 1,
        patient_id: 1,
        organisation_id: 1,
        created_by_user_id: 1,
        consent_id: 1,
      },
    ];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(demo));
    return demo;
  }

  function saveDesktopItems(nextItems: Result[]) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nextItems));
  }

  const fetchSessions = async (limit: number = 50, offset: number = 0) => {
    isLoading.value = true;
    error.value = null;
    try {
      if (isDesktopRuntime()) {
        const allItems = loadDesktopItems();
        items.value = allItems.slice(offset, offset + limit);
        return;
      }
      const response = await api.get("/results", { params: { limit, offset } });
      items.value = response.data || [];
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Erreur lors du chargement";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchSessionById = async (sessionId: number): Promise<Result> => {
    isLoading.value = true;
    error.value = null;
    try {
      if (isDesktopRuntime()) {
        const found = loadDesktopItems().find((session) => session.session_id === sessionId);
        if (!found) throw new Error("Session introuvable");
        current.value = found;
        return found;
      }
      const response = await api.get(`/results/${sessionId}`);
      current.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Erreur lors du chargement";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const createSession = async (payload: Partial<Result>): Promise<Result> => {
    isLoading.value = true;
    error.value = null;
    try {
      if (isDesktopRuntime()) {
        const nextItems = loadDesktopItems();
        const session: Result = {
          session_id: nextItems.length > 0 ? Math.max(...nextItems.map((item) => item.session_id)) + 1 : 1,
          mode: payload.mode || "Démo",
          started_at: payload.started_at || new Date().toISOString(),
          ended_at: payload.ended_at,
          notes: payload.notes,
          app_version: payload.app_version || "desktop-local",
          device_id: payload.device_id,
          patient_id: payload.patient_id,
          organisation_id: 1,
          created_by_user_id: payload.created_by_user_id || 1,
          consent_id: payload.consent_id,
        };
        nextItems.unshift(session);
        saveDesktopItems(nextItems);
        items.value.unshift(session);
        return session;
      }
      const response = await api.post("/results", payload);
      items.value.unshift(response.data);
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Erreur lors de la création";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const updateSession = async (
    sessionId: number,
    payload: Partial<Result>
  ): Promise<Result> => {
    isLoading.value = true;
    error.value = null;
    try {
      if (isDesktopRuntime()) {
        const nextItems = loadDesktopItems();
        const index = nextItems.findIndex((session) => session.session_id === sessionId);
        if (index < 0) throw new Error("Session introuvable");
        nextItems[index] = { ...nextItems[index], ...payload, session_id: sessionId };
        saveDesktopItems(nextItems);
        const currentSession = nextItems[index];
        const localIndex = items.value.findIndex((session) => session.session_id === sessionId);
        if (localIndex >= 0) items.value[localIndex] = currentSession;
        current.value = currentSession;
        return currentSession;
      }
      const response = await api.put(`/results/${sessionId}`, payload);
      const index = items.value.findIndex((s) => s.session_id === sessionId);
      if (index >= 0) items.value[index] = response.data;
      current.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Erreur lors de la mise à jour";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteSession = async (sessionId: number): Promise<void> => {
    isLoading.value = true;
    error.value = null;
    try {
      if (isDesktopRuntime()) {
        const nextItems = loadDesktopItems().filter((session) => session.session_id !== sessionId);
        saveDesktopItems(nextItems);
        items.value = items.value.filter((session) => session.session_id !== sessionId);
        if (current.value?.session_id === sessionId) current.value = null;
        return;
      }
      await api.delete(`/results/${sessionId}`);
      items.value = items.value.filter((s) => s.session_id !== sessionId);
      if (current.value?.session_id === sessionId) current.value = null;
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Erreur lors de la suppression";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const getSessionQuality = async (sessionId: number): Promise<any> => {
    try {
      if (isDesktopRuntime()) {
        const session = loadDesktopItems().find((item) => item.session_id === sessionId);
        return session ? { quality: 82, fatigue: 23, session_id: sessionId } : null;
      }
      const response = await api.get(`/analytics/sessions/${sessionId}/quality`);
      return response.data;
    } catch (err: any) {
      console.error('Erreur qualité:', err);
      return null;
    }
  };

  const getSessionFatigueScore = async (sessionId: number): Promise<any> => {
    try {
      if (isDesktopRuntime()) {
        return { fatigue_score: 23, session_id: sessionId };
      }
      const response = await api.get(`/analytics/sessions/${sessionId}/fatigue-score`);
      return response.data;
    } catch (err: any) {
      console.error('Erreur fatigue:', err);
      return null;
    }
  };

  const getSessionEEGData = async (sessionId: number): Promise<any> => {
    try {
      if (isDesktopRuntime()) {
        return { session_id: sessionId, samples: [] };
      }
      const response = await api.get(`/analytics/sessions/${sessionId}/eeg`);
      return response.data;
    } catch (err: any) {
      console.error('Erreur EEG:', err);
      return null;
    }
  };

  const clearCurrent = () => {
    current.value = null;
  };

  return {
    items,
    current,
    isLoading,
    error,
    isEmpty,
    fetchSessions,
    fetchSessionById,
    createSession,
    updateSession,
    deleteSession,
    getSessionQuality,
    getSessionFatigueScore,
    getSessionEEGData,
    clearCurrent,
  };
});