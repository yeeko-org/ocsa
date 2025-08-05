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
    v-model="full_main.ai_name"
    label="Nombre clasificado en la IA"
    variant="outlined"
    style="max-width: 400px;"
  ></v-text-field>
</template>

<style scoped>

</style>