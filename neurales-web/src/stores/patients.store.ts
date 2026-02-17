import { defineStore } from "pinia";
import * as PatientsAPI from "@/api/patients.api";

export const usePatientsStore = defineStore("patients", {
  actions: {
    async createPatient(payload: PatientsAPI.PatientCreatePayload) {
      return PatientsAPI.createPatient(payload);
    },
  },
});
