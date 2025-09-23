# AlloCar — Cahier des charges Backend (Flask)

## 0) Objectif & portée

* Construire une **API REST** sécurisée, performante et documentée pour l’app de covoiturage **AlloCar**.
* Couvre : **auth**, **KYC**, **utilisateurs & véhicules**, **trajets**, **réservations**, **paiements (Wave/OM/MTN/Carte)**, **wallet**, **messagerie**, **ratings**, **support**, **admin**, **webhooks**, **analytics**, **observabilité**.
* Cibles : **mobile Flutter**, **web Angular**, **admin web**.
* Tous les identifiants sont des **UUID v4** (base app + ressources + relations).

---

## 1) Stack & conventions

* **Langage** : Python 3.12
* **Framework** : Flask (Blueprints) + Flask-RESTX/Flask-Smorest (OpenAPI)
* **ORM** : SQLAlchemy 2.x + **Alembic** (migrations)
* **DB** : PostgreSQL 15 + **PostGIS** (géoloc)
* **Cache/Queues** : Redis + **Celery** (tâches async)
* **Temps réel** : Flask-SocketIO (chat + position conducteur)
* **Auth** : JWT (flask-jwt-extended) + OAuth social (Google/Apple via authlib)
* **Validation** : Marshmallow/Pydantic-core (au choix de l’équipe)
* **Stockage** : S3 compatible (MinIO en dev)
* **Notifs** : FCM (push), SMTP provider (emails), SMS agrégateur local
* **Carto** : OSRM/Mapbox (services externes)
* **Logs/APM** : structuré JSON + Prometheus metrics + Sentry
* **ID** : `UUID` (string, canonical) — **toutes** les tables, y compris pivot.

**Conventions API**

* Préfixe : `/api/v1`
* JSON seulement. Encodage UTF-8. Heures **UTC ISO-8601**.
* **Pagination** : `page`, `page_size` (max 100), renvoie `total`, `page_count`.
* **Tri** : `sort=field,-created_at`
* **Filtre** : paramètres query (ex: `status=in:paid,accepted` ; `date_gte=...`).
* **Idempotency** : header `Idempotency-Key` (pour POST sensibles : paiements, réservations).
* **Rate limit** : par IP + par user (ex: 60 req/min).
* **Sécurité** : CORS strict (origins front), headers sécurisés, TLS obligatoire.

---

## 2) Architecture & dossiers

```
backend/
  app.py (création app + extensions)
  config.py
  extensions/
    db.py, migrate.py, jwt.py, cache.py, celery.py, s3.py, mail.py, socketio.py, limiter.py, logger.py
  common/
    errors.py, responses.py, auth.py, security.py, utils.py, geo.py, validators.py, enums.py
  domain/
    users/, kyc/, vehicles/, trips/, bookings/, payments/, wallet/, messages/,
    ratings/, disputes/, promos/, referrals/, admin/, reports/, audit/
      models.py
      schemas.py
      routes.py
      services.py
      tasks.py
      repository.py
      signals.py (optionnel)
  integrations/
    wave/, orange_money/, mtn_momo/, stripe/, fcm/, sms/, osrm/, mapbox/
      client.py, webhook.py, adapters.py
  migrations/
  tests/
    unit/, integration/, e2e/, data/
  scripts/
    seed.py, manage.py
```

---

## 3) Modèle de données (schéma logique)

> Types : `UUID` (pk/fk), `TIMESTAMP WITH TIME ZONE`, `NUMERIC(12,2)` pour montants, `GEOGRAPHY(POINT, 4326)`.

### 3.1 Identité & KYC

* **users**

  * `id: UUID`, `phone`, `email`, `password_hash`, `first_name`, `last_name`, `gender?`, `birthdate?`
  * `photo_url?`, `is_driver: bool`, `is_active: bool`, `is_phone_verified: bool`, `is_email_verified: bool`
  * `rating_avg: numeric(3,2) default 0`, `rating_count: int default 0`
  * `created_at`, `updated_at`
* **kyc\_documents**

  * `id: UUID`, `user_id: UUID fk users`
  * `doc_type: enum(cni,passport,permis)`, `doc_number`, `front_url`, `back_url?`
  * `status: enum(pending,approved,rejected)`, `notes?`, `reviewed_by? (admin_id UUID)`, `reviewed_at?`
  * `created_at`, `updated_at`

