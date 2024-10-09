<script setup>

import NoteHeader from "~/components/dashboard/note/NoteHeader.vue";
import MentionDetails from "~/components/dashboard/note/MentionDetails.vue";
import GenericSelect from "~/components/dashboard/common/GenericSelect.vue";
import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";
import MegaProjectType from "~/components/dashboard/project/MegaProjectType.vue";

import { ref, computed } from 'vue'
import ProjectEdit from "~/components/dashboard/project/ProjectEdit.vue";

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
  <v-expansion-panel-text
    class="ml-n16 mr-n6"
    color="purple-lighten-5"
  >
    <v-sheet
      color="purple-lighten-5"
      class="mt-n2 mb-n4 pa-3"
    >
      <v-card class="mb-3 pa-3">
        <ProjectEdit
          :full_main="full_project"
          is_edit
        />
      </v-card>
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
    </v-sheet>
  </v-expansion-panel-text>
</template>

<style scoped>

</style>