<script setup>
import StatusChip from '~/components/dashboard/status/StatusChip.vue'
import HeaderChip from '~/components/dashboard/common/HeaderChip.vue'
import ActorsChip from "~/components/dashboard/actor/ActorsChip.vue";
import ImpactChip from "~/components/dashboard/common/ImpactChip.vue";

import { computed, defineProps } from 'vue'
import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'
import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";

const mainStore = useMainStore()
const { cats } = storeToRefs(mainStore)

const props = defineProps({
  project: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['open-project'])

const locations_count = computed(() => {
  return props.project.locations.length
})
const mention_counts = computed(() => {
  return props.project.mentions.length
})
const states_tooltip = computed(() => {
  let all_states = props.project.locations.map(loc => loc.state)
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
  <v-expansion-panel-title
    color="purple-lighten-5"
    _class="pl-2 pr-3"
    class="pl-0 py-0"
    @click="emit('open-project')"
    height="60"
    style="min-height: 60px;"
  >
<!--    <v-toolbar-->
<!--      color="purple-lighten-5"-->
<!--    >-->
    <ExtractivismIcons
      :project="project"
    />
      <v-toolbar-title
        class="text-subtitle-1 mr-6"
        style="max-width: 300px;"
      >
        <div
          class="ml-2"
          style="text-wrap: pretty; width: 300px; max-height: 54px; overflow: hidden;"
          v-tooltip:bottom="project.official_name"
        >{{ project.official_name }}</div>
      </v-toolbar-title>
      <template v-if="show_details">
        <StatusChip
          v-if="project.status_register"
          :main="project"
          collection="validation"
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
          :mentions="project.mentions"
        />
        <ActorsChip
          :main="project"
        />

      </template>
      <v-btn
        v-else
        color="blue"
        variant="plain"
      >
        cargando detalles...
      </v-btn>

<!--      <v-spacer></v-spacer>-->
<!--      <v-icon-->
<!--        color="purple"-->
<!--        class="mr-2"-->
<!--      >-->
<!--        expand_more-->
<!--      </v-icon>-->
<!--    </v-toolbar>-->
  </v-expansion-panel-title>

</template>

<style scoped>

</style>