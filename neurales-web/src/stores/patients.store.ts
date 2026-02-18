import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { http as api } from "@/api/http";

export interface Patient {
  patient_id: number;
  identifiant_interne: string;
  nom: string;
  prenom: string;
  date_naissance?: string;
  numero_securite_sociale?: string;
  sexe?: string;
  service?: string;
  medecin_referent?: string;
  remarque?: string;
  notes?: string;
  organisation_id: number;
}

export interface PatientCreatePayload {
  identifiant_interne: string;
  nom: string;
  prenom: string;
  date_naissance?: string;
  numero_securite_sociale?: string;
  sexe?: string;
  service?: string;
  medecin_referent?: string;
  remarque?: string;
  notes?: string;
}

export const usePatientsStore = defineStore("patients", () => {
  const items = ref<Patient[]>([]);
  const current = ref<Patient | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const services = ref<string[]>([]);
  const medecins = ref<string[]>([]);

  const isEmpty = computed(() => items.value.length === 0);

  const fetchPatients = async (limit: number = 50, offset: number = 0) => {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await api.get("/patients", { params: { limit, offset } });
      items.value = response.data || [];
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Erreur lors du chargement";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchPatientById = async (patientId: number): Promise<Patient> => {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await api.get(`/patients/${patientId}`);
      current.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Erreur lors du chargement";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const createPatient = async (payload: PatientCreatePayload): Promise<Patient> => {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await api.post("/patients", payload);
      items.value.unshift(response.data);
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Erreur lors de la création";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const updatePatient = async (
    patientId: number,
    payload: Partial<PatientCreatePayload>
  ): Promise<Patient> => {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await api.put(`/patients/${patientId}`, payload);
      const index = items.value.findIndex((p) => p.patient_id === patientId);
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

  const deletePatient = async (patientId: number): Promise<void> => {
    isLoading.value = true;
    error.value = null;
    try {
      await api.delete(`/patients/${patientId}`);
      items.value = items.value.filter((p) => p.patient_id !== patientId);
      if (current.value?.patient_id === patientId) current.value = null;
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Erreur lors de la suppression";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchServices = async () => {
    try {
      const response = await api.get("/patients/meta/services");
      services.value = response.data;
    } catch (err: any) {
      console.error("Erreur services:", err);
    }
  };

  const fetchMedecins = async () => {
    try {
      const response = await api.get("/patients/meta/medecins");
      medecins.value = response.data;
    } catch (err: any) {
      console.error("Erreur medecins:", err);
    }
  };

  return {
    items,
    current,
    isLoading,
    error,
    services,
    medecins,
    isEmpty,
    fetchPatients,
    fetchPatientById,
    createPatient,
    updatePatient,
    deletePatient,
    fetchServices,
    fetchMedecins,
  };
});
