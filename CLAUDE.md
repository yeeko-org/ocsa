# OCSA — monorepo

Observatorio de Conflictos Socioambientales (Universidad Iberoamericana): data on socio-environmental conflicts, mega-projects, actors, impacts and events in Mexico from 2017 to present, built from newspaper articles (La Jornada, Reforma, Proceso).

Event types: violence against activists · collective actions · legal resources (against/in favor of projects). Impact types: social · environmental.

## Structure

| Path | What it is |
|---|---|
| `api/` | Django + DRF over PostgreSQL — see [api/CLAUDE.md](api/CLAUDE.md) |
| `nuxt/` | Nuxt + Vuetify front (editorial dashboard and public map) — see [nuxt/CLAUDE.md](nuxt/CLAUDE.md) |
| `docs/` | Submodule of the **private** repo `yeeko-org/ocsa-docs`: the documenter graph (ADRs, open tasks, records) plus the `deploy` skill |
| `.claude/skills/` | Skills for the whole monorepo, both sides |

`docs/` needs access to the private repo. Without it the directory stays empty and `.claude/skills/deploy` is a dangling symlink — that is expected. With access: `git submodule update --init`.

## Commits

Prefix `[api]` or `[nuxt]` when the commit touches one side only; no prefix when it is cross-cutting (root files, submodule, skills). Subject in Spanish.

## Testing

No test suite on either side; what exists are re-runnable diagnostics that hit real services and cost money. See [TESTING.md](TESTING.md) before running any.
