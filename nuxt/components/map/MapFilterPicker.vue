<script setup>
import { computed } from 'vue'
import { useDisplay } from 'vuetify'
import { VMenu, VBottomSheet } from 'vuetify/components'
import { useMainStore } from '~/store/index.js'
import { useMapStore } from '~/store/map.js'
import MapMultiSelect from '~/components/map/MapMultiSelect.vue'
import MapHelpTooltip from '~/components/map/MapHelpTooltip.vue'

// Picker de un rail-group (decisions §4, Capa D): botón-ícono persistente
// (Capa A) + popover transitorio (v-menu en escritorio / v-bottom-sheet en
// móvil). El cuerpo compone un MapMultiSelect por cada `select` del grupo
// (megaproyecto = extractivismo + megaproyecto; afectaciones = tipo +
// subtipo condicional) más, en legal, el toggle de propósito.
const props = defineProps({
  group: { type: String, required: true },  // id del rail-group
})

const { smAndDown } = useDisplay()
const mainStore = useMainStore()
const mapStore = useMapStore()

// Grupo resuelto (label/icon/color heredados + selects/purposeKey).
const rg = computed(() => mapStore.resolveGroup(props.group) || {})
const count = computed(() => mapStore.countFor(props.group))
const hasSelection = computed(() => count.value > 0)

// Un solo picker abierto a la vez: el estado vive en el store, así una fila
// de la Capa B/C también puede reabrirlo poniendo activePickerKey.
const isOpen = computed({
  get: () => mapStore.activePickerKey === props.group,
  set: v => { mapStore.activePickerKey = v ? props.group : null },
})

// Selects visibles: los condicionales (subtipo de afectación) solo si hay
// opciones (algún tipo seleccionado tiene hijos).
const visibleSelects = computed(() =>
  (rg.value.selects || []).filter(sel =>
    !sel.conditional ||
    mapStore.optionsFor(props.group, sel.stateKey).length > 0))

// Colección (schema) de un select según su nivel (type/subtype).
const collectionOf = sel => {
  const snake = sel.level === 'type'
    ? rg.value.category_type : rg.value.category_subtype
  return mainStore.schemas?.collections_dict?.[snake] || null
}
// Etiqueta de cada select = nombre de su colección.
const labelFor = sel => collectionOf(sel)?.name || rg.value.label
// Descripción de ayuda por select (solo se muestra si hay >1 select).
const helpFor = sel => collectionOf(sel)?.description || ''
const hasMultiSelects = computed(() => visibleSelects.value.length > 1)

// Toggle despojo/defensa (solo el grupo legal lo usa).
const purposeModel = computed({
  get: () => mapStore.filters.legalPurpose,
  set: v => { mapStore.filters.legalPurpose = v },
})
</script>

<template>
  <component
    :is="smAndDown ? VBottomSheet : VMenu"
    v-model="isOpen"
    :close-on-content-click="false"
    location="end"
    :offset="8"
  >
    <template #activator="{ props: actProps }">
      <div class="d-flex align-center">
        <v-badge
          :model-value="hasSelection"
          :content="count"
          :color="rg.color"
          location="bottom end"
          offset-x="2"
          offset-y="2"
        >
          <v-btn
            :icon="rg.icon"
            :color="rg.color"
            :variant="hasSelection ? 'tonal' : 'text'"
            :active="isOpen"
            size="large"
            v-bind="actProps"
          />
        </v-badge>
        <v-tooltip activator="parent" :text="rg.label" location="end"/>
      </div>
    </template>

    <v-card min-width="340" max-width="460" class="pa-2">
      <div class="text-title-medium font-weight-bold px-2 pt-1 pb-2 d-flex
        align-center">
        <v-icon :color="rg.color" :icon="rg.icon" class="mr-2"/>
        {{ rg.label }}
        <MapHelpTooltip
          :title="rg.label"
          :description="rg.description"
          :color="rg.color"
        />
      </div>

      <!-- Mecanismos legales: propósito despojo / defensa (decisions §7). -->
      <div v-if="rg.purposeKey" class="d-flex align-center mb-3 mx-2">
        <span class="text-body-medium mr-3 flex-shrink-0">Propósito del Mecanismo:</span>
        <v-btn-toggle
          v-model="purposeModel"
          multiple
          divided
          density="compact"
          variant="outlined"
        >
          <v-btn
            v-for="p in mapStore.purposeOptions"
            :key="p.id"
            :value="p.id"
            :color="p.color"
            :prepend-icon="p.icon"
            size="small"
          >
            {{ p.name }}
          </v-btn>
        </v-btn-toggle>
      </div>

      <div class="px-2">
        <div v-for="sel in visibleSelects" :key="sel.stateKey">
          <!-- Con >1 select, cada uno lleva su título + ayuda. -->
          <div v-if="hasMultiSelects" class="d-flex align-center mt-1">
            <span class="text-title-small font-weight-medium">
              {{ labelFor(sel) }}
            </span>
            <MapHelpTooltip
              :title="labelFor(sel)"
              :description="helpFor(sel)"
              :color="rg.color"
            />
          </div>
          <MapMultiSelect
            :group="group"
            :state-key="sel.stateKey"
            :picker="sel.picker"
            :label="hasMultiSelects ? '' : labelFor(sel)"
            :autofocus="group === 'states'"
            v-model="mapStore.filters[sel.stateKey]"
          />
        </div>
      </div>

      <div class="d-flex justify-end px-2 pt-1">
        <v-btn 
          variant="text"
          size="small"
          color="primary"
          @click="isOpen = false"
        >
          Aplicar
        </v-btn>
      </div>
    </v-card>
  </component>
</template>

<style scoped>
</style>