### 3.2 Véhicules

* **vehicles**

  * `id`, `user_id`, `make`, `model`, `color`, `plate_number` (unique), `seats_total: int`, `comfort_level: enum(basic,standard,comfort)`
  * `year?`, `verified: bool`
  * `created_at`, `updated_at`

### 3.3 Trajets & arrêts

* **trips**

  * `id`, `driver_id: UUID fk users`,
  * `origin_point: GEOGRAPHY(POINT,4326)`, `origin_text`,
  * `destination_point`, `destination_text`,
  * `departure_time: timestamp`, `arrival_eta: timestamp?`
  * `price_per_seat: numeric`, `seats_available: int`, `luggage_policy?`, `rules?`
  * `allow_auto_accept: bool default false`
  * `status: enum(draft,published,ongoing,completed,cancelled)`
  * `created_at`, `updated_at`
* **trip\_stops**

  * `id`, `trip_id`, `order: int`
  * `point: GEOGRAPHY(POINT,4326)`, `label`, `pickup_allowed: bool`, `dropoff_allowed: bool`

### 3.4 Réservations & QR

* **bookings**

  * `id`, `trip_id`, `passenger_id`, `seats: int`
  * `amount_total: numeric`, `status: enum(pending,accepted,paid,cancelled,completed)`
  * `qr_code: string`, `created_at`, `updated_at`
* **booking\_events** (audit de statut)

  * `id`, `booking_id`, `from_status`, `to_status`, `by (user/admin/system)`, `meta JSONB`, `created_at`

### 3.5 Paiements & Wallet

* **payments**

  * `id`, `booking_id`, `user_id`, `method: enum(wave,orange,mtn,card,wallet)`, `provider_ref?`
  * `amount`, `currency: 'XOF'`, `fees: numeric default 0`, `status: enum(init,authorized,paid,failed,refunded)`
  * `raw_payload JSONB`, `created_at`, `updated_at`
* **wallets**

  * `id`, `user_id`, `balance: numeric default 0`, `currency: 'XOF'`, `updated_at`
* **wallet\_txns**

  * `id`, `wallet_id`, `type: enum(credit,debit)`, `amount`, `source: enum(refund,topup,payout,promo)`, `ref?`, `status`, `created_at`

### 3.6 Messagerie & live

* **messages**

  * `id`, `booking_id`, `from_user_id`, `type: enum(text,image)`, `content`, `created_at`
* **driver\_locations** (optionnel, si persistance)

  * `id`, `trip_id`, `driver_id`, `point`, `created_at`

### 3.7 Réputation, promo, parrainage, litiges

* **ratings**

  * `id`, `from_user_id`, `to_user_id`, `booking_id`, `stars: int(1..5)`, `comment?`, `created_at`
* **promos**

  * `id`, `code unique`, `type: enum(amount,percent)`, `value`, `max_uses`, `per_user_limit`, `starts_at`, `ends_at`, `status`
* **referrals**

  * `id`, `referrer_id`, `referee_id`, `bonus_referrer`, `bonus_referee`, `status`, `created_at`
* **disputes**

  * `id`, `booking_id`, `opened_by`, `category`, `description`, `status`, `resolution?`, `resolved_by?`, `resolved_at?`, `created_at`

### 3.8 Admin & audit

* **admin\_users**

  * `id`, `email`, `password_hash`, `role: enum(super,ops,support,finance,compliance)`, `is_active`, `last_login?`
* **audit\_logs**

  * `id`, `actor_type: enum(user,admin,system)`, `actor_id`, `action`, `entity`, `entity_id`, `meta JSONB`, `created_at`

---

## 4) États & règles métiers

### 4.1 Réservation (Booking) — machine à états

`pending → accepted → paid → completed`
`pending/accepted/paid → cancelled` (règles d’annulation)

* **Création** : `pending`.
* **Acceptation** par conducteur (ou auto si `allow_auto_accept=true`) → `accepted`.
* **Paiement** confirmé (webhook provider) → `paid`.
* **Check-in + start ride + end ride** → `completed`.
* **Annulation** : règles dynamiques (fenêtres horaires, frais, remboursements wallet/paiement).

