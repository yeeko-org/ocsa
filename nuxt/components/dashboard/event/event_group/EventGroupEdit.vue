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
  <v-switch
    v-model="full_main.show_position"
    label="Desplegar Intención de Mecanismo"
    class="ml-4"
    color="accent"
    append-icon="double_arrow"
  />
</template>

<style scoped>

</style>