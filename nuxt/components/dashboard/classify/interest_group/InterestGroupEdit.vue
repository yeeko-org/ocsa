<script setup>
import CommonGroupEdit from "~/components/dashboard/generic/CommonGroupEdit.vue";

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <CommonGroupEdit :full_main="full_main" />
</template>

<style scoped>

</style>