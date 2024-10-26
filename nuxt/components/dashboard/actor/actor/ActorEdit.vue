<script setup>
const props = defineProps({
  is_edit: Boolean,
  full_main: {
    type: Object,
    required: true,
  },
})

</script>

<template>
  <v-text-field
    v-model="full_main.name"
    label="Nombre del actor"
    variant="outlined"
    class="mb-2"
  />
  <v-text-field
    v-model="full_main.official_name"
    label="Nombre oficial del actor"
    variant="outlined"
    class="mb-2"
  />
</template>

<style scoped>

</style>