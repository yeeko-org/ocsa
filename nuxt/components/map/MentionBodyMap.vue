<script setup>
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import dayjs from "dayjs";

import CollectionListMap from "~/components/map/CollectionListMap.vue";

const mainStore = useMainStore()
const { all_nodes } = storeToRefs(mainStore)

const props = defineProps({
  mention: {
    type: Object,
    required: true,
  },
})

const status_index = computed(() => {
  const tree = all_nodes.value?.status_projects
  if (!tree?.descendants) return {}
  const idx = {}
  tree.descendants().forEach(n => {
    if (n.data?.id) idx[n.data.id] = n.data
  })
  return idx
})

function statusName(id) {
  return status_index.value[id]?.name || 'Sin estatus'
}

function statusColor(id) {
  return status_index.value[id]?.color || 'purple'
}

function formatDate(date) {
  return date ? dayjs(date).format('DD/MM/YYYY') : 'Sin fecha'
}
</script>

<template>
  <div
    class="px-1 py-2"
  >
    <CollectionListMap
      v-if="mention.impacts?.length > 0"
      :objects="mention.impacts"
      node_name="impact_types"
      type_key="impact_type"
      :clickable="false"
    />
    <CollectionListMap
      v-if="mention.events?.length > 0"
      :objects="mention.events"
      node_name="event_types"
      type_key="event_type"
      :clickable="false"
    />

    <div
      v-if="mention.status_history?.length > 0"
      class="mt-2"
    >
      <div class="text-subtitle-2 text-grey-darken-1 mb-1 d-flex align-center">
        <v-icon size="small" class="mr-1">history_toggle_off</v-icon>
        Historial de estatus
      </div>
      <v-chip
        v-for="entry in mention.status_history"
        :key="entry.id"
        :color="statusColor(entry.status_project)"
        variant="tonal"
        size="small"
        class="mr-1 mb-1"
      >
        <span class="font-weight-medium">
          {{ statusName(entry.status_project) }}
        </span>
        <span class="ml-2 text-caption">
          {{ formatDate(entry.date) }}
        </span>
      </v-chip>
    </div>

    <!--
      TODO: Participantes/actores. Pendiente para otra sesión.
      Datos en mention.participants (cada uno con actor_full,
      participant_types, participant_group).
    -->
  </div>
</template>

<style scoped>

</style>