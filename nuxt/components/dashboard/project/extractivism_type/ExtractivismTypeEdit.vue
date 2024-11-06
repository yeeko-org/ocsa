<script setup>
const props = defineProps({
  is_massive_edit: Boolean,
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
    label="Nombre del grupo"
    variant="outlined"
    style="max-width: 400px;"
  />
  <v-text-field
    v-model="full_main.icon"
    label="Ícono (material icons)"
    variant="outlined"
    class="ml-2"
    style="max-width: 200px;"
  />
  <v-text-field
    v-model="full_main.color"
    label="Color"
    variant="outlined"
    class="ml-2"
    style="max-width: 200px;"
  />
</template>

<style scoped>

</style>