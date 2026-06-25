import client from "./client";

export interface PatientLoginPayload {
  nom: string;
  prenom: string;
  date_naissance: string;
  password: string;
}

export interface PatientMe {
  patient_id: number;
  nom: string;
  prenom: string;
  date_naissance: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export async function patientLogin(data: PatientLoginPayload): Promise<LoginResponse> {
  const res = await client.post<LoginResponse>("/auth/patient-login", data);
  return res.data;
}

export async function getPatientMe(token?: string): Promise<PatientMe> {
  const headers = token ? { Authorization: `Bearer ${token}` } : undefined;
  const res = await client.get<PatientMe>("/auth/patient/me", { headers });
  return res.data;
}
