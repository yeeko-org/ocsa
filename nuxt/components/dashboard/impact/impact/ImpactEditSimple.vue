<script setup>

import ImpactToolbar from "~/components/dashboard/impact/impact/ImpactToolbar.vue";

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
})

const artificial_mention = computed(() => {
  return {"impacts": [props.full_main]}
})

</script>

<template>
  <v-card class="mb-4 pa-0">
    <ImpactToolbar
      :mention="artificial_mention"
    />
  </v-card>
</template>

<style scoped>

</style>