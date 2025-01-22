<script setup>

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  is_massive_edit: Boolean,
  is_edit: Boolean,
})

const capital_types = [
  {"name": "Público", "value": "public"},
  {"name": "Privado", "value": "private"},
  {"name": "Mixto", "value": "mixed"},
  {"name": "Conflicto", "value": "conflict"},
]

</script>

<template>
  <v-col cols="12" class="pa-0 d-flex">
    <v-checkbox
      v-model="full_main.is_collective"
      label="Es colectivo"
      class="mr-4"
      color="primary"
      hide-details
    />
<!--    workspaces-->
    <v-checkbox
      v-model="full_main.has_belongs"
      label="Tiene grupos de pertenencia"
      class="mr-2"
      color="primary"
      hide-details
    />
    <v-select
      v-model="full_main.capital_type"
      :items="capital_types"
      item-title="name"
      item-value="value"
      label="Tipo de capital"
      class="ml-2"
      variant="outlined"
      style="max-width: 240px;"
    />
  </v-col>
</template>

<style scoped>

</style>