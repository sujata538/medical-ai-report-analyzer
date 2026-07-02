# Contributing to MedInsight

Thanks for your interest in contributing!

## Getting started

1. Fork and clone the repository.
2. Run `./scripts/setup.sh` to install backend + frontend dependencies.
3. Copy `.env.example` to `.env`.
4. Run the backend and frontend locally (see README "Quick start").

## Workflow

1. Create a branch: `git checkout -b feature/short-description`
2. Make your changes, following the conventions in
   [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md).
3. Add or update tests for any behavior change.
4. Run the full test suite: `cd backend && pytest`
5. Run the frontend build/lint: `cd frontend && npm run lint && npm run build`
6. Commit with a clear message (see below) and open a pull request using
   the provided PR template.

## Commit message style

Prefer short, imperative subject lines, optionally scoped:

```
feat(extraction): recover parameters via semantic matching
fix(auth): reject expired refresh tokens correctly
docs: clarify reference range seeding behavior
test(health-score): cover critical-flag boundary cases
```

## Code style

- **Backend**: PEP 8, type hints on all function signatures, docstrings on
  every module/class. No business logic in API routers — see
  `docs/DEVELOPMENT.md`.
- **Frontend**: functional components + hooks, Tailwind utility classes
  using the design tokens in `tailwind.config.js`, no inline hex colors.

## Reporting bugs / requesting features

Please use the issue templates under `.github/ISSUE_TEMPLATE/`.

## Medical content changes

Any change touching recommendation wording, reference ranges, or health
scoring logic should be flagged clearly in the PR description — these are
safety-sensitive and should stay conservative, cautious, and
non-diagnostic by design.
