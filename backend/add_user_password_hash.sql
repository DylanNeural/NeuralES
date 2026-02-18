-- Ajoute le champ password_hash pour l'authentification
ALTER TABLE public.t_utilisateur
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
