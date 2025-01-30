<script setup>
import PanelList from "~/components/dashboard/common/PanelList.vue";
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

const dest_collection = computed(() => {
  const available_collections = ['event', 'project', 'impact']
  const current_collection = available_collections.find(
    collection => props.full_main[collection]
  )
  if (!current_collection)
    return null
  let coll = collections_summary.value[current_collection]
  coll.results = [props.full_main[`${current_collection}_full`]]
  coll.collection_data = schemas.value.collections_dict[current_collection]
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