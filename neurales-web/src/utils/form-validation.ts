/**
 * Validation utilities pour les formulaires
 */

export interface ValidationRule {
  validate: (value: string) => boolean;
  message: string;
}

export const validatePatientName = (name: string): string[] => {
  const errors: string[] = [];

  if (!name || !name.trim()) {
    errors.push("Ce champ est obligatoire.");
    return errors;
  }

  if (name.length < 2) {
    errors.push("Minimum 2 caractères requis.");
  }

  if (name.length > 80) {
    errors.push("Maximum 80 caractères.");
  }

  if (/\d/.test(name)) {
    errors.push("Aucun chiffre autorisé.");
  }

  if (/[!@#$%^&*()+=\[\]{};:"'<>?,./\\|`~]/.test(name)) {
    errors.push("Aucun caractère spécial autorisé.");
  }

  if (/^\s+$/.test(name)) {
    errors.push("Peut pas être vide ou espaces seulement.");
  }

  return errors;
};

export const validateSecurityNumber = (secu: string): string[] => {
  const errors: string[] = [];

  if (!secu || !secu.trim()) {
    return errors; // Optionnel
  }

  if (!/^\d+$/.test(secu)) {
    errors.push("Uniquement des chiffres autorisés.");
  }

  if (secu.length !== 13) {
    errors.push("Exactement 13 chiffres requis.");
  }

  return errors;
};

export const validateDeviceName = (name: string): string[] => {
  const errors: string[] = [];

  if (!name || !name.trim()) {
    errors.push("Le nom du dispositif est obligatoire.");
    return errors;
  }

  if (name.length < 2) {
    errors.push("Minimum 2 caractères requis.");
  }

  if (name.length > 120) {
    errors.push("Maximum 120 caractères.");
  }

  if (/^\s+$/.test(name)) {
    errors.push("Peut pas être vide ou espaces seulement.");
  }

  return errors;
};

export const validateSessionName = (name: string): string[] => {
  const errors: string[] = [];

  if (!name || !name.trim()) {
    errors.push("Le nom de la session est obligatoire.");
    return errors;
  }

  if (name.length < 2) {
    errors.push("Minimum 2 caractères requis.");
  }

  if (name.length > 200) {
    errors.push("Maximum 200 caractères.");
  }

  return errors;
};

export const validateDuration = (duration: string | number): string[] => {
  const errors: string[] = [];

  if (!duration) {
    errors.push("La durée est obligatoire.");
    return errors;
  }

  const num = typeof duration === "string" ? parseFloat(duration) : duration;

  if (isNaN(num)) {
    errors.push("Doit être un nombre.");
  } else if (num <= 0) {
    errors.push("Doit être supérieur à 0.");
  } else if (num > 1000) {
    errors.push("Doit être inférieur à 1000 minutes.");
  }

  return errors;
};

export const validateThreshold = (threshold: string | number): string[] => {
  const errors: string[] = [];

  if (threshold === "" || threshold === undefined || threshold === null) {
    errors.push("Le seuil est obligatoire.");
    return errors;
  }

  const num = typeof threshold === "string" ? parseFloat(threshold) : threshold;

  if (isNaN(num)) {
    errors.push("Doit être un nombre.");
  } else if (num < 0 || num > 100) {
    errors.push("Doit être entre 0 et 100.");
  }

  return errors;
};

export const validateInternalId = (id: string): string[] => {
  const errors: string[] = [];

  if (!id || !id.trim()) {
    errors.push("L'identifiant interne est obligatoire.");
    return errors;
  }

  if (id.length < 2) {
    errors.push("Minimum 2 caractères requis.");
  }

  if (id.length > 50) {
    errors.push("Maximum 50 caractères.");
  }

  if (/^\s+$/.test(id)) {
    errors.push("Peut pas être vide ou espaces seulement.");
  }

  return errors;
};

export const validateDate = (date: string): string[] => {
  const errors: string[] = [];

  if (!date) {
    errors.push("La date est obligatoire.");
    return errors;
  }

  const dateObj = new Date(date);
  if (isNaN(dateObj.getTime())) {
    errors.push("Date invalide.");
    return errors;
  }

  // Vérifier que la date est dans le futur ou passé raisonnable
  const now = new Date();
  const age = now.getFullYear() - dateObj.getFullYear();

  if (age < 0) {
    errors.push("La date ne peut pas être dans le futur.");
  } else if (age > 150) {
    errors.push("Âge invalide (trop ancien).");
  }

  return errors;
};

export const hasErrors = (errorObj: Record<string, string>): boolean => {
  return Object.values(errorObj).some((err) => err !== "");
};
