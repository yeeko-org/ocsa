<script setup>

import EventToolbar from "~/components/dashboard/event/event/EventToolbar.vue";

const full_main = defineModel({type: Object, required: true})
const events = ref([])
// const artificial_mention = computed(() => {
//   if (!full_main.value.involvements)
//     return []
//   const participants = full_main.value.involvements.map(
//       involvement => involvement.participant_full)
//   return {"events": [full_main.value], participants: participants}
// })
const all_actors = computed(() => {
  return full_main.value.involvements.map(involvement => {
    return {...involvement.participant_full}
  })
})
watch(
  full_main, (newVal) => {
    events.value = [newVal]
  }, {immediate: true}
)
</script>

<template>
  <v-card class="mb-4 pa-0">
    <EventToolbar
      v-model="events"
      :parent_id="full_main.id"
      :all_actors="all_actors"
    />
  </v-card>
</template>

<style scoped>

</style>