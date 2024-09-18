<script setup>
import { ref, computed, defineProps } from 'vue'
import { actorCounter } from "~/composables/actor_counter.js";

const props = defineProps({
  main: Object,
  mentions: Array,
  participants: Array,
  field: {
    type: String,
    required: false,
    default: "actor",
  },
  subfield: String,
})

const actor_by_position = computed(() => {
  let all_participants = []
  if (props.participants){
    all_participants = props.participants.map(
      participant => ({...participant, ...participant.mention}) )
  }
  else {
    const final_mentions = props.mentions || props.main.mentions
    all_participants = final_mentions.flatMap(mention => mention.participants)
  }
  return actorCounter(all_participants, props.field, props.subfield)
})

</script>

<template>
  <v-card
    v-if="actor_by_position.length"
    color="blue"
    class="d-flex pa-1"
    rounded
    variant="outlined"
  >
    <div
      v-for="position in actor_by_position"
      class="d-flex flex-column align-center px-1"
    >
      <span class="text-caption" :class="`text-${position.color}`">
        {{ position.count }}
      </span>
      <v-icon
        :color="position.color"
        size="small"
      >
        {{ position.icon }}
      </v-icon>
      <v-tooltip
        activator="parent"
        location="bottom"
      >
        <v-card
          :color="position.color"
        >
          <v-card-title
            class="text-subtitle-1"
            _class="`text-${position.color}`"
          >
            {{ position.name }}
          </v-card-title>
          <v-card-text>
            <div
              v-for="element in position.elements"
              :key="element"
              class="text-body-2"
            >
              {{ element }}
            </div>
          </v-card-text>
        </v-card>
      </v-tooltip>
    </div>
  </v-card>
</template>

<style scoped>

</style>