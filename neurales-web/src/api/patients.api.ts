import { http } from "./http";

export type PatientCreatePayload = {
  identifiant_interne: string;
  nom: string;
  prenom: string;
  date_naissance: string;
  numero_securite_sociale?: string;
  sexe?: string;
  service?: string;
  medecin_referent?: string;
  remarque?: string;
  notes?: string;
};

export type PatientListItem = {
  patient_id: number;
  organisation_id: number;
  identifiant_interne: string;
  nom: string;
  prenom: string;
  date_naissance?: string | null;
  numero_securite_sociale?: string | null;
};

export type PatientDetail = {
  patient_id: number;
  organisation_id: number;
  identifiant_interne: string;
  nom: string;
  prenom: string;
  date_naissance?: string | null;
  numero_securite_sociale?: string | null;
  sexe?: string | null;
  service?: string | null;
  medecin_referent?: string | null;
  remarque?: string | null;
  notes?: string | null;
  created_at: string;
};

export async function createPatient(payload: PatientCreatePayload) {
  const { data } = await http.post("/patients", payload);
  return data;
}

export async function listPatients(params?: { limit?: number; offset?: number }) {
  const { data } = await http.get<PatientListItem[]>("/patients", { params });
  return data;
}

export async function getPatientById(patientId: number) {
  const { data } = await http.get<PatientDetail>(`/patients/${patientId}`);
  return data;
}

export async function listServices() {
  const { data } = await http.get<string[]>("/patients/meta/services");
  return data;
}

export async function listMedecins() {
  const { data } = await http.get<string[]>("/patients/meta/medecins");
  return data;
}
