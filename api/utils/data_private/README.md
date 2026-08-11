# Volcados privados

Volcados con la codificación analítica del OCSA (2024): notas, notas filtradas y datos filtrados tal como quedaron tras la codificación. Se versionan aquí porque son insumo reproducible del análisis, pero no son públicos, así que van cifrados con [age](https://github.com/FiloSottile/age).

La llave privada no vive en este repositorio: está en el repositorio privado `ocsa-docs`, en `keys/ocsa-dumps.key`.

## Cómo descifrar

```bash
age -d -i <llave> archivo.age > archivo
```

Por ejemplo, con el repositorio privado clonado como hermano de este:

```bash
age -d -i ../ocsa-docs/keys/ocsa-dumps.key filtered_data.csv.age > filtered_data.csv
```

## Archivos

- `all_notes.json.age`
- `filtered_notes.csv.age`
- `filtered_data.csv.age`
