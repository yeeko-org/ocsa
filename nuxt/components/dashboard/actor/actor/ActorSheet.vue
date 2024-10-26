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
  <span>
    Acá habrá otras listas interesantes
  </span>
</template>

<style scoped>

</style>