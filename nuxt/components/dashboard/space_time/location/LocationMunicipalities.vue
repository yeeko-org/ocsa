<script setup>

import {useGeoNewStore} from "~/store/geo.js";
import {storeToRefs} from "pinia";

const props = defineProps({
  municipalities_full: {
    type: Array,
    default: () => [],
  },
  type_location: {
    type: String,
    default: null,
  },
})

const {states} = storeToRefs(useGeoNewStore())

const dialog = ref(false)

// Un punto con un solo municipio ya lo muestra el selector de LocationMex
const show = computed(() => props.municipalities_full.length > 0
    && (props.municipalities_full.length > 1
        || props.type_location !== 'point'))

function stateOf(state_id) {
  return states.value.find(item => item.id === state_id) || null
}

// La clave del estado sólo desambigua cuando hay más de uno en la lista
const multi_state = computed(() => new Set(
    props.municipalities_full.map(mun => mun.state)).size > 1)

function stateCode(state_id) {
  const state = stateOf(state_id)
  return state?.code_name || state?.short_name || state?.name || null
}

function chipLabel(mun) {
  if (!multi_state.value) return mun.name
  const code = stateCode(mun.state)
  return code ? `${mun.name} (${code})` : mun.name
}

// Agrupados en el orden en que llegan los municipios: la lista del servidor
// ya viene ordenada y reordenar aquí la volvería otra lista.
const by_state = computed(() => {
  const groups = []
  const index = {}
  for (const mun of props.municipalities_full) {
    if (!(mun.state in index)) {
      const state = stateOf(mun.state)
      index[mun.state] = groups.length
      groups.push({
        id: mun.state,
        title: state?.short_name || state?.name || 'Sin estado',
        municipalities: [],
      })
    }
    groups[index[mun.state]].municipalities.push(mun)
  }
  return groups
})

const tooltip = computed(
    () => `Ver los ${props.municipalities_full.length} municipios`
        + ' agrupados por estado')

</script>

<template>
  <div
    v-if="show"
    class="municipalities-strip d-flex align-center flex-nowrap ga-1 mb-2"
    role="button"
    tabindex="0"
    v-tooltip:bottom="tooltip"
    @click="dialog = true"
    @keydown.enter.prevent="dialog = true"
    @keydown.space.prevent="dialog = true"
  >
    <span class="text-body-2 text-medium-emphasis flex-shrink-0 mr-1">
      Municipios que abarca:
    </span>
    <v-chip
      v-for="mun in municipalities_full"
      :key="mun.id"
      class="flex-shrink-0"
      size="small"
      variant="tonal"
    >
      {{ chipLabel(mun) }}
    </v-chip>
  </div>
  <v-dialog
    v-model="dialog"
    max-width="640"
    scrollable
  >
    <v-card title="Municipios que abarca la ubicación">
      <v-card-text>
        <div
          v-for="group in by_state"
          :key="group.id"
          class="mb-4"
        >
          <div class="text-subtitle-2 text-medium-emphasis mb-1">
            {{ group.title }}
          </div>
          <div class="d-flex flex-wrap ga-1">
            <v-chip
              v-for="mun in group.municipalities"
              :key="mun.id"
              size="small"
              variant="tonal"
            >
              {{ mun.name }}
            </v-chip>
          </div>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn
          text="Cerrar"
          @click="dialog = false"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
/* Alto de un renglón de chips: los que no caben se recortan, y la lista
   completa vive en el diálogo. */
.municipalities-strip {
  height: 32px;
  overflow: hidden;
  cursor: pointer;
}
</style>
