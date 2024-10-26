<script setup>

import MentionDetails from "~/components/dashboard/source/MentionDetails.vue";

import { ref } from 'vue'
import NoteEdit from "~/components/dashboard/source/note/NoteEdit.vue";

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
const new_mention = ref({})
const dialog_mention = ref(false)

const openNote = () => {
  console.log("open note")
}

const full_note = computed(() => {
  return props.full_main
})

const addMention = () => {
  console.log("add mention")
}

</script>

<template>
  <v-card v-if="full_note.mentions">
    <v-card-title>
      <div class="d-flex">
        {{ full_note.mentions.length }} menciones de proyectos
        <v-spacer></v-spacer>
        <v-btn
          @click="addMention"
          color="primary"
          variant="outlined"
          prepend-icon="add"
          text="Agregar mención"
        ></v-btn>
      </div>
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
</template>

<style scoped>

</style>