<script setup>

import { ref } from 'vue'

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

const full_actor = ref(props.full_main)

</script>

<template>
  <v-expansion-panel-text
    class="ml-n16 mr-n6"
    color="blue-lighten-5"
  >
    <v-sheet
      v-if="full_actor"
      color="deep-purple-lighten-5"
      class="mt-n2 mb-n4 pa-3"
    >
      {{full_main}}
      {{ full_actor }}
    </v-sheet>
  </v-expansion-panel-text>
</template>

<style scoped>

</style>