import { defineStore } from "pinia";
import * as AuthAPI from "@/api/auth.api";

type User = { user_id: number; prenom: string; nom: string; email: string; role?: string };

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as User | null,
    isReady: false,
  }),
  getters: {
    isLogged: () => !!localStorage.getItem("access_token"),
    displayName: (state) => (state.user ? `${state.user.prenom} ${state.user.nom}` : ""),
  },
  actions: {
    async login(email: string, password: string) {
      const res = await AuthAPI.login({ email, password });
      localStorage.setItem("access_token", res.access_token);
      await this.fetchMe();
    },
    async fetchMe() {
      this.user = await AuthAPI.me();
      this.isReady = true;
    },
    logout() {
      localStorage.removeItem("access_token");
      this.user = null;
      this.isReady = true;
    },
  },
});
