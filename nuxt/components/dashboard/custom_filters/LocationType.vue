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

const width = computed(() => {
  return props.is_filter
      ? '150px'
      : is_point.value ? '56px' : '130px'
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
      >{{ item.title }}</span>
<!--          {{ item.title }}-->
    </template>
  </v-select>
</template>

<style scoped>

</style>