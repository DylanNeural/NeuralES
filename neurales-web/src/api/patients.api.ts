import { http } from "./http";

export type PatientCreatePayload = {
  nom: string;
  prenom: string;
  date_naissance: string;
  numero_securite_sociale: string;
  sexe: string;
  service?: string;
  medecin_referent?: string;
  remarque?: string;
};

export async function createPatient(payload: PatientCreatePayload) {
  const { data } = await http.post("/patients", payload);
  return data;
}
