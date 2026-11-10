<script setup>
import PanelList from "~/components/dashboard/common/main/PanelList.vue";
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
const mainStore = useMainStore()
const { schemas, collections_summary } = storeToRefs(mainStore)

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  show_details: {
    type: Boolean,
    default: false,
  },
})

// Toda ubicación cuelga de un proyecto (adr-0033).
const dest_collection = computed(() => {
  if (!props.full_main.project) return null
  let coll = collections_summary.value.project
  if (!coll) return null
  coll.results = [props.full_main.project_full]
  coll.collection_data = schemas.value.collections_dict.project
  return coll
})

</script>

<template>
  <v-card class="mb-4 pa-3" v-if="dest_collection">
    {{ dest_collection.collection_data.name }} contenedor de la ubicación:
    <PanelList
      :results="dest_collection.results"
      :collection_data="dest_collection.collection_data"
      :show_details="show_details"
    />
  </v-card>
</template>

<style scoped>

</style>