### 4.2 Paiement — machine à états

`init → authorized? → paid`, `failed`, `refunded`.

* **Webhook** obligatoire pour `paid/failed`.
* **Idempotency** des webhooks par `provider_ref`+signature.

### 4.3 KYC

`pending → approved | rejected` avec `notes`, `reviewed_by`.

---

## 5) Endpoints (exhaustif)

> Tous les chemins préfixés par `/api/v1`. Les ressources renvoient des **UUID**.
> Protection : `public`, `auth:user`, `auth:driver`, `auth:admin`, scopes par rôle.

### 5.1 Auth & profil (public / auth\:user)

* `POST /auth/register` — body: `{phone|email, password?}` → OTP (si phone) ou validation email.
* `POST /auth/login` — `{identifier, password}` → `{access_token, refresh_token, user}`
* `POST /auth/token/refresh`
* `POST /auth/otp/send` / `POST /auth/otp/verify`
* `POST /auth/social/{provider}` (Google/Apple) — échange token → JWT
* `GET /me` — infos profil
* `PATCH /me` — modification profil (nom, photo, préférences)
* `POST /me/photo` — presigned URL S3
* `POST /me/kyc` — upload docs, crée `kyc_document`
* `GET /me/kyc/status`

### 5.2 Véhicules (auth\:driver)

* `GET /vehicles` (mes véhicules)
* `POST /vehicles` — créer véhicule (UUID)
* `GET /vehicles/{id}`, `PATCH /vehicles/{id}`, `DELETE /vehicles/{id}`

### 5.3 Trajets (auth\:driver + public search)

* `POST /trips` — créer (draft/published)
* `GET /trips/{id}`
* `PATCH /trips/{id}` — modifs (heure, prix, sièges… si règles ok)
* `DELETE /trips/{id}` — si pas de booking payé
* `POST /trips/{id}/publish`, `POST /trips/{id}/cancel`
* `POST /trips/{id}/stops` (bulk), `GET /trips/{id}/stops`
* **Recherche publique** :
  `GET /trips/search?from=lat,lon&to=lat,lon&date=YYYY-MM-DD&radius_km=&price_min=&price_max=&seats>=&comfort=&driver_rating>=`

### 5.4 Réservations (auth\:user)

* `POST /bookings` — `{trip_id, seats}` → `pending`
* `GET /bookings/{id}`, `GET /bookings?role=passenger|driver&status=...`
* `POST /bookings/{id}/accept` (driver)
* `POST /bookings/{id}/reject` (driver)
* `POST /bookings/{id}/cancel` (selon règles)
* `POST /bookings/{id}/checkin` (QR/code)
* `POST /bookings/{id}/start-ride` (driver)
* `POST /bookings/{id}/end-ride` (driver)

### 5.5 Paiements & wallet (auth\:user)

* `POST /payments/init` — `{booking_id, method}` → crée payment (status=init) + redirection/provider payload
* `POST /payments/webhook/{provider}` — **public** (signature requise) → met à jour `paid/failed`
* `GET /payments/{id}`
* `GET /wallet` — solde
* `POST /wallet/topup` — via provider
* `POST /wallet/withdraw` — demande retrait (rules)
* `GET /wallet/txns?type=&status=&period=`

### 5.6 Messagerie & live (auth\:user)

* `GET /bookings/{id}/messages` — pagination
* `POST /bookings/{id}/messages` — `{content, type}`
* **WebSocket** :

  * `/ws/bookings/{id}` — chat temps réel
  * `/ws/trips/{id}/driver-location` — position driver (broadcast aux passagers réservés)

### 5.7 Ratings & support (auth\:user)

* `POST /ratings` — `{booking_id, to_user_id, stars, comment?}`
* `GET /users/{id}/ratings` — pagination
* `POST /disputes` — créer ticket litige
* `GET /disputes/{id}`, `PATCH /disputes/{id}` (admin)

### 5.8 Promos & parrainage (auth\:user/admin)

* `POST /promos/validate` — vérifie code pour un user/booking
* `POST /referrals/use` — applique parrainage à l’inscription
* Admin CRUD promos/referrals : voir section admin

### 5.9 Admin (auth\:admin, rôles)

