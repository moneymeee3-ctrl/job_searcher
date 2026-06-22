# API Reference

Base URL: `http://localhost:8000` (local). All application endpoints are versioned
under `/api/v1`. Interactive docs are served at `/docs` (Swagger) and `/redoc`.

Authentication uses JWT bearer tokens. Obtain a token from `/auth/login` or
`/auth/register`, then send it on protected routes:

```
Authorization: Bearer <access_token>
```

When an access token expires, call `/auth/refresh` with the refresh token to get a
new pair. The mobile client does this automatically on a `401`.

## Service / operational

| Method | Path             | Auth | Description                  |
| ------ | ---------------- | ---- | ---------------------------- |
| GET    | `/health`        | no   | Liveness probe               |
| GET    | `/health/ready`  | no   | Readiness probe (DB check)   |
| GET    | `/metrics`       | no   | Prometheus metrics           |

## Authentication — `/api/v1/auth`

| Method | Path               | Auth | Description                       |
| ------ | ------------------ | ---- | --------------------------------- |
| POST   | `/register`        | no   | Register a new user (201)         |
| POST   | `/login`           | no   | Login with email + password       |
| POST   | `/refresh`         | no   | Exchange refresh for new tokens   |
| POST   | `/verify-email`    | no   | Verify email with token           |
| POST   | `/forgot-password` | no   | Request a password-reset token    |
| POST   | `/reset-password`  | no   | Reset password with token         |
| GET    | `/me`              | yes  | Current user profile              |

**Register / login response**

```json
{
  "access_token": "…",
  "refresh_token": "…",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "…", "email": "…", "username": "…",
    "first_name": "…", "last_name": "…", "full_name": "…",
    "role": "candidate", "is_verified": false, "is_premium": false
  },
  "message": "…"
}
```

## Resumes — `/api/v1/resumes`

| Method | Path                  | Auth | Description                          |
| ------ | --------------------- | ---- | ------------------------------------ |
| POST   | `/upload`             | yes  | Upload + parse + profile a resume    |
| GET    | `/`                   | yes  | List all resumes                     |
| GET    | `/{resume_id}`        | yes  | Resume metadata                      |
| GET    | `/{resume_id}/profile`| yes  | Extracted AI profile                 |
| PUT    | `/{resume_id}/primary`| yes  | Set as primary resume (204)          |
| DELETE | `/{resume_id}`        | yes  | Delete a resume (204)                |

## Candidate profile — `/api/v1/profile`

| Method | Path | Auth | Description                                    |
| ------ | ---- | ---- | ---------------------------------------------- |
| GET    | `/`  | yes  | Full candidate profile from primary resume     |

## Recommendations — `/api/v1/recommendations`

| Method | Path                  | Auth | Description                                  |
| ------ | --------------------- | ---- | -------------------------------------------- |
| GET    | `/jobs`               | yes  | AI-ranked jobs (`min_score`, `salary_min_lpa`)|
| GET    | `/jobs/{job_id}/gaps` | yes  | Full skill-gap analysis for a job            |
| POST   | `/approve`            | yes  | Approve a job for auto-apply (201)           |

**Ranked job shape** (items in `jobs[]`)

```json
{
  "rank": 1, "job_id": "…", "title": "…", "company": "…",
  "company_tier": "tier1", "location": "…", "source_portal": "greenhouse",
  "apply_url": "…", "salary_min_lpa": 30, "salary_max_lpa": 45, "meets_salary": true,
  "match_score": 88, "match_tier": "auto_apply", "is_auto_apply": true,
  "matched_skills": ["c", "rtos"], "missing_skills": ["can"],
  "explanation": "…", "recommendation": "…", "category_breakdown": [ … ]
}
```

## Autonomous agent — `/api/v1/agent`

| Method | Path          | Auth | Description                                      |
| ------ | ------------- | ---- | ------------------------------------------------ |
| GET    | `/advise`     | yes  | Scan, reason, plan, coach (`min_score`, `salary_min_lpa`) |
| POST   | `/auto-apply` | yes  | Queue apply-now matches (201)                    |

## Dashboard — `/api/v1/dashboard`

| Method | Path | Auth | Description                                          |
| ------ | ---- | ---- | --------------------------------------------------- |
| GET    | `/`  | yes  | Metrics, recommendation summary, recent applications |

## Applications — `/api/v1/applications`

| Method | Path | Auth | Description           |
| ------ | ---- | ---- | --------------------- |
| GET    | `/`  | yes  | List all applications |

## Learning roadmap — `/api/v1/roadmap`

| Method | Path             | Auth | Description                         |
| ------ | ---------------- | ---- | ----------------------------------- |
| GET    | `/`              | yes  | Roadmap from top matched jobs       |
| GET    | `/job/{job_id}`  | yes  | Roadmap for a specific job          |

## Interview prep — `/api/v1/interview`

| Method | Path             | Auth | Description                         |
| ------ | ---------------- | ---- | ----------------------------------- |
| GET    | `/prep`          | yes  | General interview preparation kit   |
| GET    | `/prep/{job_id}` | yes  | Interview kit for a specific job    |

## Company intelligence — `/api/v1/company`

| Method | Path            | Auth | Description                          |
| ------ | --------------- | ---- | ------------------------------------ |
| GET    | `/intelligence` | yes  | Monitored companies and portals      |
| GET    | `/fit`          | yes  | Company fit analysis                 |

## Job search — `/api/v1/search`

| Method | Path     | Auth | Description             |
| ------ | -------- | ---- | ----------------------- |
| GET    | `/jobs`  | yes  | Search and filter jobs  |

## Notifications — `/api/v1/notifications`

| Method | Path | Auth | Description            |
| ------ | ---- | ---- | --------------------- |
| GET    | `/`  | yes  | User notifications    |

## Error shape

Errors are returned with the appropriate HTTP status and a JSON body:

```json
{ "error": "Human-readable message", "detail": "optional context" }
```

`401` means unauthenticated (missing/invalid token); `403` means authenticated but
not permitted.
