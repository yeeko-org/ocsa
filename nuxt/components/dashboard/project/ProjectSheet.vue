<script setup>

import NoteHeader from "~/components/dashboard/note/NoteHeader.vue";
import MentionDetails from "~/components/dashboard/note/MentionDetails.vue";
import GenericSelect from "~/components/dashboard/impact/GenericSelect.vue";
import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";
import MegaProjectType from "~/components/dashboard/project/MegaProjectType.vue";

import { ref, defineProps, defineEmits } from 'vue'

const props = defineProps({
  full_project: {
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
        <div class="d-flex">
          <v-text-field
            v-model="full_project.official_name"
            label="Nombre oficial"
            width="400"
            max-width="400"
            variant="outlined"
          >
          </v-text-field>
          <StatusDetail
            :final_filters="full_project"
            field="status_register"
            collection="validation"
            label="Status de registro"
            style="max-width: 300px;"
          />
        </div>
        <MegaProjectType
          :project="full_project"
        />
        <GenericSelect
          :final_filters="full_project"
          collection="scales"
          field="scale"
          label="Escala"
          clearable
          hide_details
          style="max-width: 300px; min-width: 200px;"
          _change-status="applyFilters"
          density="comfortable"
        />
      </v-card>
      <v-card v-if="full_project.mentions">
        <v-card-title>
          {{ full_project.mentions.length }} Notas:
        </v-card-title>
        <v-card-text>
          <v-expansion-panels multiple>
            <v-expansion-panel
              v-for="mention in full_project.mentions"
              :key="mention.id"
            >
              <NoteHeader
                :note="mention.note"
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