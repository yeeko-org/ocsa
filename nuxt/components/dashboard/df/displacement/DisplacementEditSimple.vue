<script setup>

import DisplacementToolbar from "~/components/dashboard/df/DisplacementToolbar.vue";

const full_main = defineModel({type: Object, required: true})
const artificial_displacements = computed(() => {
  return [full_main.value]
})
const main_collection_name = computed(() => {
  return full_main.value.event ? 'event' : 'impact'
})

</script>

<template>
  <v-card class="mb-4 pa-0">
    <DisplacementToolbar
      v-model="artificial_displacements"
      direct_displacement
      :main_collection_name="main_collection_name"
      second_level
    />
  </v-card>
</template>

<style scoped>

</style>