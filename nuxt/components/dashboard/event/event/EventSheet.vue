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

const full_event = ref(props.full_main)

</script>

<template>
  {{ full_event }}
</template>

<style scoped>

</style>