* `POST /admin/login` (JWT admin séparé ou même issuer avec scope)
* **Utilisateurs** :
  `GET /admin/users?query=&status=&created_from=...`,
  `GET /admin/users/{id}`, `PATCH /admin/users/{id}` (activer/suspendre/reset MFA)
* **KYC** :
  `GET /admin/kyc/pending`,
  `POST /admin/kyc/{id}/approve`, `POST /admin/kyc/{id}/reject` (notes)
* **Trajets** :
  `GET /admin/trips?status=`, `PATCH /admin/trips/{id}` (annulation admin, modération)
* **Réservations** :
  `GET /admin/bookings?status=`, `PATCH /admin/bookings/{id}` (arbitrage)
* **Paiements & Payouts** :
  `GET /admin/payments?status=&method=`,
  `POST /admin/payouts/run` (batch payouts conducteurs),
  `GET /admin/wallet/txns/export?format=csv|xlsx`
* **Promos** :
  `GET/POST/PATCH /admin/promos`, activation/désactivation
* **Disputes** :
  `GET /admin/disputes?status=`, `PATCH /admin/disputes/{id}`
* **Rapports** :
  `GET /admin/reports/finance?period=`,
  `GET /admin/reports/usage?period=`,
  export CSV/XLSX/PDF
* **Audit** :
  `GET /admin/audit-logs?actor=&entity=&date_from=...`

---

## 6) Intégrations paiements (process)

### 6.1 Wave / Orange Money / MTN MoMo (XOF)

* **Init** (`POST /payments/init`) : crée `payment(id UUID, status=init)` + **intent** auprès du provider, renvoie payload/redirection.
* **Notification** : provider appelle `POST /payments/webhook/{provider}` (signé + secret + idempotent).
* **Vérif** : vérifier signature, `provider_ref`, montants, statut, `Idempotency-Key`.
* **Mise à jour** :

  * `paid` → `payments.status=paid`, `bookings.status=paid`, décrément `trip.seats_available`, écriture commissions + éventuels frais, mise à jour **wallet** si nécessaire (cashback/promo).
  * `failed` → `payments.status=failed` (pas de changement booking).
* **Remboursements** : endpoint admin/service pour créer `refund` via provider + `wallet_txn` si partiel.

### 6.2 Payouts conducteurs

* Tâche **Celery** planifiable : agrège `bookings.completed` – commissions – frais → **payout**.
* Statuts : `scheduled → processing → done/failed`.
* Export des remises disponibles.

---

## 7) Règles d’annulation & frais

* **Variables admin** : fenêtres (X heures), pourcentages (Y%), no-show (Z%), plancher/plafond par axe.
* **Calcul** :

  * Passager annule : si `< Xh` → frais Y% (priorité wallet).
  * Conducteur annule `< Xh` → pénalité (score + éventuelle amende retenue sur futurs payouts).
* **Automatisation** : Celery calcule et applique, écrit `wallet_txns` et met à jour `payments` si remboursement.

---

## 8) Sécurité

* **JWT** accès/refresh (exp courts), rotation refresh, **revoke list** (Redis).
* **Scopes/Rôles** : routes protégées par décorateurs (user/driver/admin + rôle admin).
* **Protection Webhooks** : signatures HMAC, replay protection (nonce+ts).
* **Stockage KYC** : S3 privé + URLs signées, **jamais** servir direct-public.
* **PII** : chiffrement au repos de champs sensibles (optionnel via pgcrypto/KMS).
* **Rate limiting** : Flask-Limiter (IP+user).
* **Permissions données** : un user ne voit que ses bookings, messages, wallet, etc.

---

## 9) Observabilité & qualité

* **Logs** JSON (request id, user id, status), niveaux (INFO/WARN/ERROR).
* **APM/Tracing** (OpenTelemetry) si possible.
* **Metrics Prometheus** : `http_requests_total`, latence P95, erreurs 4xx/5xx, succès paiement, taux conversion.
* **Sentry** pour exceptions.
* **Audits** : toute action critique → `audit_logs`.

---

## 10) Tâches asynchrones (Celery)

