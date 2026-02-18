import argparse
import base64
import hashlib
import secrets
from sqlalchemy import text

from app.data.db import engine


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def hash_password(password: str, iterations: int = 260000) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${_b64encode(salt)}${_b64encode(dk)}"


def _scalar_one_or_none(conn, sql: str, params: dict):
    return conn.execute(text(sql), params).scalar_one_or_none()


def _get_or_create_org(conn, nom: str, org_type: str, adresse: str | None):
    org_id = _scalar_one_or_none(
        conn,
        """
        SELECT organisation_id
        FROM public.t_organisation
        WHERE nom = :nom AND type = :type
        """,
        {"nom": nom, "type": org_type},
    )
    if org_id:
        return org_id

    return conn.execute(
        text(
            """
            INSERT INTO public.t_organisation (nom, type, adresse, created_at)
            VALUES (:nom, :type, :adresse, now())
            RETURNING organisation_id
            """
        ),
        {"nom": nom, "type": org_type, "adresse": adresse},
    ).scalar_one()


def _get_or_create_role(conn, code: str, libelle: str) -> int:
    role_id = _scalar_one_or_none(
        conn,
        """
        SELECT role_id FROM public.t_role WHERE code = :code
        """,
        {"code": code},
    )
    if role_id:
        return role_id

    return conn.execute(
        text(
            """
            INSERT INTO public.t_role (code, libelle)
            VALUES (:code, :libelle)
            RETURNING role_id
            """
        ),
        {"code": code, "libelle": libelle},
    ).scalar_one()


def _get_or_create_permission(conn, code: str, description: str) -> int:
    perm_id = _scalar_one_or_none(
        conn,
        """
        SELECT permission_id FROM public.t_permission WHERE code = :code
        """,
        {"code": code},
    )
    if perm_id:
        return perm_id

    return conn.execute(
        text(
            """
            INSERT INTO public.t_permission (code, description)
            VALUES (:code, :description)
            RETURNING permission_id
            """
        ),
        {"code": code, "description": description},
    ).scalar_one()


def _get_or_create_service(conn, nom: str, organisation_id: int) -> int:
    """Get or create a service reference"""
    service_id = _scalar_one_or_none(
        conn,
        """
        SELECT service_id FROM public.t_service 
        WHERE nom = :nom AND organisation_id = :org_id AND deleted_at IS NULL
        """,
        {"nom": nom, "org_id": organisation_id},
    )
    if service_id:
        return service_id

    return conn.execute(
        text(
            """
            INSERT INTO public.t_service (nom, organisation_id, created_at)
            VALUES (:nom, :org_id, now())
            RETURNING service_id
            """
        ),
        {"nom": nom, "org_id": organisation_id},
    ).scalar_one()


def _get_or_create_medecin(conn, nom: str, organisation_id: int) -> int:
    """Get or create a doctor reference"""
    medecin_id = _scalar_one_or_none(
        conn,
        """
        SELECT medecin_id FROM public.t_medecin 
        WHERE nom = :nom AND organisation_id = :org_id AND deleted_at IS NULL
        """,
        {"nom": nom, "org_id": organisation_id},
    )
    if medecin_id:
        return medecin_id

    return conn.execute(
        text(
            """
            INSERT INTO public.t_medecin (nom, organisation_id, created_at)
            VALUES (:nom, :org_id, now())
            RETURNING medecin_id
            """
        ),
        {"nom": nom, "org_id": organisation_id},
    ).scalar_one()


def _get_or_create_user(
    conn,
    nom: str,
    prenom: str,
    email: str,
    etat_compte: str,
    organisation_id: int,
    password_hash: str,
):
    user_id = _scalar_one_or_none(
        conn,
        """
        SELECT user_id FROM public.t_utilisateur WHERE email = :email
        """,
        {"email": email},
    )
    if user_id:
        conn.execute(
            text(
                """
                UPDATE public.t_utilisateur
                SET nom = :nom,
                    prenom = :prenom,
                    etat_compte = :etat,
                    organisation_id = :org_id,
                    password_hash = :hash
                WHERE user_id = :user_id
                """
            ),
            {
                "nom": nom,
                "prenom": prenom,
                "etat": etat_compte,
                "org_id": organisation_id,
                "hash": password_hash,
                "user_id": user_id,
            },
        )
        return user_id

    return conn.execute(
        text(
            """
            INSERT INTO public.t_utilisateur
                (nom, prenom, email, etat_compte, created_at, organisation_id, password_hash)
            VALUES
                (:nom, :prenom, :email, :etat, now(), :org_id, :hash)
            RETURNING user_id
            """
        ),
        {
            "nom": nom,
            "prenom": prenom,
            "email": email,
            "etat": etat_compte,
            "org_id": organisation_id,
            "hash": password_hash,
        },
    ).scalar_one()


