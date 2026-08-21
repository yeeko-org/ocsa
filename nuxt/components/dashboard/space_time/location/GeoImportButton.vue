<script setup>

import {useMainStore} from "~/store/index.js";

// El botón vive dentro de la tarjeta del mapa, que se remonta al importar:
// el error y los avisos se emiten para que los pinte quien sobrevive.
const emit = defineEmits(['imported', 'import-error'])

const mainStore = useMainStore()
const { importLocationGeo } = mainStore

const geo_input = ref(null)
const importing = ref(false)
const import_tooltip = 'Importar archivo (GeoJSON, .zip de shapefile o KML)'

async function importGeoFile(event) {
  const file = event.target.files?.[0]
  if (!file) return
  emit('import-error', '')
  importing.value = true
  const form_data = new FormData()
  form_data.append('file', file, file.name)
  // Sin type_location el API infiere el tipo a partir del archivo: lo que
  // traiga el archivo manda sobre lo elegido en el formulario.
  const result = await importLocationGeo(form_data)
  importing.value = false
  // Sin esto, volver a elegir el mismo archivo no dispara el evento
  event.target.value = ''
  if (result?.error) {
    emit('import-error', result.error)
    return
  }
  emit('imported', {
    feature: importedFeature(result),
    type_location: result.type_location,
    warnings: result.warnings || [],
  })
}

// El API devuelve el punto como par de coordenadas y sin geojson, pero el
// camino de actualización del formulario espera siempre una Feature.
function importedFeature(result) {
  if (result.geojson) return result.geojson
  if (result.latitude === null || result.latitude === undefined) return null
  return {
    type: 'Feature',
    properties: {},
    geometry: {
      type: 'Point',
      coordinates: [result.longitude, result.latitude],
    },
  }
}

</script>

<template>
  <v-btn
    color="accent"
    :loading="importing"
    icon
    variant="text"
    @click="geo_input.click()"
    v-tooltip:bottom="import_tooltip"
  >
    <v-icon>
      upload_file
    </v-icon>
  </v-btn>
  <input
    ref="geo_input"
    type="file"
    accept=".geojson,.json,.zip,.kml"
    class="d-none"
    @change="importGeoFile"
  />
</template>
