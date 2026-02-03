<script setup>

import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";
import {computed} from "vue";
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import DescriptionIcon from "~/components/dashboard/utils/DescriptionIcon.vue";

const mainStore = useMainStore()
const { cats } = storeToRefs(mainStore)

const props = defineProps({
  locations: {
    type: Array,
    required: true,
  },
  horizontal: Boolean,
})

const states_tooltip = computed(() => {
  let all_states = props.project.locations.map(loc => loc.state)
  let states = [...new Set(all_states)]
  const full_states = states.reduce((coll, state) => {
    const curr_state = cats.value.state.find(st => st.id === Number(state))
    if (curr_state)
      coll.push(curr_state)
    return coll
  }, [])
  const names = full_states.map(state => state.name)
  const text_names = names.join(", ")
  return `${all_states.length} estados: ${text_names}`
})

const all_locations = computed(() => {
  return props.locations.map(loc => {
    loc.state_full = cats.value.state.find(st => st.id === Number(loc.state))
    return loc
  })
})

const locations_count = computed(() => {
  return props.locations.length
})
</script>

<template>
  <v-card
    variant="tonal"
    color="indigo"
    class="text-body-2 px-2 d-flex align-center"
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
        v-for="location in all_locations"
        :key="location.id"
        class="d-flex align-center ga-1"
      >
        <b>{{location.state_full.code_name}}</b>
        <span v-if="location.municipality_full">
          - {{location.municipality_full.name}}
        </span>
        <span v-if="location.locality_full">
          ({{location.locality_full.name}})
        </span>
        <DescriptionIcon
          :description="location.details"
        />
      </div>
    </div>
    <v-tooltip
      activator="parent"
      location="top"
    >
      <div class="font-weight-bold">
        Hola tooltip

      </div>
    </v-tooltip>
  </v-card>

<!--  <HeaderChip-->
<!--    :count="locations_count"-->
<!--    icon="location_on"-->
<!--    label="ubicación"-->
<!--    label_plural="ubicaciones"-->
<!--    color="indigo"-->
<!--    :tooltip_complement="states_tooltip"-->
<!--    class="mx-1"-->
<!--    :horizontal="horizontal"-->
<!--  />-->
</template>

<style scoped>

</style>
