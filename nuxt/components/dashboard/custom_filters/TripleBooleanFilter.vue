<script setup>

const props = defineProps({
  final_filters: Object,
  field: String,
  label: String,
})

const single_items = [
  { title: "Sí", value: true },
  { title: "No", value: false },
  // { title: "Indefinido", value: null },
]

</script>

<template>
  <v-select
    v-model="final_filters[field]"
    :items="single_items"
    :label="label"
    clearable
    variant="underlined"
    density="compact"
    hide-details
    min-width="140"
    max-width="220"
  >
  </v-select>
</template>

<style scoped>

</style>