* Envoi **notifications** (push/email/SMS).
* **Réconciliations** paiements quotidiennes.
* **Payouts** hebdo/quotidiens.
* **Rappels** trajets (H-24 / H-2).
* **Nettoyage** sessions, tokens expirés, OTP.
* **Indexation**/cache des recherches populaires.
* **Géocodage inverse** et enrichissement adresses (optionnel).

---

## 11) Recherche & géo

* **PostGIS** pour requêtes rayon/nearest (index GIST).
* Normaliser inputs : bbox, rayon par défaut (ex: 25 km intra-urbain).
* OSRM/Mapbox pour ETA/distance (côté service `integrations/osrm`).

---

## 12) Spéc de réponses & erreurs

### 12.1 Enveloppe standard

```json
{
  "data": { ... }, 
  "meta": { "request_id": "uuid", "pagination": { "page":1, "page_size":20, "total":120, "page_count":6 } }
}
```

### 12.2 Erreurs

```json
{
  "error": {
    "code": "booking_conflict",
    "message": "Not enough seats available",
    "details": {"available": 1, "requested": 3}
  }
}
```

**Codes communs** :
`validation_error`, `auth_required`, `forbidden`, `not_found`, `conflict`, `rate_limited`,
`payment_failed`, `webhook_invalid_signature`, `kyc_required`, `insufficient_funds`.

---

## 13) Exemples d’API (schémas)

### 13.1 Création trajet

**POST** `/api/v1/trips`

```json
{
  "origin": {"lat":5.3575,"lon":-4.0083,"text":"Abidjan, Plateau"},
  "destination": {"lat":6.8190,"lon":-5.2760,"text":"Yamoussoukro"},
  "departure_time":"2025-10-02T08:30:00Z",
  "price_per_seat": 6000,
  "seats_available": 3,
  "allow_auto_accept": true,
  "luggage_policy":"1 valise cabine",
  "rules":"Non-fumeur"
}
```

**201** → `data.id (UUID)`, `status: "published"` si publication directe.

### 13.2 Init paiement

**POST** `/api/v1/payments/init`

```json
{
  "booking_id": "1c2ab8f2-4e3a-4fd0-a3d2-0a07ec6ef0a2",
  "method": "wave"
}
```

**200** → payload provider (intent), `payment.id`.

---

## 14) Admin — rôles & permissions

| Ressource          | super |   ops | support | finance | compliance |
| ------------------ | ----: | ----: | ------: | ------: | ---------: |
| Users CRUD         |     ✓ | edit- |    read |    read |       read |
| KYC review         |     ✓ |       |         |         |          ✓ |
| Trips modération   |     ✓ |     ✓ |         |         |            |
| Bookings arbitrage |     ✓ |     ✓ |       ✓ |         |            |
| Payments & payouts |     ✓ |       |         |       ✓ |            |
| Promos/Referrals   |     ✓ |     ✓ |         |         |            |
| Disputes           |     ✓ |     ✓ |       ✓ |         |          ✓ |
| Reports export     |     ✓ |     ✓ |         |       ✓ |            |
| Audit logs         |     ✓ |  read |         |         |            |

---

## 15) Performance & SLA

* Latence **P95** endpoints clés `< 300 ms`, recherche `< 2 s`.
* **Disponibilité** cible : 99.5%.
* Index DB : GIST (géographie), btrees sur `created_at`, `status`, `driver_id`, `trip_id`, `user_id`.
* Cache : résultats de recherche, profils, configs système.
* **N+1** : interdits (use `selectinload/joinedload`).

---

## 16) Tests & CI/CD

* **Tests unitaires** (domain/services), **intégration** (DB, webhooks), **contract tests** (schémas OpenAPI).
* **E2E** (collections Postman/Playwright API).
* **Coverage** cible: 80%+.
* **Pipeline** : lint (ruff/flake8), type-check (mypy), tests, build image, migrations Alembic, déploiement (blue/green).
* **Seeds** : script `scripts/seed.py` (users drivers, trajets démo Abidjan↔Yamoussoukro).

---

## 17) Documentation

* **OpenAPI 3.1** auto-générée (Flask-Smorest/RESTX) à `/api/docs`.
* **Guides** internes : onboarding dev, exécution locale (docker-compose), playbooks incident, catalogue erreurs.
* **Changelog** versionné (SemVer de l’API).

---

