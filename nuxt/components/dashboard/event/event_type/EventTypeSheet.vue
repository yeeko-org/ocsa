<script setup>

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
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

const event_collection_data = computed(() => {
  return schemas.value.collections_dict['event']
})
const actor_collection_data = computed(() => {
  return schemas.value.collections_dict['actor']
})
const participant_collection_data = computed(() => {
  return schemas.value.collections_dict['participant']
})

const event_init_filters = computed(() => {
  return {
    event_type: props.full_main.id,
  }
})

const event_direct_filters = computed(() => {
  return {
    event_type: props.full_main.id,
  }
})

const event_indirect_filters = computed(() => {
  return {
    indirect_event_type: props.full_main.id,
  }
})

</script>

<template>

  <v-card class="mb-4">
    <v-card-text>
      <CollectionDisplay
        :parent_collection="event_collection_data"
        :init_filters="event_init_filters"
        :init_total_count="full_main.events_count"
        direct_sheet
      >
        <template #title>
          Eventos
          ({{ full_main.events_count }})
        </template>
      </CollectionDisplay>
    </v-card-text>
  </v-card>
  <v-card class="mb-4">
    <v-card-text>
      <CollectionDisplay
        :parent_collection="participant_collection_data"
        :init_filters="event_direct_filters"
        direct_sheet
      >
        <template #title>
          Participaciones
        </template>
      </CollectionDisplay>
    </v-card-text>
  </v-card>
  <v-card class="mb-4">
    <v-card-text>
      <CollectionDisplay
        :parent_collection="actor_collection_data"
        :init_filters="event_direct_filters"
        direct_sheet
      >
          <template #title>
            Actores con participación directa
          </template>
      </CollectionDisplay>
    </v-card-text>
  </v-card>
  <v-card class="mb-4">
    <v-card-text>
      <CollectionDisplay
        :parent_collection="actor_collection_data"
        :init_filters="event_indirect_filters"
        direct_sheet
      >
          <template #title>
            Actores con participación directa e indirecta
          </template>
      </CollectionDisplay>
    </v-card-text>
  </v-card>
</template>

<style scoped>

</style>