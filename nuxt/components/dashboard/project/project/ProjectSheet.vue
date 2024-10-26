<script setup>

import NoteHeader from "~/components/dashboard/source/note/NoteHeader.vue";
import MentionDetails from "~/components/dashboard/source/MentionDetails.vue";

import { ref, computed } from 'vue'
import ProjectEdit from "~/components/dashboard/project/project/ProjectEdit.vue";

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

const full_project = computed(() => {
  return props.full_main
})

</script>

<template>
  <v-card v-if="full_project.mentions">
    <v-card-title class="text-deep-purple">
      {{ full_project.mentions.length }} Notas:
    </v-card-title>
    <v-card-text>
      <v-expansion-panels multiple>
        <v-expansion-panel
          v-for="mention in full_project.mentions"
          :key="mention.id"
        >
          <NoteHeader
            :main="mention.note"
            :mentions="[mention]"
            :show_details="show_details"
            @open-panel="openNote"
            parent="project"
          />
          <v-expansion-panel-text
            _class="ml-n16 mr-n6"
            color="deep-purple-lighten-5"
          >
            <MentionDetails
              :mention="mention"
            />
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

    </v-card-text>

  </v-card>
  <v-card class="my-3">
    <v-card-title>
      Todos los actores:
    </v-card-title>
  </v-card>
</template>

<style scoped>

</style>