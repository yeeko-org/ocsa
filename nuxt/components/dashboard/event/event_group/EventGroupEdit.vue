<script setup>

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  is_massive_edit: Boolean,
  is_edit: Boolean,
})
</script>

<template>
  <v-text-field
    v-model="full_main.model_origin"
    label="Modelo origen"
    variant="outlined"
    readonly
    style="max-width: 340px;"
  />
</template>

<style scoped>

</style>