def _get_or_create_device(conn, serial_number: str, marque_modele: str, connection_type: str, etat: str, organisation_id: int):
    device_id = _scalar_one_or_none(
        conn,
        """
        SELECT device_id FROM public.t_dispositif WHERE serial_number = :serial
        """,
        {"serial": serial_number},
    )
    if device_id:
        return device_id

    return conn.execute(
        text(
            """
            INSERT INTO public.t_dispositif
                (marque_modele, serial_number, connection_type, etat, organisation_id)
            VALUES
                (:marque_modele, :serial, :connection_type, :etat, :org_id)
            RETURNING device_id
            """
        ),
        {
            "marque_modele": marque_modele,
            "serial": serial_number,
            "connection_type": connection_type,
            "etat": etat,
            "org_id": organisation_id,
        },
    ).scalar_one()


def _get_or_create_channel(conn, device_id: int, nom: str, unite: str, sampling_rate_hz: int) -> int:
    channel_id = _scalar_one_or_none(
        conn,
        """
        SELECT channel_id FROM public.t_canal WHERE device_id = :device_id AND nom = :nom
        """,
        {"device_id": device_id, "nom": nom},
    )
    if channel_id:
        return channel_id

    return conn.execute(
        text(
            """
            INSERT INTO public.t_canal (nom, unite, sampling_rate_hz, device_id)
            VALUES (:nom, :unite, :sampling_rate_hz, :device_id)
            RETURNING channel_id
            """
        ),
        {"nom": nom, "unite": unite, "sampling_rate_hz": sampling_rate_hz, "device_id": device_id},
    ).scalar_one()


def _get_or_create_patient(
    conn,
    organisation_id: int,
    identifiant_interne: str,
    nom: str,
    prenom: str,
    date_naissance: str,
    sexe: str,
    notes: str | None,
    numero_securite_sociale: str | None,
    service: str | None,
    medecin_referent: str | None,
    remarque: str | None,
    service_id: int | None = None,
    medecin_referent_id: int | None = None,
) -> int:
    patient_id = _scalar_one_or_none(
        conn,
        """
        SELECT patient_id FROM public.t_patient
        WHERE organisation_id = :org_id AND identifiant_interne = :ident
        """,
        {"org_id": organisation_id, "ident": identifiant_interne},
    )
    if not patient_id and numero_securite_sociale:
        patient_id = _scalar_one_or_none(
            conn,
            """
            SELECT patient_id FROM public.t_patient
            WHERE numero_securite_sociale = :nss
            """,
            {"nss": numero_securite_sociale},
        )

    if patient_id:
        conn.execute(
            text(
                """
                UPDATE public.t_patient
                SET nom = :nom,
                    prenom = :prenom,
                    date_naissance = :date_naissance,
                    sexe = :sexe,
                    notes = :notes,
                    numero_securite_sociale = :nss,
                    service = :service,
                    medecin_referent = :medecin,
                    remarque = :remarque,
                    service_id = :service_id,
                    medecin_referent_id = :medecin_id
                WHERE patient_id = :patient_id
                """
            ),
            {
                "nom": nom,
                "prenom": prenom,
                "date_naissance": date_naissance,
                "sexe": sexe,
                "notes": notes,
                "nss": numero_securite_sociale,
                "service": service,
                "medecin": medecin_referent,
                "remarque": remarque,
                "service_id": service_id,
                "medecin_id": medecin_referent_id,
                "patient_id": patient_id,
            },
        )
        return patient_id

    return conn.execute(
        text(
            """
            INSERT INTO public.t_patient
                (identifiant_interne, date_naissance, sexe, notes, created_at, organisation_id,
                 prenom, numero_securite_sociale, service, medecin_referent, remarque, nom, service_id, medecin_referent_id)
            VALUES
                (:ident, :date_naissance, :sexe, :notes, now(), :org_id,
                 :prenom, :nss, :service, :medecin, :remarque, :nom, :service_id, :medecin_id)
            RETURNING patient_id
            """
        ),
        {
            "ident": identifiant_interne,
            "date_naissance": date_naissance,
            "sexe": sexe,
            "notes": notes,
            "org_id": organisation_id,
            "prenom": prenom,
            "nss": numero_securite_sociale,
            "service": service,
            "medecin": medecin_referent,
            "remarque": remarque,
            "nom": nom,
            "service_id": service_id,
            "medecin_id": medecin_referent_id,
        },
    ).scalar_one()


