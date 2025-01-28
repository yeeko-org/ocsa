<script setup>

import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";
import {computed} from "vue";
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";

const mainStore = useMainStore()
const { cats } = storeToRefs(mainStore)

const props = defineProps({
  project: {
    type: Object,
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

const locations_count = computed(() => {
  return props.project.locations.length
})
</script>

<template>
  <HeaderChip
    :count="locations_count"
    icon="location_on"
    label="ubicación"
    label_plural="ubicaciones"
    color="indigo"
    :tooltip_complement="states_tooltip"
    class="mx-1"
    :horizontal="horizontal"
  />
</template>

<style scoped>

</style>