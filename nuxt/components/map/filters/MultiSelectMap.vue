<script setup>
import { computed, ref, onMounted } from 'vue'
import { VSelect, VAutocomplete } from 'vuetify/components'
import { useMapStore } from '~/store/map.js'

// Select múltiple base de los filtros del mapa. Recibe el id del rail-group y
// la clave de estado (uno de sus `selects`); resuelve sus ítems vía
// `mapStore.optionsFor`, que ya traen ícono/color/nombre/descripción. Render
// según `picker`: checkbox (lista corta) / select / autocomplete (largas).
// v-model = ids[]. Cada ítem: checkbox a la izquierda + ícono/color, título en
// 1 línea (completo en tooltip) y descripción recortada a 3 líneas.
const props = defineProps({
  group: { type: String, required: true },        // id del rail-group
  stateKey: { type: String, required: true },     // clave del select
  picker: { type: String, default: 'checkbox' },  // checkbox|select|autocomplete
  label: { type: String, default: '' },
  // Estados: al montar (al abrir el picker) abre el menú y enfoca el input.
  autofocus: { type: Boolean, default: false },
})
const model = defineModel({ type: Array, default: () => [] })

const mapStore = useMapStore()

// Solo categorías seleccionables (las no-seleccionables son encabezados).
const items = computed(() =>
  mapStore.optionsFor(props.group, props.stateKey)
    .filter(o => o.is_selectable !== false))

const selectComponent = computed(() =>
  props.picker === 'autocomplete' ? VAutocomplete : VSelect)

const titleOf = o => o.short_name || o.name
const isSelected = id => model.value.includes(id)

// Control del menú para el autofocus (estados).
const menuModel = ref(false)
onMounted(() => {
  if (props.autofocus && props.picker !== 'checkbox') menuModel.value = true
})
</script>

<template>
  <!-- Lista larga → select / autocomplete múltiple. -->
  <component
    :is="selectComponent"
    v-if="picker !== 'checkbox'"
    v-model="model"
    v-model:menu="menuModel"
    :items="items"
    :item-title="titleOf"
    item-value="id"
    :label="label"
    :autofocus="autofocus"
    multiple
    chips
    closable-chips
    clearable
    clear-icon="clear"
    density="compact"
    variant="outlined"
    hide-details
    class="mb-2"
  >
    <template #item="{ props: itemProps, internalItem: item }">
      <v-list-item
        v-bind="itemProps"
        :title="null"
        class="ms-item"
        max-width="400"
      >
        <template #prepend>
          <v-checkbox-btn
            :model-value="isSelected(item.raw.id)"
            density="compact"
            class="ms-check"
          />
          <v-icon
            v-if="item.raw.icon"
            :color="item.raw.color || 'grey-darken-2'"
            :icon="item.raw.icon"
            class="mr-2"
          />
        </template>
        <v-list-item-title class="ms-title">
          {{ titleOf(item.raw) }}
        </v-list-item-title>
        <v-list-item-subtitle v-if="item.raw.description" class="ms-desc">
          {{ item.raw.description }}
        </v-list-item-subtitle>
        <v-tooltip activator="parent" location="right" :max-width="400">
          <div class="font-weight-bold">{{ item.raw.name }}</div>
          <div v-if="item.raw.description">{{ item.raw.description }}</div>
        </v-tooltip>
      </v-list-item>
    </template>
  </component>

  <!-- Lista corta → checkboxes. -->
  <v-list
    v-else
    v-model:selected="model"
    select-strategy="leaf"
    density="compact"
    max-height="320"
    class="py-0"
  >
    <v-list-item
      v-for="opt in items"
      :key="opt.id"
      :value="opt.id"
      :title="null"
      class="ms-item"
    >
      <template #prepend="{ isSelected: sel }">
        <v-checkbox-btn
          :model-value="sel"
          density="compact"
          class="ms-check"
        />
        <v-icon
          v-if="opt.icon"
          :color="opt.color || 'grey-darken-2'"
          :icon="opt.icon"
          class="mr-2"
        />
      </template>
      <v-list-item-title class="ms-title">{{ titleOf(opt) }}</v-list-item-title>
      <v-list-item-subtitle v-if="opt.description" class="ms-desc">
        {{ opt.description }}
      </v-list-item-subtitle>
      <v-tooltip activator="parent" location="right" :max-width="400">
        <div class="font-weight-bold">{{ opt.name }}</div>
        <div v-if="opt.description">{{ opt.description }}</div>
      </v-tooltip>
    </v-list-item>
  </v-list>
</template>

<style scoped>
/* Checkbox pegado a la izquierda sin empujar el texto: recortamos el padding
   inicial del list-item y el gap del prepend. */
.ms-item :deep(.v-list-item__spacer) {
  width: 8px;
}
.ms-item {
  padding-inline-start: 8px !important;
}
.ms-check {
  margin-inline-end: 0;
}

/* Título: una sola línea con elipsis (el nombre completo va en el tooltip). */
.ms-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Descripción: máximo 3 líneas. */
.ms-desc {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  white-space: normal;
}
</style>
