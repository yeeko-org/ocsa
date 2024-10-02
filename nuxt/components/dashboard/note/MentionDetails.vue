<script setup>

import StatusChip from "~/components/dashboard/status/StatusChip.vue";
import ImpactDetails from "~/components/dashboard/impact/ImpactDetails.vue";
import GenericSelect from "~/components/dashboard/common/GenericSelect.vue";
import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";

import { ref } from 'vue'
import EventDetails from "~/components/dashboard/event/EventDetails.vue";

const props = defineProps({
  mention: Object,
  is_full: {
    type: Boolean,
    default: false,
  },
})

</script>

<template>
  <v-col
    cols="12"
    :md="is_full ? 6 : 12"
  >
    <v-card elevation="3">
      <div class="px-3 py-2" v-if="is_full">
        <div class="text-h6">
          {{ mention.project.official_name }}
        </div>
        <div class="d-flex flex-wrap">
          <StatusChip
            v-if="mention.project.status_register"
            :main="mention.project"
            collection="validation"
            field="status_register"
            left_label
            label="Registro:"
            class="mb-1"
            bold_text
          />
          <ExtractivismIcons
            :project="mention.project"
            show_name
            class="ml-2"
          />
        </div>
      </div>
      <div class="px-3 py-2" v-else-if="mention.note">
        <div class="text-h6 d-flex">
          <v-icon>
            newspaper
          </v-icon>
          {{ mention.note.title }}
          <v-btn
            v-if="mention.note.link"
            color="primary"
            icon
            :href="mention.note.link"
            target="_blank"
            class="ml-2"
            size="small"
            variant="text"
          >
            <v-icon>open_in_new</v-icon>
          </v-btn>
        </div>
        <div class="d-flex flex-wrap">
          <span v-if="mention.note.section">
            <b>Sección:</b> {{ mention.note.section }}
          </span>
          <StatusChip
            :main="mention.note"
            collection="validation"
            field="status_register"
            left_label
            label="Registro:"
            class="mb-1"
            bold_text
          />
        </div>
      </div>
      <v-divider></v-divider>
      <v-card-text>
        <v-col
          cols="12"
          v-for="status_record in mention.status_history"
          :key="status_record.id"
          class="d-flex"
        >
          <v-date-input
            _v-model="new_date"
            label="Fecha del status"
            max-width="220"
            class="mr-2"
          ></v-date-input>
          <GenericSelect
            :final_filters="status_record"
            collection="status_project"
            collection_type="status_project"
            field="status_project"
            label="Status reportado"
            clearable
            density="default"
            style="max-width: 220px; min-width: 200px;"
            _change-status="applyFilters"
          />
        </v-col>

      </v-card-text>
      <v-divider></v-divider>
      <ImpactDetails :mention="mention"/>
      <EventDetails :mention="mention" v-if="mention.events" />

      <v-divider></v-divider>

    </v-card>
  </v-col>
</template>

<style scoped>

</style>