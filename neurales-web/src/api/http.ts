import axios from "axios";

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 20000,
  withCredentials: true,
});

let accessToken: string | null = null;

export const setAccessToken = (token: string | null) => {
  accessToken = token;
};

http.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Intercepteur de réponse pour erreurs globales
http.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log en mode dev
    if (import.meta.env.DEV) {
      console.error("[HTTP Error]", {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        data: error.response?.data,
      });
    }

    // Gestion globale : si 401, déconnecter l'utilisateur
    if (error.response?.status === 401) {
      const currentPath = window.location.pathname;
      if (currentPath !== "/login") {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);
