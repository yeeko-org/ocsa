<script setup>

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  show_details: {
    type: Boolean,
    default: false,
  },
})

</script>

<template>
  <v-expansion-panel-text
    class="ml-n16 mr-n6"
    color="grey-lighten-5"
  >
    <v-sheet
      v-if="full_main"
      color="grey-lighten-5"
      class="mt-n2 mb-n4 pa-3"
    >
      Contenido Genérico 2
    </v-sheet>
  </v-expansion-panel-text>
</template>

<style scoped>

</style>