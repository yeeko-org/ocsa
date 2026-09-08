<script setup>
import { computed } from 'vue'
import { useDisplay } from 'vuetify'
import { VMenu, VBottomSheet } from 'vuetify/components'
import { useMainStore } from '~/store/index.js'
import { useMapStore } from '~/store/map.js'
import MultiSelectMap from '~/components/map/filters/MultiSelectMap.vue'
import HelpTooltip from '~/components/map/common/HelpTooltip.vue'
import {
  RAIL_TONE, tileLabelWidth,
} from '~/components/map/filters/filterRegistry.js'

// Picker de un rail-group (decisions §4, Capa D): botón-ícono persistente
// (Capa A) + popover transitorio (v-menu en escritorio / v-bottom-sheet en
// móvil). El cuerpo compone un MultiSelectMap por cada `select` del grupo
// (megaproyecto = extractivismo + megaproyecto; afectaciones = tipo +
// subtipo condicional) más, en legal, el toggle de propósito.
const props = defineProps({
  group: { type: String, required: true },  // id del rail-group
})

const { smAndDown } = useDisplay()

// `location`/`offset` son del v-menu: pasados al v-bottom-sheet lo
// reposicionan al borde superior de la pantalla.
const overlayProps = computed(() =>
  smAndDown.value ? {} : { location: 'end', offset: 8 })
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
    v-bind="overlayProps"
  >
    <template #activator="{ props: actProps }">
      <!-- Teléfono: tile ícono + etiqueta (dos líneas), todo el tile es el
           blanco táctil. -->
      <v-btn
        v-if="smAndDown"
        class="rail-tile text-none"
        variant="text"
        :color="RAIL_TONE"
        :active="isOpen || hasSelection"
        v-bind="actProps"
      >
        <v-badge
          :model-value="hasSelection"
          :content="count"
          :color="RAIL_TONE"
          location="top end"
          offset-x="-6"
          offset-y="4"
          class="rail-tile__badge"
        >
          <v-icon :icon="rg.icon" size="28"/>
        </v-badge>
        <span
          class="rail-tile__label"
          :style="{ width: tileLabelWidth(rg.label) }"
        >
          {{ rg.label }}
        </span>
      </v-btn>
      <div v-else class="d-flex align-center">
        <v-badge
          :model-value="hasSelection"
          :content="count"
          :color="RAIL_TONE"
          location="bottom end"
          offset-x="2"
          offset-y="2"
        >
          <v-btn
            :icon="rg.icon"
            :color="RAIL_TONE"
            :variant="hasSelection ? 'tonal' : 'text'"
            :active="isOpen"
            size="large"
            v-bind="actProps"
          />
        </v-badge>
        <v-tooltip
          v-if="!smAndDown"
          activator="parent"
          :text="rg.label"
          location="end"
        />
      </div>
    </template>

    <v-card min-width="340" max-width="460" class="pa-2">
      <div class="text-title-medium font-weight-bold px-2 pt-1 pb-2 d-flex
        align-center">
        <v-icon :color="rg.color" :icon="rg.icon" class="mr-2"/>
        {{ rg.label }}
        <HelpTooltip
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
            <HelpTooltip
              :title="labelFor(sel)"
              :description="helpFor(sel)"
              :color="rg.color"
            />
          </div>
          <MultiSelectMap
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
/* Tile del rail en teléfono: ícono arriba, etiqueta a dos líneas debajo,
   relleno igual arriba y abajo; ancho según contenido (mín. 64 px). Ícono y
   etiqueta heredan el color del botón (RAIL_TONE). */
.rail-tile {
  flex-direction: column;
  height: auto;
  width: auto;
  min-width: 64px;
  padding: 6px 8px;
  gap: 4px;
}

/* Badge chico, abajo-derecha del ícono, dentro de la caja del tile. */
.rail-tile__badge :deep(.v-badge__badge) {
  font-size: 0.625rem;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
}

.rail-tile :deep(.v-btn__content) {
  flex-direction: column;
  gap: 4px;
  white-space: normal;
}

.rail-tile__label {
  font-size: 0.625rem;
  line-height: 1.15;
  font-weight: 500;
  text-align: center;
  min-width: min-content;
  max-width: 76px;
}
</style>
