# Authentification NeuralES (Web + API)

Ce document explique le fonctionnement complet de l'authentification entre le front (neurales-web) et le backend (FastAPI), en utilisant :
- Access token JWT en memoire cote front.
- Refresh token JWT stocke dans un cookie HttpOnly.

## Objectif

- Minimiser l'exposition du token d'acces (il n'est pas stocke en localStorage).
- Permettre un renouvellement automatique via un refresh token HttpOnly.
- Simplifier l'utilisation cote front (Axios ajoute le Bearer automatiquement).

## Vue d'ensemble

1. L'utilisateur soumet le formulaire de connexion.
2. Le backend valide les identifiants.
3. Le backend renvoie un access token (body JSON) et depose un refresh token (cookie HttpOnly).
4. Le front stocke l'access token en memoire et l'ajoute dans le header Authorization.
5. Au rechargement ou demarrage, le front appelle /auth/refresh pour regenerer un access token.
6. En logout, le front appelle /auth/logout et le backend supprime le cookie refresh.

## Endpoints utilises

- POST /auth/login
  - Entree : { email, password }
  - Sortie : { access_token, token_type }
  - Effet : set cookie refresh_token HttpOnly

- POST /auth/refresh
  - Entree : cookie refresh_token
  - Sortie : { access_token, token_type }
  - Effet : set cookie refresh_token HttpOnly (rotation)

- POST /auth/logout
  - Effet : supprime le cookie refresh_token

- GET /auth/me
  - Header : Authorization: Bearer <access_token>
  - Sortie : profil utilisateur

## Cote front (neurales-web)

- Le store Pinia (auth.store.ts) gere :
  - accessToken en memoire
  - initialize() : appel /auth/refresh au demarrage
  - login() : appel /auth/login
  - logout() : appel /auth/logout
  - fetchMe() : appel /auth/me

- Axios (http.ts) :
  - withCredentials: true pour envoyer les cookies
  - ajoute Authorization: Bearer <access_token> si present

## Cote backend (FastAPI)

- /auth/login :
  - verifie l'admin (email + mot de passe)
  - genere access token (court)
  - genere refresh token (long)
  - pose le refresh token en cookie HttpOnly

- /auth/refresh :
  - lit le cookie refresh
  - valide le JWT + type=refresh
  - regenere access token + refresh token
  - repose le cookie refresh

- /auth/logout :
  - supprime le cookie refresh

## Cookies et CORS (important)

- withCredentials: true cote front
- Cote backend, CORS avec allow_credentials=true
- allow_origins ne doit pas etre "*" quand allow_credentials=true
- Pour un front sur un autre domaine : SameSite=None et Secure=true

## Sequence (simplifie)

1) LOGIN
Front -> POST /auth/login { email, password }
Backend -> set-cookie refresh_token + JSON access_token
Front -> stocke access_token en memoire, puis GET /auth/me

2) REFRESH (demarrage)
Front -> POST /auth/refresh (cookie)
Backend -> set-cookie refresh_token + JSON access_token
Front -> met a jour access_token, puis GET /auth/me

3) LOGOUT
Front -> POST /auth/logout
Backend -> supprime cookie refresh
Front -> purge access_token et user

## Schema sequence (texte)

Client(Web) -> POST /auth/login { email, password }
API -> Set-Cookie: refresh_token=...; HttpOnly; SameSite=...; Secure?
API -> 200 { access_token, token_type }
Client -> GET /auth/me (Authorization: Bearer access_token)
API -> 200 { user }

Client (au demarrage) -> POST /auth/refresh (cookie refresh)
API -> Set-Cookie: refresh_token=... (rotation)
API -> 200 { access_token, token_type }
Client -> GET /auth/me (Authorization: Bearer access_token)

Client -> POST /auth/logout
API -> Set-Cookie: refresh_token=; Max-Age=0 (suppression)
Client -> purge access_token + user

## Details techniques (exemples)

### Login

Requete :
POST /auth/login
Content-Type: application/json

{ "email": "admin@neurales.com", "password": "admin123" }

Reponse :
Set-Cookie: refresh_token=<jwt>; HttpOnly; Path=/; SameSite=Lax
{ "access_token": "<jwt>", "token_type": "bearer" }

### Refresh

Requete :
POST /auth/refresh
Cookie: refresh_token=<jwt>

Reponse :
Set-Cookie: refresh_token=<new-jwt>; HttpOnly; Path=/; SameSite=Lax
{ "access_token": "<jwt>", "token_type": "bearer" }

### Me

Requete :
GET /auth/me
Authorization: Bearer <access_token>

Reponse :
{ "user_id": 1, "prenom": "Admin", "nom": "NeuralES", "email": "admin@neurales.com", "role": "admin" }

### Logout

Requete :
POST /auth/logout

Reponse :
Set-Cookie: refresh_token=; Max-Age=0; Path=/
{ "ok": true }

## Notes

- L'access token n'est jamais sauvegarde sur disque.
- Le refresh token est inaccessible au JS (HttpOnly).
- Le WS /eeg/stream doit accepter l'auth par cookie si besoin.
