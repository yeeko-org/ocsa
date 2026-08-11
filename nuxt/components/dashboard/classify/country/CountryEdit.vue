<script setup >

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
  <v-col cols="12" class="d-flex pa-0" :order="col_order">
    <v-text-field
      v-model="full_main.flag_emoji"
      label="Emoji del país"
      variant="outlined"
      class="mb-2 mr-3"
      style="max-width: 250px;"
    />
  </v-col>
</template>

<style scoped>

</style>