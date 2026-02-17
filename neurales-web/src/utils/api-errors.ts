import type { AxiosError } from "axios";

export interface ApiError {
  message: string;
  status?: number;
  details?: string;
}

/**
 * Transforme une erreur Axios en message utilisateur lisible
 */
export function parseApiError(error: unknown): ApiError {
  if (!error) {
    return { message: "Erreur inconnue." };
  }

  const axiosError = error as AxiosError<{ detail?: string; message?: string }>;

  // Erreur réseau (pas de réponse du serveur)
  if (axiosError.request && !axiosError.response) {
    return {
      message: "Impossible de joindre le serveur. Vérifie ta connexion.",
      details: "Erreur réseau",
    };
  }

  // Erreur avec réponse du serveur
  if (axiosError.response) {
    const status = axiosError.response.status;
    const data = axiosError.response.data;
    const detail = data?.detail || data?.message;

    switch (status) {
      case 400:
        return {
          message: detail || "Requête invalide.",
          status,
          details: "Données incorrectes",
        };
      case 401:
        return {
          message: "Session expirée. Reconnecte-toi.",
          status,
          details: "Non autorisé",
        };
      case 403:
        return {
          message: "Tu n'as pas les droits pour cette action.",
          status,
          details: "Accès refusé",
        };
      case 404:
        return {
          message: "Ressource introuvable.",
          status,
          details: "Non trouvé",
        };
      case 422:
        return {
          message: detail || "Données invalides ou manquantes.",
          status,
          details: "Validation échouée",
        };
      case 500:
        return {
          message: "Erreur serveur. Réessaye plus tard.",
          status,
          details: "Erreur interne",
        };
      case 503:
        return {
          message: "Service temporairement indisponible.",
          status,
          details: "Service indisponible",
        };
      default:
        return {
          message: detail || "Une erreur inattendue s'est produite.",
          status,
          details: `Erreur ${status}`,
        };
    }
  }

  // Timeout
  if (axiosError.code === "ECONNABORTED") {
    return {
      message: "La requête a pris trop de temps. Réessaye.",
      details: "Timeout",
    };
  }

  // Erreur générique
  return {
    message: "Une erreur inattendue s'est produite.",
    details: String(error),
  };
}

/**
 * Log l'erreur dans la console (dev mode)
 */
export function logError(error: unknown, context?: string) {
  if (import.meta.env.DEV) {
    console.error(`[API Error${context ? ` - ${context}` : ""}]`, error);
  }
}
