<script setup>
const props = defineProps({
  full_main: Object,
  is_filter: Boolean,
})

const location_types = [
  { id: 'point', name: 'Punto', icon: 'location_on' },
  { id: 'line', name: 'Línea', icon: 'timeline' },
  { id: 'polygon', name: 'Polígono', icon: 'map' },
]

const width = computed(() => {
  return props.is_filter ? '150px' : '56px'
})

</script>

<template>
  <v-select
    v-model="full_main.type_location"
    :items="location_types"
    item-title="name"
    item-value="id"
    :variant="is_filter ? 'underlined' : 'solo-filled'"
    :label="is_filter ? 'Tipo de ubicación' : ''"
    :bg-color="is_filter ? '' : 'grey-lighten-2'"
    :menu-icon="is_filter ? 'arrow_drop_down' : null"
    class="ml-2"
    :density="is_filter ? 'compact' : 'default'"
    :hide-details="is_filter"
    _style="max-width: 56px;"
    :max-width="width"
  >
    <template #prepend-item>
      <div class="px-2 py-2 text-grey">
        Tipo de ubicación:
      </div>
    </template>
    <template #item="{ item, props: {onClick, title, value} }">
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

    <template #selection="{ item }">
      <v-icon
        v-if="item.raw.icon"
        color="primary"
        size="24"
        :icon="item.raw.icon || 'trip_origin'"
        class="mr-2"
      ></v-icon>
      <span
        v-if="is_filter"
      >{{ item.title }}</span>
<!--          {{ item.title }}-->
    </template>
  </v-select>
</template>

<style scoped>

</style>