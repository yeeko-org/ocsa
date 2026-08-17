<script setup>
import { LOCATION_TYPES } from "~/composables/location_types.js";
const props = defineProps({
  full_main: Object,
  is_filter: Boolean,
})

const location_type = computed(() => LOCATION_TYPES.find(
  loc => loc.id === props.full_main.type_location)
)

const is_point = computed(() => location_type.value?.id === 'point')

// Número de partes de la geometría: una línea o un polígono pueden guardarse
// como Multi* con varias figuras, y el editor no muestra cuántas hay.
const parts_count = computed(() => {
  if (props.is_filter) return 0
  const geojson = props.full_main.geojson
  if (!geojson) return 0
  if (geojson.type === 'FeatureCollection')
    return geojson.features.length
  const geometry = geojson.type === 'Feature' ? geojson.geometry : geojson
  if (!geometry?.type) return 0
  return geometry.type.startsWith('Multi') ? geometry.coordinates.length : 1
})

const show_parts_count = computed(() => parts_count.value > 1)

const parts_label = computed(
    () => `${parts_count.value} ${location_type.value?.name_plural || ''}`)

const width = computed(() => {
  if (props.is_filter) return '150px'
  if (is_point.value) return '56px'
  return show_parts_count.value ? '160px' : '130px'
})

</script>

<template>
  <v-select
    v-model="full_main.type_location"
    :items="LOCATION_TYPES"
    item-title="name"
    item-value="id"
    :variant="is_filter ? 'underlined' : 'solo-filled'"
    :label="is_filter ? 'Tipo de ubicación' : ''"
    :bg-color="is_filter ? '' : 'grey-lighten-2'"
    :menu-icon="is_filter ? 'arrow_drop_down' : null"
    class="ml-2"
    :density="is_filter ? 'compact' : 'default'"
    hide-details
    :max-width="width"
  >
    <template #prepend-item>
      <div class="px-2 py-2 text-grey">
        Tipo de ubicación:
      </div>
    </template>
    <template #item="{ internalItem: item, props: {onClick, title, value} }">
      <v-list-item
        @click="onClick"
        :title="title"
        :value="value"
      >
        <template v-slot:prepend v-if="item.raw.icon">
          <v-icon
            color="primary"
            :icon="item.raw.icon || 'trip_origin'"
          ></v-icon>
        </template>
      </v-list-item>
    </template>

    <template #selection="{ internalItem: item }">
      <v-icon
        v-if="item.raw.icon"
        color="primary"
        size="24"
        :icon="item.raw.icon || 'trip_origin'"
        class="mr-2"
      ></v-icon>
      <span
        v-if="is_filter || !is_point"
        class="font-weight-bold"
      >{{ show_parts_count ? parts_label : item.title }}</span>
<!--          {{ item.title }}-->
    </template>
  </v-select>
</template>

<style scoped>

</style>