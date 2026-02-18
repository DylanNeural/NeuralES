-- Migration: Add refresh token storage for revocation support
-- Date: 2026-02-18
-- Purpose: Store refresh tokens in DB for rotation, revocation, and audit
--

CREATE TABLE IF NOT EXISTS public.t_refresh_token (
    jti VARCHAR(64) PRIMARY KEY,
    user_id INTEGER NOT NULL,
    issued_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP NULL,
    replaced_by_jti VARCHAR(64) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    FOREIGN KEY (user_id) REFERENCES public.t_utilisateur(user_id) ON DELETE CASCADE
);

-- Index for lookups by user
CREATE INDEX IF NOT EXISTS idx_refresh_token_user
    ON public.t_refresh_token(user_id);

-- Index for lookups by jti (already primary key, but explicit for clarity)
CREATE INDEX IF NOT EXISTS idx_refresh_token_revoked
    ON public.t_refresh_token(revoked_at, expires_at);
