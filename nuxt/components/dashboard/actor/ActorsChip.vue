<script setup>
import { ref, computed } from 'vue'
import { actorCounter } from "~/composables/actor_counter.js";

const props = defineProps({
  main: Object,
  mentions: Array,
  participants: Array,
  field: {
    type: String,
    required: false,
    default: "actor_full",
  },
  subfield: String,
  is_simple: Boolean,
})

const actor_by_position = computed(() => {
  let all_participants
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
    :color="actor_by_position.length ? 'blue' : 'warning'"
    class="d-flex pa-1"
    rounded
    variant="outlined"
  >
    <div
      v-for="position in actor_by_position"
      class="d-flex flex-column align-center px-1"
    >
      <span
        v-if="!is_simple"
        class="text-caption"
        :class="`text-${position.color}`"
      >
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
          class="mx-n4 my-n2"
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
    <div
      v-if="!actor_by_position.length"
      class="d-flex flex-column align-center"
    >
      <div class="text-warning text-body-2">
        0
      </div>
      <v-icon color="warning">
        warning
      </v-icon>
      <v-tooltip
        activator="parent"
        location="bottom"
      >
        <v-card
          color="warning"
          class="mx-n4 my-n2"
        >
          <v-card-title
            class="text-subtitle-1"
            _class="`text-${position.color}`"
          >
            No hay ningún actor participante
          </v-card-title>
        </v-card>
      </v-tooltip>
    </div>
  </v-card>
</template>

<style scoped>

</style>