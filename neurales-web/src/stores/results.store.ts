import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { http as api } from "@/api/http";
import { isDesktopRuntime } from "@/utils/desktop-runtime";
import * as ResultsAPI from "@/api/results.api";

export interface Result {
  session_id: string;
  mode: string;
  started_at: string;
  ended_at?: string;
  notes?: string;
  app_version?: string;
  device_id?: string;
  patient_id?: string;
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
  device_id?: string;
  patient_id?: string;
  created_by_user_id?: number;
  consent_id?: number;
}

export const useResultsStore = defineStore("results", () => {
  const items = ref<Result[]>([]);
  const current = ref<Result | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const isEmpty = computed(() => items.value.length === 0);

  const toErrorMessage = (err: unknown, fallback: string): string => {
    const e = err as any;
    return e?.response?.data?.detail || e?.message || (typeof e === "string" ? e : fallback);
  };
  

  const fetchSessions = async (limit: number = 50, offset: number = 0) => {
    isLoading.value = true;
    error.value = null;
    try {
      if (isDesktopRuntime()) {
        const allItems = (await ResultsAPI.listSessions()) as any;
        items.value = (allItems || []).slice(offset, offset + limit) as Result[];
        return;
      }
      const response = await api.get("/results", { params: { limit, offset } });
      items.value = response.data || [];
    } catch (err: any) {
      error.value = toErrorMessage(err, "Erreur lors du chargement");
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchSessionById = async (sessionId: string): Promise<Result> => {
    isLoading.value = true;
    error.value = null;
    try {
      if (isDesktopRuntime()) {
        const found = (await ResultsAPI.getSessionById(sessionId as any)) as any;
        if (!found) throw new Error("Session introuvable");
        current.value = found as any;
        return found as any;
      }
      const response = await api.get(`/results/${sessionId}`);
      current.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = toErrorMessage(err, "Erreur lors du chargement");
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
        const created = await ResultsAPI.createSession(payload as any);
        items.value.unshift(created as any);
        return created as any;
      }
      const response = await api.post("/results", payload);
      items.value.unshift(response.data);
      return response.data;
    } catch (err: any) {
      error.value = toErrorMessage(err, "Erreur lors de la création");
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const updateSession = async (
    sessionId: string,
    payload: Partial<Result>
  ): Promise<Result> => {
    isLoading.value = true;
    error.value = null;
    try {
      if (isDesktopRuntime()) {
        const updated = (await ResultsAPI.updateSession(sessionId as any, payload as any)) as any;
        const idx = items.value.findIndex((s) => s.session_id === sessionId);
        if (idx >= 0) items.value[idx] = updated as any;
        current.value = updated as any;
        return updated as any;
      }
      const response = await api.put(`/results/${sessionId}`, payload);
      const index = items.value.findIndex((s) => s.session_id === sessionId);
      if (index >= 0) items.value[index] = response.data;
      current.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = toErrorMessage(err, "Erreur lors de la mise à jour");
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteSession = async (sessionId: string): Promise<void> => {
    isLoading.value = true;
    error.value = null;
    try {
      if (isDesktopRuntime()) {
        await ResultsAPI.deleteSession(sessionId as any);
        items.value = items.value.filter((s) => s.session_id !== sessionId);
        if (current.value?.session_id === sessionId) current.value = null;
        return;
      }
      await api.delete(`/results/${sessionId}`);
      items.value = items.value.filter((s) => s.session_id !== sessionId);
      if (current.value?.session_id === sessionId) current.value = null;
    } catch (err: any) {
      error.value = toErrorMessage(err, "Erreur lors de la suppression");
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const getSessionQuality = async (sessionId: string): Promise<any> => {
    try {
      if (isDesktopRuntime()) {
        const session = await ResultsAPI.getSessionById(sessionId as any);
        return session ? { quality: 82, fatigue: 23, session_id: sessionId } : null;
      }
      const response = await api.get(`/analytics/sessions/${sessionId}/quality`);
      return response.data;
    } catch (err: any) {
      console.error('Erreur qualité:', err);
      return null;
    }
  };

  const getSessionFatigueScore = async (sessionId: string): Promise<any> => {
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

  const getSessionEEGData = async (sessionId: string): Promise<any> => {
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