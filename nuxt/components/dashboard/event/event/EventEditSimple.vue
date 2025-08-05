<script setup>

import EventToolbar from "~/components/dashboard/event/event/EventToolbar.vue";

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
})

const artificial_mention = computed(() => {
  if (!props.full_main.involvements)
    return []
  const participants = props.full_main.involvements.map(
      involvement => involvement.participant_full)
  return {"events": [props.full_main], participants: participants}
})

</script>

<template>
  <v-card class="mb-4 pa-0">
    <EventToolbar
      :mention="artificial_mention"
    />
  </v-card>
</template>

<style scoped>

</style>