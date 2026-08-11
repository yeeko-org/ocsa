<script setup>

import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";

const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  show_details: {
    type: Boolean,
    default: false,
  },
  collection_data: Object,
})

const actor_collection_data = computed(() => {
  return schemas.value.collections_dict['actor']
})

const participant_type = computed(() => {
  const part_types = props.full_main.participant_types
  if (!part_types)
    return null
  if (part_types.length === 0)
    return null
  return part_types[0]
})

const init_filters = computed(() => {
  return {'participant_type': props.full_main.id}
})


</script>

<template>
  <v-card class="mb-4" v-if="true">
    <v-card-title>
      Actores
      <span>
        ({{ full_main.actors_count }})
      </span>
    </v-card-title>
    <v-card-text>
      <CollectionDisplay
        :parent_collection="actor_collection_data"
        :init_filters="init_filters"
        :init_total_count="full_main.actors_count"
        direct_sheet
      />
    </v-card-text>
  </v-card>
</template>

<style scoped>

</style>