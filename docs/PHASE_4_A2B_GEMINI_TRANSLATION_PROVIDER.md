# Phase 4-A2b: Gemini Translation Provider

## Scope

- Add `gemini` to the existing translation-provider layer.
- Keep `mock`, official OpenAI Responses API, and OpenAI-compatible Chat Completions unchanged.
- Reuse the Phase 4-A2 scientific translation prompt and educational context.
- Call Gemini through the REST `models.generateContent` endpoint using `httpx`.
- Send `store=false` and preserve the local deterministic fallback for missing credentials, timeouts, HTTP errors, blocked/empty responses, and oversized input.
- Keep API keys on the backend only.

## Runtime configuration

Create `backend/.env` locally or add the values as deployment secrets:

```env
MADARIK_AI_PROVIDER=gemini
GEMINI_API_KEY=replace-with-your-real-key
GEMINI_MODEL=gemini-3.1-flash-lite
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
MADARIK_AI_EXTERNAL_ENABLED=true
MADARIK_AI_TIMEOUT_SECONDS=45
MADARIK_AI_MAX_INPUT_CHARS=4000
MADARIK_AI_MAX_OUTPUT_TOKENS=1200
MADARIK_AI_TEMPERATURE=0.1
```

`GEMINI_MODEL` is optional. If it is empty, Madarik uses `gemini-3.1-flash-lite`.

For backward compatibility, Gemini can also use `MADARIK_AI_API_KEY` and
`MADARIK_AI_MODEL` when the dedicated Gemini variables are empty.

## Security

- Never commit `backend/.env`.
- Never expose the key through the provider-status endpoint or the frontend.
- The request uses the `x-goog-api-key` header.
- The request body sets `store=false`.
- Translation still requires teacher review before export.

## Verification

```bash
cd backend
pytest -q

cd ../frontend
npm run lint
npm run build

cd ..
git diff --check
git status -sb
```

A live test should be run only after local tests pass and should use an
environment secret rather than a committed key.
