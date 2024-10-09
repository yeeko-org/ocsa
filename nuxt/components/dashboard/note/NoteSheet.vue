<script setup>

import MentionDetails from "~/components/dashboard/note/MentionDetails.vue";

import { ref } from 'vue'
import NoteEdit from "~/components/dashboard/note/NoteEdit.vue";

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

const openNote = () => {
  console.log("open note")
}

const full_note = computed(() => {
  return props.full_main
})

</script>

<template>
  <v-expansion-panel-text
    class="ml-n16 mr-n6"
    color="blue-lighten-5"
  >
    <v-sheet
      v-if="full_note"
      color="deep-purple-lighten-5"
      class="mt-n2 mb-n4 pa-3"
    >
      <v-card class="mb-3 pa-3">
        <NoteEdit
          :full_main="full_note"
          :is_edit="true"
        />

      </v-card>
      <v-card v-if="full_note.mentions">
        <v-card-title>
          {{ full_note.mentions.length }} menciones de proyectos
        </v-card-title>
        <v-card-text>
          <v-row>
            <MentionDetails
              v-for="mention in full_note.mentions"
              :key="mention.id"
              :mention="mention"
              is_full
            />
          </v-row>
        </v-card-text>
      </v-card>
      <v-card class="my-3">
        <v-card-title>
          -----
        </v-card-title>
        <v-card-text v-if="!full_note.mentions">
          {{full_note}}
        </v-card-text>
      </v-card>
    </v-sheet>
  </v-expansion-panel-text>
</template>

<style scoped>

</style>