# Insumos geográficos del INEGI

Fuentes, capas, tolerancias de simplificación, gotchas de codificación y reglas de carga: **skill `ocs-geo`**, `.claude/skills/ocs-geo/references/cartografia.md` (desde la raíz del monorepo).

**Cuidado con `git add`:** `00ent.shp`, `00mun.shp`, `00l.shp` y `localidades.*` suman más de 270 MB y no se versionan. No los subas; se regeneran con el script.

## Descarga y carga

```bash
./download_inegi.sh          # --force [mgi|localidades|municipios] para rehacer
python manage.py load_states_data
python manage.py load_municipios
python manage.py load_localidades
python manage.py load_geometries
```
