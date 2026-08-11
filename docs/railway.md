# ORX on Railway

ORX Core is prepared for Railway using a root `Dockerfile` and `railway.json`.

## Required Railway services

1. ORX API — deploy this GitHub repository.
2. PostgreSQL — add Railway PostgreSQL to the same project.
3. Redis — optional for the current MVP, reserved for future sessions/rate limiting.

## API service variables

Configure these variables on the ORX API service:

```text
DATABASE_URL=${{Postgres.DATABASE_URL}}
ADMIN_API_KEY=<LONG_RANDOM_SECRET>
ENVIRONMENT=production
TREASURY_EXTERNAL_ID=ORX_TREASURY
```

If a Railway Redis service is added:

```text
REDIS_URL=${{Redis.REDIS_URL}}
```

The application converts Railway's PostgreSQL URL automatically for SQLAlchemy asyncpg.

## Deployment lifecycle

Railway builds the root `Dockerfile`.

Before each deploy:

```text
alembic upgrade head
```

The service starts with:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Railway checks:

```text
GET /health
```

## First verification

After generating a Railway domain, verify:

```text
GET /
GET /health
GET /docs
GET /api/v1/orx
```

Protected ORX endpoints require:

```text
X-ORX-Admin-Key: <ADMIN_API_KEY>
```

Mutation endpoints also require an idempotency key when applicable:

```text
X-Idempotency-Key: <UNIQUE_REQUEST_KEY>
```

## Initial ORX flow

1. Create account with `POST /api/v1/accounts`.
2. The account automatically receives one ORX wallet.
3. Issue Genesis ORX with `POST /api/v1/treasury/issue`.
4. Transfer ORX using `POST /api/v1/transactions/transfer`.
5. Verify balances using `GET /api/v1/wallets/{wallet_id}/balance`.
6. Verify ledger transaction using `GET /api/v1/transactions/{transaction_id}`.

## Security note

The MVP intentionally protects account, wallet, transaction, and treasury APIs with the owner/admin key until ORLIX Identity authentication is implemented. Never place `ADMIN_API_KEY` in public frontend JavaScript.
