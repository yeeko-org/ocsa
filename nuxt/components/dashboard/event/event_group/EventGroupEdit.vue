<script setup>

const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
  col_order: {
    type: Number,
    default: 5,
  }
})
const full_main = defineModel({type: Object, required: true})
const emits = defineEmits(['item-saved'])
</script>

<template>
  <v-col
    cols="12"
    class="d-flex pa-0"
   :order="col_order"
  >
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
  </v-col>
</template>

<style scoped>

</style>