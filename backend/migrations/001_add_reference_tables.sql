-- Migration: Add reference tables and soft-delete support
-- Date: 2026-02-17
-- Purpose: 
--   1. Create t_service and t_medecin reference tables with FK support
--   2. Add deleted_at columns for soft-delete across all tables
--   3. Add indexes for performance
--   4. Document enum values

-- =====================================================
-- PART 1: Create Reference Tables
-- =====================================================

-- Create t_service table
CREATE TABLE IF NOT EXISTS public.t_service (
    service_id SERIAL PRIMARY KEY,
    nom VARCHAR(120) NOT NULL,
    organisation_id INTEGER NOT NULL,
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    FOREIGN KEY (organisation_id) REFERENCES public.t_organisation(organisation_id) ON DELETE CASCADE,
    UNIQUE(nom, organisation_id)
);

-- Create t_medecin table
CREATE TABLE IF NOT EXISTS public.t_medecin (
    medecin_id SERIAL PRIMARY KEY,
    nom VARCHAR(120) NOT NULL,
    organisation_id INTEGER NOT NULL,
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    FOREIGN KEY (organisation_id) REFERENCES public.t_organisation(organisation_id) ON DELETE CASCADE,
    UNIQUE(nom, organisation_id)
);

-- =====================================================
-- PART 2: Add FK columns to t_patient
-- =====================================================

ALTER TABLE public.t_patient
ADD COLUMN IF NOT EXISTS service_id INTEGER,
ADD COLUMN IF NOT EXISTS medecin_referent_id INTEGER,
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;

-- =====================================================
-- PART 3: Add deleted_at to all tables for soft-delete
-- =====================================================

ALTER TABLE public.t_utilisateur ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;
ALTER TABLE public.t_organisation ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;
ALTER TABLE public.t_dispositif ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;
ALTER TABLE public.t_canal ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;
ALTER TABLE public.t_session_mesure ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;

-- =====================================================
-- PART 4: Create Indexes for Performance
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_service_organisation ON public.t_service(organisation_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_medecin_organisation ON public.t_medecin(organisation_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_patient_organisation_deleted ON public.t_patient(organisation_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_dispositif_organisation_deleted ON public.t_dispositif(organisation_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_session_organisation_deleted ON public.t_session_mesure(organisation_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_utilisateur_email_deleted ON public.t_utilisateur(email) WHERE deleted_at IS NULL;
