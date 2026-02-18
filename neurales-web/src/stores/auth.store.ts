import { defineStore } from "pinia";
import * as AuthAPI from "@/api/auth.api";
import { setAccessToken } from "@/api/http";

type User = { user_id: number; prenom: string; nom: string; email: string; organisation_id: number; role?: string };

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as User | null,
    isReady: false,
    accessToken: null as string | null,
  }),
  getters: {
    isLogged: (state) => !!state.accessToken,
    displayName: (state) => (state.user ? `${state.user.prenom} ${state.user.nom}` : ""),
  },
  actions: {
    async login(email: string, password: string) {
      const res = await AuthAPI.login({ email, password });
      this.accessToken = res.access_token;
      setAccessToken(res.access_token);
      await this.fetchMe();
      this.isReady = true;
    },
    async refresh() {
      const res = await AuthAPI.refresh();
      this.accessToken = res.access_token;
      setAccessToken(res.access_token);
      await this.fetchMe();
      this.isReady = true;
    },
    async initialize() {
      if (this.isReady) return;
      try {
        await this.refresh();
      } catch {
        this.accessToken = null;
        setAccessToken(null);
        this.user = null;
        this.isReady = true;
      }
    },
    async fetchMe() {
      this.user = await AuthAPI.me();
    },
    async logout() {
      try {
        await AuthAPI.logout();
      } catch {
        // ignore network/logout errors
      }
      this.accessToken = null;
      setAccessToken(null);
      this.user = null;
      this.isReady = true;
    },
  },
});
