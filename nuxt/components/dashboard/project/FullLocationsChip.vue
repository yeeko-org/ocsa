<script setup>

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import DescriptionIcon from "~/components/dashboard/common/utils/DescriptionIcon.vue";

const mainStore = useMainStore()
const { cats } = storeToRefs(mainStore)

const props = defineProps({
  locations: {
    type: Array,
    required: true,
  },
  horizontal: Boolean,
})

const has_municipality = computed(() => {
  return props.locations.some(loc => loc.municipality_full !== undefined)
})

const saved_locations = computed(() => {
  return props.locations.reduce((acc, loc) => {
    if (loc.path) return acc
    loc.state_full = cats.value.state.find(st => st.id === Number(loc.state))
    loc.display_state = has_municipality.value
      ? loc.state_full?.code_name
      : loc.state_full?.name
    return [...acc, loc]
  }, [])
})

const locations_count = computed(() => {
  return props.locations.length
})

</script>

<template>
  <v-card
    v-if="saved_locations.length > 0"
    variant="tonal"
    color="indigo"
    class="text-body-2 px-2 d-flex align-center py-1"
  >
    <v-icon
      size="20"
      color="indigo"
      class="mr-2"

    >
      location_on
    </v-icon>
    <div>
      <div
        v-for="location in saved_locations"
        :key="location.id"
        class="d-flex align-center ga-1"
      >
        <b>{{location.display_state}}</b>
        <span v-if="location.municipality_full">
          - {{location.municipality_full.name}}
        </span>
        <span v-if="location.locality_full">
          ({{location.locality_full.name}})
        </span>
        <DescriptionIcon
          :description="location.details"
          size="x-small"
          icon_size="large"
        />
      </div>

      <span
        v-if="locations_count === 0"
        class="text-warning"
      >
        <v-icon color="warning" size="20" class="mr-2">
          location_off
        </v-icon>
        Sin ubicaciones
      </span>
    </div>
  </v-card>

</template>

<style scoped>

</style>
