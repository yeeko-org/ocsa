<script setup>

const props = defineProps({
  is_edit: Boolean,
  is_massive_edit: Boolean,
  full_main: {
    type: Object,
    required: true,
  },
})

</script>

<template>
  <span>
    Acá estarán los campos de edición
  </span>
</template>

<style scoped>

</style>