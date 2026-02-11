<script setup>

const props = defineProps({
  is_edit: Boolean,
  is_massive_edit: Boolean,
})
const full_main = defineModel({type: Object, required: true})

</script>

<template>
  <span>
    Acá estarán los campos de edición
  </span>
</template>

<style scoped>

</style>