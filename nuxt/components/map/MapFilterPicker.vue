<script setup>
import { computed } from 'vue'
import { useDisplay } from 'vuetify'
import { VMenu, VBottomSheet } from 'vuetify/components'
import { useMapStore } from '~/store/map.js'

// Picker genérico de un filtro (decisions §4): botón-ícono en el rail +
// popover transitorio. El popover es un v-menu anclado en escritorio y un
// bottom-sheet en móvil; el cuerpo (checkboxes / autocomplete / toggle) es
// el mismo en ambos, así que usamos <component :is> para no duplicarlo.
const props = defineProps({
  // Definición declarativa del filtro (ver FILTER_DEFS en MapFilterRail).
  //   { key, label, icon, pickerType, indented, dependsOn, purposeToggle }
  def: { type: Object, required: true },
  // Catálogo de opciones { id, name, short_name?, icon?, color? }.
  options: { type: Array, default: () => [] },
  // v-model: ids seleccionados (vive en mapStore.filters[def.key]).
  modelValue: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

const { smAndDown } = useDisplay()
const mapStore = useMapStore()

const localModel = computed({
  get: () => props.modelValue,
  set: v => emit('update:modelValue', v),
})

// Toggle despojo/defensa (solo el filtro legal lo usa).
const purposeModel = computed({
  get: () => mapStore.filters.legalPurpose,
  set: v => { mapStore.filters.legalPurpose = v },
})

// Un solo picker abierto a la vez: el estado vive en el store, así una
// cápsula también puede reabrir este picker poniendo activePickerKey.
const isOpen = computed({
  get: () => mapStore.activePickerKey === props.def.key,
  set: v => { mapStore.activePickerKey = v ? props.def.key : null },
})

// Megaproyecto se habilita solo con ≥1 extractivismo activo (decisions §6).
const disabled = computed(() => {
  if (!props.def.dependsOn) return false
  return (mapStore.filters[props.def.dependsOn] || []).length === 0
})

// Badge ● cuando el filtro aporta algo (selección o, en legal, un purpose).
const hasSelection = computed(() =>
  (props.modelValue?.length || 0) > 0 ||
  (props.def.purposeToggle && mapStore.filters.legalPurpose.length > 0))

const titleOf = o => o.short_name || o.name
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
      <div :class="['rail-btn', { indented: def.indented }]">
        <v-badge
          :model-value="hasSelection"
          dot
          color="primary"
          offset-x="6"
          offset-y="6"
        >
          <v-btn
            :icon="def.icon"
            :disabled="disabled"
            :color="isOpen ? 'primary' : undefined"
            variant="text"
            density="comfortable"
            v-bind="actProps"
          />
        </v-badge>
        <v-tooltip activator="parent" :text="def.label" location="end"/>
      </div>
    </template>

    <v-card min-width="260" max-width="360" class="pa-2">
      <div class="text-subtitle-2 font-weight-medium px-2 pt-1 pb-2">
        {{ def.label }}
      </div>

      <!-- Mecanismos legales: subtoggle despojo / defensa (decisions §7). -->
      <v-btn-toggle
        v-if="def.purposeToggle"
        v-model="purposeModel"
        multiple
        divided
        density="compact"
        variant="outlined"
        class="mb-2 mx-2"
      >
        <v-btn
          v-for="p in mapStore.purposeOptions"
          :key="p.id"
          :value="p.id"
          size="small"
        >
          {{ p.short_name || p.name }}
        </v-btn>
      </v-btn-toggle>

      <div
        v-if="!options.length"
        class="text-caption text-medium-emphasis px-2 py-3"
      >
        Sin opciones disponibles.
      </div>

      <!-- Lista larga → autocomplete múltiple. -->
      <v-autocomplete
        v-else-if="def.pickerType === 'autocomplete'"
        v-model="localModel"
        :items="options"
        :item-title="titleOf"
        item-value="id"
        :label="def.label"
        multiple
        chips
        closable-chips
        density="compact"
        variant="outlined"
        hide-details
        class="mx-2 mb-1"
      ></v-autocomplete>

      <!-- Lista corta → checkboxes. -->
      <v-list
        v-else
        v-model:selected="localModel"
        select-strategy="leaf"
        density="compact"
        max-height="320"
        class="py-0"
      >
        <v-list-item
          v-for="opt in options"
          :key="opt.id"
          :value="opt.id"
          :title="titleOf(opt)"
        >
          <template #prepend="{ isSelected }">
            <v-checkbox-btn :model-value="isSelected" density="compact"/>
          </template>
        </v-list-item>
      </v-list>
    </v-card>
  </component>
</template>

<style scoped>
/* El botón se indenta cuando el filtro cuelga de otro (megaproyecto bajo
   extractivismo, decisions §6) para insinuar la relación padre-hijo. */
.rail-btn.indented {
  margin-left: 14px;
}
</style>
