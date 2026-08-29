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

// Con varios estados los municipios se muestran en un renglón por estado
const multi_state = computed(() => new Set(
    props.municipalities_full.map(mun => mun.state)).size > 1)

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

// Siempre en plural, aunque sea uno: es el rótulo de una cuenta
const summary = computed(() => {
  const total = `${props.municipalities_full.length} municipios abarcados:`
  if (!multi_state.value) return total
  return `${by_state.value.length} estados; ${total}`
})

const tooltip = computed(
    () => `Ver los ${props.municipalities_full.length} municipios`
        + ' agrupados por estado')

</script>

<template>
  <v-card
    v-if="show"
    class="cursor-pointer mb-6 pa-3"
    role="button"
    tabindex="0"
    variant="outlined"
    v-tooltip:bottom="tooltip"
    @click="dialog = true"
    @keydown.enter.prevent="dialog = true"
    @keydown.space.prevent="dialog = true"
  >
    <div class="d-flex align-center flex-wrap ga-1">
      <span class="text-body-2 mr-1">
        {{ summary }}
      </span>
      <template v-if="!multi_state">
        <v-chip
          v-for="mun in municipalities_full"
          :key="mun.id"
          size="small"
          color="blue"
          variant="tonal"
        >
          {{ mun.name }}
        </v-chip>
      </template>
    </div>
    <template v-if="multi_state">
      <div
        v-for="group in by_state"
        :key="group.id"
        class="d-flex align-center flex-wrap ga-1 mt-1"
      >
        <span class="text-body-2 mr-1">
          {{ group.title }}: {{ group.municipalities.length }}
        </span>
        <v-chip
          v-for="mun in group.municipalities"
          :key="mun.id"
          size="small"
          color="blue"
          variant="tonal"
        >
          {{ mun.name }}
        </v-chip>
      </div>
    </template>
    <v-dialog
      v-model="dialog"
      max-width="640"
      scrollable
    >
      <v-card title="Municipios abarcados por la línea o polígono">
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
                color="blue"
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
  </v-card>

</template>

