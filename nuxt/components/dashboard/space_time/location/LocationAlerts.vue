<script setup>

import {storeToRefs} from 'pinia'
import LocationPersistAlert from
    '~/components/dashboard/space_time/location/LocationPersistAlert.vue'
import {buildAlertComment} from '~/composables/useGeolocate.js'
import {patchElement} from '~/composables/save_elements.js'
import {useAuthStore} from '~/store/auth.js'
import {useDashboardStore} from '~/store/dash.js'
import {useMainStore} from '~/store/index.js'

const props = defineProps({
  import_warnings: {
    type: Array,
    default: () => [],
  },
  // Ayudas del tipo de ubicación; sólo llegan con el mapa abierto
  helps: {
    type: Array,
    default: null,
  },
  geo_notices: {
    type: Array,
    default: () => [],
  },
  // Lo capturado que no cuadra con el trazo: mismo trato que los avisos,
  // pero en amarillo, porque pide una corrección y no sólo informa.
  geo_warnings: {
    type: Array,
    default: () => [],
  },
  // Las localidades cercanas que el motor no eligió, en un solo renglón
  candidates_text: {
    type: String,
    default: '',
  },
  // El modelo de la ubicación; sin él no hay dónde persistir los avisos
  location: {
    type: Object,
    default: null,
  },
})

const {schemas, status_dict} = storeToRefs(useMainStore())
const authStore = useAuthStore()
const {user_details_ocsa} = authStore
const {is_staff} = storeToRefs(authStore)
const {showSnackbar} = useDashboardStore()

// El botón guarda el aviso como comentario, o sea escribe la ubicación: el
// candado del status lo cierra igual que a los demás campos.
const can_persist = computed(() => {
  if (!props.location) return false
  if (is_staff.value) return true
  const status_name = props.location.status_location
  if (!status_name) return true
  return status_dict.value.location?.[status_name]?.open_editor !== false
})

// Cerrar un aviso no puede tocar el arreglo del padre, que es su dueño
const dismissed = ref([])
const persisted = ref([])

watch(() => [props.geo_notices, props.geo_warnings],
    () => dismissed.value = [])

// Cambiar de ubicación estrena comentarios: lo ya persistido era del otro
watch(() => props.location, () => persisted.value = [])

const visible_notices = computed(
    () => props.geo_notices.filter(msg => !dismissed.value.includes(msg)))

const visible_warnings = computed(
    () => props.geo_warnings.filter(msg => !dismissed.value.includes(msg)))

const import_error = defineModel('import_error', {type: String, default: ''})
const overwrote_saved = defineModel(
    'overwrote_saved', {type: Boolean, default: false})

async function persist(text) {
  const loc = props.location
  if (!loc || persisted.value.includes(text)) return
  persisted.value.push(text)
  const before = loc.comments
  loc.comments = buildAlertComment(
      before, text, user_details_ocsa?.first_name || '')
  // Sin id el comentario viaja en el POST de alta; con id se guarda ya, para
  // que el aviso quede registrado aunque la edición se abandone.
  if (!loc.id) return
  const res = await patchElement(
      schemas.value.collections_dict.location, loc.id, {comments: loc.comments})
  if (res?.errors) {
    // También el texto local: sin deshacerlo, reintentar lo agregaría dos veces
    loc.comments = before
    persisted.value = persisted.value.filter(msg => msg !== text)
    showSnackbar('No se pudo guardar el comentario', 'error')
  }
}

</script>

<template>
  <v-alert
    v-if="import_error"
    type="error"
    variant="tonal"
    class="mb-2"
    density="compact"
    closable
    @click:close="import_error = ''"
  >
    {{ import_error }}
  </v-alert>
  <v-alert
    v-if="overwrote_saved"
    type="warning"
    variant="tonal"
    class="mb-2"
    density="compact"
    closable
    @click:close="overwrote_saved = false"
  >
    El archivo que importaste reemplazó lo que estaba marcado en el mapa;
    si guardas, se pierde lo anterior.
  </v-alert>
  <v-alert
    v-for="msg in import_warnings"
    :key="msg"
    type="info"
    variant="tonal"
    class="mb-2"
    density="compact"
  >
    {{ msg }}
    <template #append>
      <LocationPersistAlert
        v-if="can_persist"
        :done="persisted.includes(msg)"
        @persist="persist(msg)"
      />
    </template>
  </v-alert>
  <v-alert
    v-if="candidates_text"
    type="info"
    variant="tonal"
    class="mb-2"
    density="compact"
  >
    {{ candidates_text }}
    <template #append>
      <LocationPersistAlert
        v-if="can_persist"
        :done="persisted.includes(candidates_text)"
        @persist="persist(candidates_text)"
      />
    </template>
  </v-alert>
  <v-alert
    v-for="msg in visible_notices"
    :key="msg"
    type="info"
    variant="tonal"
    class="mb-2"
    density="compact"
    closable
    @click:close="dismissed.push(msg)"
  >
    {{ msg }}
    <template #append>
      <LocationPersistAlert
        v-if="can_persist"
        :done="persisted.includes(msg)"
        @persist="persist(msg)"
      />
    </template>
  </v-alert>
  <v-alert
    v-for="msg in visible_warnings"
    :key="msg"
    type="warning"
    variant="tonal"
    class="mb-2"
    density="compact"
    closable
    @click:close="dismissed.push(msg)"
  >
    {{ msg }}
    <template #append>
      <LocationPersistAlert
        v-if="can_persist"
        :done="persisted.includes(msg)"
        @persist="persist(msg)"
      />
    </template>
  </v-alert>
  <v-alert
    v-if="helps"
    type="info"
    variant="tonal"
    class="mt-3"
    density="compact"
  >
    <div
      v-for="msg in helps"
      :key="msg"
    >
      {{ msg }}
    </div>
  </v-alert>
</template>
