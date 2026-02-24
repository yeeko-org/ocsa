<script setup>

import ParticipantsToolbar from "~/components/dashboard/source/ParticipantsToolbar.vue";

const full_main = defineModel({type: Object, required: true})
const participants = ref([])
// const artificial_mention = computed(() => {
//   if (!full_main.value.involvements)
//     return []
//   const participants = full_main.value.involvements.map(
//       involvement => involvement.participant_full)
//   return {"events": [full_main.value], participants: participants}
// })
const all_actors = computed(() => {
  return full_main.value.involvements.map(involvement => {
    const participant_full = involvement.participant_full
    return {...participant_full.actor_full, ...participant_full}
  })
})
watch(
  full_main, (newVal) => {
    participants.value = [newVal]
  }, {immediate: true}
)
</script>

<template>
  <v-card class="mb-4 pa-0">
    <ParticipantsToolbar
      ref="participantsRef"
      v-model="participants"
      :parent_id="full_main.id"
    />
  </v-card>
</template>

<style scoped>

</style>