# TESTING

Mapa de niveles del monorepo. El detalle vive de cada lado; aquí solo está qué hay montado y dónde buscarlo.

| Nivel | `api/` (Django) | `nuxt/` (front) |
|---|---|---|
| Unitario | **Sí** — `source` (adjuntos) y `space_time` (visibilidad del mapa, pendientes, geolocalización), runner nativo; comandos y gotchas en [api/TESTING.md](api/TESTING.md) | **Sí** — Vitest (`cd nuxt && pnpm test`), composables, casi todos puros: `composables/__tests__/useClosePosition.test.js` (centro de respaldo del mapa del editor) y `useGeolocate.test.js` (14: el trazo no toca los selectores, sólo previsualiza los municipios atravesados y avisa cuando lo capturado queda fuera; el pin sí sobrescribe y avisa; el aviso de localidad se decide con la lista completa aunque solo se pinten seis candidatas; el reemplazo automático sobrescribe, borra lo no resuelto y se deshace, y ni siquiera se ofrece cuando el motor no resolvió nada; el constructor del comentario persistido sigue la convención de `Comments.vue`) y `useStatusGroup.test.js` (13: la escalera de permisos de status como función pura —filtro, `readonly` del schema, superusuario y staff contra el candado, legacy asignable solo por superusuario, `open_selectable`—, la normalización de los dos vocabularios `location`/`status_location` y el objeto enriquecido, y el cableado del composable contra el store). Config en `nuxt/vitest.config.js` |
| Integración | No montado | No montado |
| E2E | No montado (Playwright cubriría los dos lados) | Suite no montada; la verificación del dashboard es **episódica en navegador con Playwright MCP** —flujos nuevos y releases, nunca por commit—, con las credenciales locales de abajo |
| Diagnósticos manuales | **Sí** — ver [api/TESTING.md](api/TESTING.md) | No |

Los diagnósticos del lado de la API no son tests: verifican contra el mundo real (proxy, PressReader, Gemini, la base) y varios **cuestan dinero o cuota**. Léase [api/TESTING.md](api/TESTING.md) antes de correr cualquiera; ahí están los comandos, las credenciales que hacen falta (todas en `api/.env`) y cuáles son gratis.

Para verificar a mano el dashboard en el navegador hacen falta credenciales locales: están en `docs/keys/local-dashboard-credentials.md` (submódulo privado), nunca en este repo.

Cuando se monte una suite de verdad, esta tabla se actualiza aquí y el detalle de comandos se queda en el TESTING.md del lado que corresponda.
