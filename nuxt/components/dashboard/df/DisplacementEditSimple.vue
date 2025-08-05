<script setup>

import ImpactToolbar from "~/components/dashboard/impact/impact/ImpactToolbar.vue";
import DisplacementToolbar from "~/components/dashboard/df/DisplacementToolbar.vue";

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
})

const artificial_parent = computed(() => {
  return {"displacements": [props.full_main]}
})

</script>

<template>
  <v-card class="mb-4 pa-0">
    Hola
    <DisplacementToolbar
      :full_main="artificial_parent"
      main_collection_name="event"
      second_level
    />
  </v-card>
</template>

<style scoped>

</style>