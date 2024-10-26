<script setup>
import StatusChip from '~/components/dashboard/status/StatusChip.vue'
import HeaderChip from '~/components/dashboard/common/HeaderChip.vue'
import ActorsChip from "~/components/dashboard/actor/ActorsChip.vue";
import ImpactChip from "~/components/dashboard/impact/ImpactChip.vue";

import { computed } from 'vue'
import { useMainStore } from '~/store/index.js'
import { storeToRefs } from 'pinia'
import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";

const mainStore = useMainStore()
const { cats, groups } = storeToRefs(mainStore)

const props = defineProps({
  main: Object,
  group: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})
const project = computed(() => {
  return props.main
})

const final_group = computed(() => {
  return props.group || groups.value.find(gr => gr.key === 'project')
})


// const emit = defineEmits(['open-panel'])

const locations_count = computed(() => {
  return project.value.locations.length
})
const mention_counts = computed(() => {
  return project.value.mentions.length
})
const states_tooltip = computed(() => {
  let all_states = project.value.locations.map(loc => loc.state)
  let states = [...new Set(all_states)]
  const full_states = states.reduce((coll, state) => {
    const curr_state = cats.value.states.find(st => st.id === Number(state))
    if (curr_state)
      coll.push(curr_state)
    return coll
  }, [])
  const names = full_states.map(state => state.name)
  const text_names = names.join(", ")
  return `${all_states.length} estados: ${text_names}`
})

</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :group="final_group"
    name_field="official_name"
  >
    <template #icon>
      <ExtractivismIcons
        :project="main"
      />
    </template>
    <template #details>
      <StatusChip
        v-if="project.status_register"
        :main="project"
        collection="register"
        field="status_register"
        left_label
        label="Registro:"
        class="mb-1"
        bold_text
      />
      <HeaderChip
        :count="mention_counts"
        icon="newspaper"
        label="nota"
        label_plural="notas"
        color="deep-purple"
        class="mx-1"
      />
      <HeaderChip
        :count="locations_count"
        icon="location_on"
        label="ubicación"
        label_plural="ubicaciones"
        color="primary"
        :tooltip_complement="states_tooltip"
        class="mx-1"
      />
      <ImpactChip
        :main_array="project.mentions"
        filter_group_name="impact_types"
        child_field="impacts"
      />
      <ActorsChip
        :main="project"
      />
    </template>
  </HeaderCommon>

</template>

<style scoped>

</style>