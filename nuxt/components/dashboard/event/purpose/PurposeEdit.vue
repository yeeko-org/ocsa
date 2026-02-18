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
      v-model="full_main.short_name"
      label="Nombre corto"
      variant="outlined"
      readonly
      style="max-width: 340px;"
    />
  </v-col>
</template>

<style scoped>

</style>