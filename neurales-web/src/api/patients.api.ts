import { http } from "./http";
import { desktopInvoke, isDesktopRuntime } from "@/utils/desktop-runtime";

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
  if (isDesktopRuntime()) {
    return desktopInvoke<PatientDetail>("create_patient", { payload });
  }
  const { data } = await http.post("/patients", payload);
  return data;
}

export async function listPatients(params?: { limit?: number; offset?: number }) {
  if (isDesktopRuntime()) {
    return desktopInvoke<PatientListItem[]>("list_patients", { params });
  }
  const { data } = await http.get<PatientListItem[]>("/patients", { params });
  return data;
}

export async function getPatientById(patientId: number) {
  if (isDesktopRuntime()) {
    return desktopInvoke<PatientDetail | null>("get_patient_by_id", { patientId });
  }
  const { data } = await http.get<PatientDetail>(`/patients/${patientId}`);
  return data;
}

export async function updatePatient(patientId: number, payload: Partial<PatientCreatePayload>) {
  if (isDesktopRuntime()) {
    return desktopInvoke<PatientDetail | null>("update_patient", { patientId, payload });
  }
  const { data } = await http.put<PatientDetail>(`/patients/${patientId}`, payload);
  return data;
}

export async function deletePatient(patientId: number) {
  if (isDesktopRuntime()) {
    return desktopInvoke<boolean>("delete_patient", { patientId });
  }
  const { data } = await http.delete(`/patients/${patientId}`);
  return data;
}

export async function listServices() {
  if (isDesktopRuntime()) {
    return desktopInvoke<string[]>("list_services");
  }
  const { data } = await http.get<string[]>("/patients/meta/services");
  return data;
}

export async function listMedecins() {
  if (isDesktopRuntime()) {
    return desktopInvoke<string[]>("list_medecins");
  }
  const { data } = await http.get<string[]>("/patients/meta/medecins");
  return data;
}
