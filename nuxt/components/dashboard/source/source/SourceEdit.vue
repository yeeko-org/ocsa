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
    <v-switch
      v-model="full_main.is_news"
      label="Es una fuente de noticias"
      append-icon="newsmode"
      hide-details
      color="primary"
      class="mr-6"
    ></v-switch>
    <v-text-field
      v-model="full_main.main_url"
      label="URL principal"
      class="mr-2"
      variant="outlined"
      style="width: 300px;"
    ></v-text-field>


  </v-col>
</template>

<style scoped>

</style>