def seed(reset: bool, admin_password: str) -> None:
    with engine.begin() as conn:
        if reset:
            conn.execute(
                text(
                    """
                    TRUNCATE TABLE
                        t_valeur_signal,
                        t_echantillon,
                        t_canal,
                        t_configuration_session,
                        t_alerte,
                        t_indicateur,
                        t_export_fichier,
                        t_log_evenement,
                        t_session_mesure,
                        t_consentement,
                        t_patient,
                        t_associer,
                        t_definir,
                        t_permission,
                        t_role,
                        t_utilisateur,
                        t_dispositif,
                        t_organisation
                    RESTART IDENTITY CASCADE;
                    """
                )
            )

        org_id = _get_or_create_org(conn, "NeuralES", "clinique", "1 rue de la Demo")
        org_id_2 = _get_or_create_org(conn, "Hopital Nord", "hopital", "42 avenue du Soin")

        role_admin_id = _get_or_create_role(conn, "admin", "Administrateur")
        role_user_id = _get_or_create_role(conn, "clinician", "Clinicien")

        perm_read_id = _get_or_create_permission(conn, "patients:read", "Lire les patients")
        perm_write_id = _get_or_create_permission(conn, "patients:write", "Ecrire les patients")

        conn.execute(
            text(
                """
                INSERT INTO public.t_definir (role_id, permission_id)
                VALUES (:role_id, :perm_id), (:role_id, :perm2_id)
                ON CONFLICT DO NOTHING
                """
            ),
            {"role_id": role_admin_id, "perm_id": perm_read_id, "perm2_id": perm_write_id},
        )

        conn.execute(
            text(
                """
                INSERT INTO public.t_definir (role_id, permission_id)
                VALUES (:role_id, :perm_id)
                ON CONFLICT DO NOTHING
                """
            ),
            {"role_id": role_user_id, "perm_id": perm_read_id},
        )

        admin_user_id = _get_or_create_user(
            conn,
            nom="NeuralES",
            prenom="Admin",
            email="admin@neurales.com",
            etat_compte="actif",
            organisation_id=org_id,
            password_hash=hash_password(admin_password),
        )

        clinician_user_id = _get_or_create_user(
            conn,
            nom="Martin",
            prenom="Claire",
            email="claire.martin@neurales.com",
            etat_compte="actif",
            organisation_id=org_id,
            password_hash=hash_password("demo1234"),
        )

        conn.execute(
            text(
                """
                INSERT INTO public.t_associer (user_id, role_id, assigned_at)
                VALUES (:user_id, :role_id, now())
                ON CONFLICT DO NOTHING
                """
            ),
            {"user_id": admin_user_id, "role_id": role_admin_id},
        )

        conn.execute(
            text(
                """
                INSERT INTO public.t_associer (user_id, role_id, assigned_at)
                VALUES (:user_id, :role_id, now())
                ON CONFLICT DO NOTHING
                """
            ),
            {"user_id": clinician_user_id, "role_id": role_user_id},
        )

        device_id = _get_or_create_device(
            conn,
            serial_number="NEU-0001",
            marque_modele="NeuralES Pro",
            connection_type="usb",
            etat="actif",
            organisation_id=org_id,
        )

        # Add more test devices
        device_id_2 = _get_or_create_device(
            conn,
            serial_number="NEU-0003",
            marque_modele="Emotiv EPOC X",
            connection_type="bluetooth",
            etat="actif",
            organisation_id=org_id,
        )

        device_id_3 = _get_or_create_device(
            conn,
            serial_number="NEU-0004",
            marque_modele="Muse 2",
            connection_type="wifi",
            etat="inactif",
            organisation_id=org_id,
        )

        device_id_4 = _get_or_create_device(
            conn,
            serial_number="NEU-0005",
            marque_modele="OpenBCI Cyton",
            connection_type="usb",
            etat="defaillant",
            organisation_id=org_id,
        )

        # Create reference data for services and doctors
        service_neuro_id = _get_or_create_service(conn, "Neurologie", org_id)
        service_sommeil_id = _get_or_create_service(conn, "Sommeil", org_id)
        
        medecin_noel_id = _get_or_create_medecin(conn, "Dr Noel", org_id)
        medecin_petit_id = _get_or_create_medecin(conn, "Dr Petit", org_id)
        medecin_lenoir_id = _get_or_create_medecin(conn, "Dr Lenoir", org_id)

        patient_id = _get_or_create_patient(
            conn,
            organisation_id=org_id,
            identifiant_interne="PAT-0001",
            nom="Durand",
            prenom="Sophie",
            date_naissance="1988-03-12",
            sexe="femme",
            notes="RAS",
            numero_securite_sociale="1234567890123",
            service="Neurologie",
            medecin_referent="Dr Noel",
            remarque="Patient stable",
            service_id=service_neuro_id,
            medecin_referent_id=medecin_noel_id,
        )

        patient_id_2 = _get_or_create_patient(
            conn,
            organisation_id=org_id,
            identifiant_interne="PAT-0002",
            nom="Moreau",
            prenom="Hugo",
            date_naissance="1975-11-04",
            sexe="homme",
            notes="Suivi sommeil",
            numero_securite_sociale="9876543210987",
            service="Sommeil",
            medecin_referent="Dr Petit",
            remarque="Nouvelle evaluation",
            service_id=service_sommeil_id,
            medecin_referent_id=medecin_petit_id,
        )

        consent_id = conn.execute(
            text(
                """
                INSERT INTO public.t_consentement
                    (scope, status, consent_at, expires_at, withdrawn_at, collected_by_user_id, patient_id)
                VALUES
                    ('eeg', 'valid', now(), now() + interval '365 days', NULL, :user_id, :patient_id)
                RETURNING consent_id
                """
            ),
            {"user_id": admin_user_id, "patient_id": patient_id},
        ).scalar_one()

        session_id = conn.execute(
            text(
                """
                INSERT INTO public.t_session_mesure
                    (mode, started_at, ended_at, notes, app_version, device_id, consent_id,
                     patient_id, created_by_user_id, organisation_id)
                VALUES
                    ('rest', now() - interval '10 minutes', now(), 'Session de test', '1.0.0', :device_id,
                     :consent_id, :patient_id, :user_id, :org_id)
                RETURNING session_id
                """
            ),
            {
                "device_id": device_id,
                "consent_id": consent_id,
                "patient_id": patient_id,
                "user_id": clinician_user_id,
                "org_id": org_id,
            },
        ).scalar_one()

        conn.execute(
            text(
                """
                INSERT INTO public.t_configuration_session
                    (window_seconds, quality_min, fatigue_threshold, alert_cooldown_seconds, session_id)
                VALUES
                    (10, 70, 80, 60, :session_id)
                """
            ),
            {"session_id": session_id},
        )

        channel_id_1 = _get_or_create_channel(conn, device_id, "Fpz-Cz", "uV", 250)
        channel_id_2 = _get_or_create_channel(conn, device_id, "Pz-Oz", "uV", 250)

        sample_id = conn.execute(
            text(
                """
                INSERT INTO public.t_echantillon (timestamp_at, quality_score, session_id)
                VALUES (now() - interval '5 minutes', 90, :session_id)
                RETURNING sample_id
                """
            ),
            {"session_id": session_id},
        ).scalar_one()

        conn.execute(
            text(
                """
                INSERT INTO public.t_valeur_signal (sample_id, channel_id, valeur)
                VALUES (:sample_id, :channel_id, :valeur)
                """
            ),
            {"sample_id": sample_id, "channel_id": channel_id_1, "valeur": 12.34},
        )

        conn.execute(
            text(
                """
                INSERT INTO public.t_valeur_signal (sample_id, channel_id, valeur)
                VALUES (:sample_id, :channel_id, :valeur)
                """
            ),
            {"sample_id": sample_id, "channel_id": channel_id_2, "valeur": 9.87},
        )

        conn.execute(
            text(
                """
                INSERT INTO public.t_indicateur
                    (nom, valeur, confidence, window_start, window_end, session_id)
                VALUES
                    ('fatigue_ratio', 1.3, 0.92, now() - interval '10 minutes', now(), :session_id)
                """
            ),
            {"session_id": session_id},
        )

        conn.execute(
            text(
                """
                INSERT INTO public.t_alerte
                    (triggered_at, alert_type, severity, valeur, message, ack_at, ack_by_user_id, session_id)
                VALUES
                    (now() - interval '2 minutes', 'fatigue', 'medium', 82.0, 'Fatigue detectee',
                     now() - interval '1 minutes', :user_id, :session_id)
                """
            ),
            {"user_id": clinician_user_id, "session_id": session_id},
        )

        conn.execute(
            text(
                """
                INSERT INTO public.t_export_fichier
                    (created_at, format, path, checksum, created_by_user_id, session_id)
                VALUES
                    (now(), 'edf', '/exports/session_1.edf', 'checksum-demo', :user_id, :session_id)
                """
            ),
            {"user_id": clinician_user_id, "session_id": session_id},
        )

        conn.execute(
            text(
                """
                INSERT INTO public.t_log_evenement
                    (created_at, level, code, message, metadata, actor_user_id, session_id, organisation_id)
                VALUES
                    (now(), 'INFO', 'SESSION_CREATED', 'Session creee', '{"source":"seed"}',
                     :user_id, :session_id, :org_id)
                """
            ),
            {"user_id": clinician_user_id, "session_id": session_id, "org_id": org_id},
        )

        conn.execute(
            text(
                """
                INSERT INTO public.t_log_evenement
                    (created_at, level, code, message, metadata, actor_user_id, session_id, organisation_id)
                VALUES
                    (now(), 'INFO', 'PATIENT_CREATED', 'Patient cree', '{"source":"seed"}',
                     :user_id, NULL, :org_id)
                """
            ),
            {"user_id": admin_user_id, "org_id": org_id},
        )

        conn.execute(
            text(
                """
                INSERT INTO public.t_session_mesure
                    (mode, started_at, ended_at, notes, app_version, device_id, consent_id,
                     patient_id, created_by_user_id, organisation_id)
                VALUES
                    ('sleep', now() - interval '2 days', now() - interval '1 day 22 hours',
                     'Session sommeil', '1.0.0', :device_id, :consent_id,
                     :patient_id, :user_id, :org_id)
                """
            ),
            {
                "device_id": device_id,
                "consent_id": consent_id,
                "patient_id": patient_id_2,
                "user_id": clinician_user_id,
                "org_id": org_id,
            },
        )

        _get_or_create_device(
            conn,
            serial_number="NEU-0002",
            marque_modele="NeuralES Mobile",
            connection_type="wifi",
            etat="maintenance",
            organisation_id=org_id_2,
        )

        _get_or_create_device(
            conn,
            serial_number="HOP-0001",
            marque_modele="BioSemi ActiveTwo",
            connection_type="ethernet",
            etat="actif",
            organisation_id=org_id_2,
        )

        _get_or_create_patient(
            conn,
            organisation_id=org_id_2,
            identifiant_interne="PAT-1001",
            nom="Fabre",
            prenom="Lea",
            date_naissance="1992-07-18",
            sexe="femme",
            notes="A suivre",
            numero_securite_sociale=None,
            service="Neurologie",
            medecin_referent="Dr Lenoir",
            remarque=None,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="truncate all tables before seeding")
    parser.add_argument("--admin-password", default="admin123", help="password for admin user")
    args = parser.parse_args()

    seed(reset=args.reset, admin_password=args.admin_password)
    print("Seed completed.")


if __name__ == "__main__":
    main()
