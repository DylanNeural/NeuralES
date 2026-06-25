import { create } from "zustand";
import * as SecureStore from "expo-secure-store";
import { TOKEN_KEY } from "../api/client";
import type { PatientMe } from "../api/auth";

interface AuthState {
  token: string | null;
  patient: PatientMe | null;
  isLoading: boolean;
  loadToken: () => Promise<void>;
  login: (token: string, patient: PatientMe) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  patient: null,
  isLoading: true,

  loadToken: async () => {
    const token = await SecureStore.getItemAsync(TOKEN_KEY);
    set({ token, isLoading: false });
  },

  login: async (token: string, patient: PatientMe) => {
    await SecureStore.setItemAsync(TOKEN_KEY, token);
    set({ token, patient });
  },

  logout: async () => {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    set({ token: null, patient: null });
  },
}));
