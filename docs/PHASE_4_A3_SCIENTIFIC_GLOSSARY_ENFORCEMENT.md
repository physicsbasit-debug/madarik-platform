# Phase 4-A3: Scientific Glossary Enforcement

## Status

Implementation package for branch:

`feat/phase-4-a3-scientific-glossary-enforcement`

Baseline:

`aa12170179ecacfd21ac43785dec369959f1815b`

## Purpose

Phase 4-A3 turns the reviewed project glossary from prompt context into an enforced translation contract.

Only glossary terms with status `approved` are mandatory. Terms still marked `needs_review` are excluded from both enforcement and the deterministic local glossary override.

## Translation flow

1. Detect approved English glossary terms that occur in the current source question or question part.
2. Include applicable entries in a dedicated `MANDATORY SOURCE TERMS` prompt section.
3. Generate the first translation through the configured provider.
4. Validate that every applicable term uses its approved Arabic equivalent.
5. If a term is missing, send one correction request to the same provider.
6. Validate the corrected response.
7. If the violation remains, return the deterministic local fallback and record the failure in review notes.

The correction cycle is intentionally limited to one attempt.

## Matching rules

- English source matching is case-insensitive and uses whole-term boundaries.
- Multiword English terms allow flexible whitespace.
- Arabic compliance checking tolerates harmless differences such as diacritics, tatweel, Alef variants, and whitespace.
- Duplicate approved English entries are resolved deterministically by the last matching glossary item.
- Empty terms and unapproved terms are ignored.

## Review notes

Each translated question receives a provider note describing one of these outcomes:

- all applicable approved terms passed validation;
- no approved glossary term matched the source;
- one glossary violation was corrected automatically;
- a persistent violation caused local fallback.

Teacher review remains mandatory before export.

## Files changed

- `backend/app/services/ai_provider.py`
- `backend/app/services/translation.py`
- `backend/tests/test_ai_provider_layer.py`
- `backend/tests/test_translation_engine.py`
- `frontend/src/features/review/ReviewStep.tsx`
- `docs/PHASE_4_A3_SCIENTIFIC_GLOSSARY_ENFORCEMENT.md`

## Verification performed while building the package

- Python compilation passed for the modified backend service files.
- Existing and new provider-layer tests passed in an isolated harness: `23 passed`.
- The new deterministic fallback glossary-status test passed.
- Gemini correction flow was exercised with mocked first and second responses.
- The patch was checked against the supplied Phase 4-A2b baseline source.

Full repository acceptance still requires:

```bash
cd backend
python -m pytest -q

cd ../frontend
nvm use 22
npm run lint
npm run build

cd ..
git diff --check
```

Expected backend total after adding seven tests: `173 passed`.
