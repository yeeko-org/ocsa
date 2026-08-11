# TESTING

Mapa de niveles del monorepo. El detalle vive de cada lado; aquí solo está qué hay montado y dónde buscarlo.

| Nivel | `api/` (Django) | `nuxt/` (front) |
|---|---|---|
| Unitario | No montado (el default sería pytest + pytest-django) | No montado (el default sería Vitest) |
| Integración | No montado | No montado |
| E2E | No montado (Playwright cubriría los dos lados) | No montado |
| Diagnósticos manuales | **Sí** — ver [api/TESTING.md](api/TESTING.md) | No |

Los diagnósticos del lado de la API no son tests: verifican contra el mundo real (proxy, PressReader, Gemini, la base) y varios **cuestan dinero o cuota**. Léase [api/TESTING.md](api/TESTING.md) antes de correr cualquiera; ahí están los comandos, las credenciales que hacen falta (todas en `api/.env`) y cuáles son gratis.

Cuando se monte una suite de verdad, esta tabla se actualiza aquí y el detalle de comandos se queda en el TESTING.md del lado que corresponda.
