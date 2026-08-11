# OCSA

Observatorio de Conflictos Socioambientales de la Universidad Iberoamericana. Registra conflictos socioambientales en México desde 2017 —megaproyectos, actores, eventos, impactos y desplazamiento forzado— a partir de la lectura sistemática de la prensa nacional (La Jornada, Reforma y Proceso).

El repositorio reúne los dos componentes del sistema:

| Componente | Stack | Qué hace |
|---|---|---|
| `api/` | Django + Django REST Framework, PostgreSQL con `unaccent` | Modelo de datos, API, exportaciones a Excel y el pipeline de captura desde notas de prensa |
| `nuxt/` | Nuxt 3 + Vuetify 4, Pinia, Mapbox GL | Panel de captura y edición para el equipo, y el mapa público |

## Arranque rápido

### `api/`

```bash
cd api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env      # credenciales de PostgreSQL y llaves de servicios
python manage.py migrate
python manage.py runserver  # http://localhost:8000
```

Hace falta una base PostgreSQL con la extensión `unaccent` creada. La carga inicial de catálogos y de datos geográficos tiene un orden que importa; está en [api/README.md](api/README.md), junto con los datos del INEGI que se descargan aparte (`api/space_time/geo_files/README.md`).

### `nuxt/`

```bash
cd nuxt
npm install
npm run dev                 # https://localhost:3000
```

Necesita un `.env` con `NUXT_API_URL`, `NUXT_ADMIN_URL` y `NUXT_MAPBOX_TOKEN`. El servidor de desarrollo corre sobre HTTPS y espera `localhost.pem` y `localhost-key.pem` en la raíz de `nuxt/` (por ejemplo, generados con `mkcert`); esos certificados no se versionan.

## Documentación de proceso

Las decisiones (ADR), las tareas abiertas y las bitácoras viven en `docs/`, un submódulo del repositorio **privado** `yeeko-org/ocsa-docs`. Quien tenga acceso lo inicializa con `git submodule update --init`; sin él, el directorio queda vacío y el resto del repositorio funciona igual.

## Convención de commits

Prefijo `[api]` o `[nuxt]` cuando el commit toca un solo componente; sin prefijo cuando es transversal. Los mensajes van en español.
