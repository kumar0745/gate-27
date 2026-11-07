# Stage 2 — UI/UX expansion and public website

## Delivered

- [x] Public homepage at `/` with product positioning, navigation and calls to action.
- [x] Responsive hero section with a CSS/SVG-style workspace preview (no stock-image dependency).
- [x] How-it-works journey explaining the student preparation flow.
- [x] Feature overview for syllabus, mind maps, PYQs, mock tests, AI support and study planning.
- [x] Live paper explorer populated from `GET /api/papers`.
- [x] Search across paper codes and paper names.
- [x] Paper cards route to `/app?paper=<CODE>`.
- [x] Student workspace available at `/app`; `/workspace` is an alias.
- [x] Workspace reads a valid `paper` query parameter and updates the local profile before rendering.
- [x] Responsive mobile navigation and reduced-motion support.
- [x] SEO metadata, semantic page landmarks, skip link, keyboard paper-search shortcut and accessible labels.
- [x] FAQ and clear independent-project / non-affiliation disclaimer.
- [x] Route and static-asset tests added.

## Validation

Run from the repository root:

```bash
python -m compileall -q backend/app
node --check frontend/app.js
node --check frontend/landing.js
python -m unittest discover -s backend/tests -v
```

Manual browser checks:

1. Open `/` and confirm the public landing page renders.
2. Search for `CS`, `DA`, `EC`, `ME` and a full paper name in the paper explorer.
3. Select a paper and confirm navigation to `/app` with the selected paper loaded in the workspace.
4. Check menu open/close behavior at mobile widths.
5. Confirm the existing student task and profile workflows still work from `/app`.

## Boundaries

- This stage builds the public marketing and paper-selection experience. It does not implement registration/authentication; that is Stage 3.
- The landing page describes the roadmap honestly. It does not imply that future mind-map, PYQ, mock-test or AI modules are already complete.
- Paper catalogue entries come from the shared JSON catalogue, which should be reconciled with official GATE 2027 sources during the content-verification stage.
