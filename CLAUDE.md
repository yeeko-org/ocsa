# OCSA — monorepo

Observatorio de Conflictos Socioambientales (Universidad Iberoamericana): data on socio-environmental conflicts, mega-projects, actors, impacts and events in Mexico from 2017 to present, built from newspaper articles (La Jornada, Reforma, Proceso).

Event types: violence against activists · collective actions · legal resources (against/in favor of projects). Impact types: social · environmental.

## Structure

| Path | What it is |
|---|---|
| `api/` | Django + DRF over PostgreSQL — see [api/CLAUDE.md](api/CLAUDE.md) |
| `nuxt/` | Nuxt + Vuetify front (editorial dashboard and public map) — see [nuxt/CLAUDE.md](nuxt/CLAUDE.md) |
| `docs/` | Submodule of the **private** repo `yeeko-org/ocsa-docs` — the monorepo's private half. Holds the documenter graph (ADRs, tasks, records) **and** a private vault that is not part of the graph: the `deploy` skill (`skills/`), the age key for `api/utils/data_private/*.age` (`keys/`), and the doc-path checker (`scripts/`). Vault lives here because it's the only private repo in a public monorepo (docs `adr-0020`) |
| `.claude/skills/` | Skills for the whole monorepo, both sides |

`docs/` needs access to the private repo. Without it the directory stays empty and `.claude/skills/deploy` is a dangling symlink — that is expected. With access: `git submodule update --init`.

## Commits

Prefix `[api]` or `[nuxt]` when the commit touches one side only; no prefix when it is cross-cutting (root files, submodule, skills). Subject in Spanish.

## Testing

No test suite on either side; what exists are re-runnable diagnostics that hit real services and cost money. See [TESTING.md](TESTING.md) before running any.