## 18) Séquences métier (résumé)

### 18.1 Réservation payée

1. User crée **booking (pending)**.
2. Driver **accepte** → booking **accepted** (ou auto).
3. User lance **/payments/init** (Wave) → provider intent.
4. **Webhook** provider → `payments.paid` → `bookings.paid` → `trip.seats_available--`.
5. Rappels (H-24/H-2), check-in QR → start → end → **completed**.
6. Inclus dans **payout** du driver.

### 18.2 Annulation & remboursement

* Si conditions → **refund** partiel/total via provider, écriture **wallet\_txn** si nécessaire.

### 18.3 KYC

* Upload doc → `pending` → admin **approve/reject**.
* **Obligatoire** pour publier trajets et recevoir payouts.

---

## 19) Variables & paramètres système (admin-config)

* Frais plateforme (% + fixe), frais annulation (%), fenêtres (Xh), no-show (Z%).
* Plancher/plafond prix par axes populaires.
* Seuil **payout** minimal.
* Email/SMS templates (id).
* Toggles : `allow_auto_accept`, `require_kyc_for_driver`, `enable_wallet`.

---

## 20) Livrables attendus de l’équipe backend

1. **Projet Flask** structuré (Blueprints + extensions) avec **OpenAPI** complet.
2. **Migrations Alembic** (UUID par défaut, PostGIS activé).
3. **Intégrations paiements** (Wave v1, hooks signés + idempotence) + stubs OM/MTN/Stripe.
4. **Gestion des états** (Booking/Payment/KYC) conforme aux machines à états ci-dessus.
5. **WebSockets** (chat + position) et **notifications** (FCM/email/SMS).
6. **Tâches Celery** : rappels, payouts, réconciliations, nettoyages.
7. **Sécurité** (JWT, rôles, rate limit, validation stricte, audit).
8. **Observabilité** (logs JSON, metrics Prometheus, Sentry).
9. **Tests** (unit/intégration/e2e) + **pipeline CI/CD**.
10. **Docs** (README run local docker-compose, `/api/docs`, catalogue d’erreurs).

---

## 21) Annexes — exemples de validations

* `phone` : format E.164 `+225...`
* `email` : RFC 5322
* `amount` : `>= 0`, currency `XOF`
* `seats` : `1..seats_available`
* `stars` : `1..5`
* `lat/lon` : bornes WGS84
* **Anti-fraude** : limite 3 tentatives OTP / 10 min, 5 bookings non payés / 24h, 3 CB échouées / 24h.

---

## 22) Roadmap technique (MVP → V2)

**MVP (8–12 semaines)**

* Auth (OTP/email), profils, KYC basique
* Trajets CRUD + recherche (PostGIS)
* Réservations, statuts jusqu’à **paid**
* **Wave** paiement + webhook
* Chat temps réel, notifications push
* Admin minimal (users, KYC, trips, bookings, payments read-only)
* Observabilité de base

**V2**

* OM, MTN, cartes ; payouts auto + réconciliations
* Annulations avancées + refunds automatiques
* Promos, parrainage, CRM
* Rapports finance/usage + exports
* Compliance & audit avancés

---

### ✅ Remarques finales

* **Tous les IDs sont des UUIDs**: configurez SQLAlchemy + Alembic pour générer des UUID serveur (Postgres `gen_random_uuid()`).
* Activez **PostGIS** et créez les **indexes GIST** pour les colonnes géographiques.
* Respectez l’**idempotence** sur les endpoints critiques (paiements, réservations) via `Idempotency-Key`.


## Déploiement
- Créer DB + Redis + S3 (ou MinIO).
- Exporter les variables (.env).
- `flask db upgrade`
- `gunicorn -k eventlet -w 1 -b 0.0.0.0:8000 app:app`

### Secrets requis en prod (exemples)

WAVE_API_KEY=...
WAVE_WEBHOOK_SECRET=...
OM_API_KEY=...
OM_SECRET=...
MTN_API_KEY=...
MTN_SECRET=...
STRIPE_SECRET_KEY=...
FCM_SERVER_KEY=...
SMTP_HOST=...
SMTP_USER=...
SMTP_PASS=...
#   a l l o c a r - b a c k e n d
# allocar-backend-flask
