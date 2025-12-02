<script setup lang="ts">

import ActivityHolder from "~/components/dashboard/activity/ActivityHolder.vue";

definePageMeta({
  middleware: 'dashboard',
  layout: 'dashboard',
})

</script>

<template>
  <ActivityHolder/>
</template>

<style scoped>

</style>