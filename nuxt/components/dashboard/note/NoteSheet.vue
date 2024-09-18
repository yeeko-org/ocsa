<script setup>

import MentionDetails from "~/components/dashboard/note/MentionDetails.vue";
import GenericSelect from "~/components/dashboard/impact/GenericSelect.vue";
import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";

import { ref, defineProps, defineEmits } from 'vue'

const props = defineProps({
  full_note: {
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
    color="blue-lighten-5"
  >
    <v-sheet
      v-if="full_note"
      color="deep-purple-lighten-5"
      class="mt-n2 mb-n4 pa-3"
    >
      <v-card class="mb-3 pa-3">
        <v-card-text class="d-flex flex-wrap">
          <v-text-field
            v-model="full_note.title"
            label="Título de la nota"
            variant="outlined"
            style="width: 100%;"
          >
          </v-text-field>
          <GenericSelect
            :final_filters="full_note"
            collection="sources"
            field="source"
            label="Medio o fuente"
            clearable
            hide_details
            style="width: 200px;"
            class="mr-2"
            density="default"
          />
          <v-text-field
            v-model="full_note.section"
            label="Sección"
            variant="outlined"
            class="mr-2"
            style="width: 200px;"
          >
          </v-text-field>
          <v-text-field
            v-model="full_note.link"
            label="Enlace a la nota"
            variant="outlined"
            class="mr-2"
            style="width: 600px;"
          >
          </v-text-field>
          <StatusDetail
            :final_filters="full_note"
            field="status_register"
            collection="validation"
            label="Status de registro"
            style="max-width: 300px;"
            density="default"
          />
        </v-card-text>
      </v-card>
      <v-card>
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
      </v-card>
    </v-sheet>
  </v-expansion-panel-text>
</template>

<style scoped>

</style>