import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { http as api } from "@/api/http";

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
  const items = ref<Result[]>([]);
  const current = ref<Result | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const isEmpty = computed(() => items.value.length === 0);

  const fetchSessions = async (limit: number = 50, offset: number = 0) => {
    isLoading.value = true;
    error.value = null;
    try {
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
      const response = await api.get(`/analytics/sessions/${sessionId}/quality`);
      return response.data;
    } catch (err: any) {
      console.error('Erreur qualité:', err);
      return null;
    }
  };

  const getSessionFatigueScore = async (sessionId: number): Promise<any> => {
    try {
      const response = await api.get(`/analytics/sessions/${sessionId}/fatigue-score`);
      return response.data;
    } catch (err: any) {
      console.error('Erreur fatigue:', err);
      return null;
    }
  };

  const getSessionEEGData = async (sessionId: number): Promise<any> => {
    try {
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