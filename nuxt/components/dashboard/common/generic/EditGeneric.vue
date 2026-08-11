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

</script>

<template>
  <v-col
    cols="12"
    class="d-flex pa-0"
   :order="col_order"
  >
    <span>
      Acá estarán los campos de edición
    </span>
  </v-col>
</template>

<style scoped>

</style>