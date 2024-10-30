<script setup>

import StatusChip from "~/components/dashboard/status/StatusChip.vue";
import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";
import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";
import { computed } from "vue";

const props = defineProps({
  mention: Object,
  is_full: {
    type: Boolean,
    default: false,
  },
})

const all_actors = computed(() => {
  return props.mention.participants.map(participant => {
    return {...participant.actor, ...participant}
  })
})

function editItem(item) {
  console.log("edit item", item)
}

function saveMention() {
  console.log("save mention")
}

</script>

<template>
  <v-col
    cols="12"
    _md="is_full ? 6 : 12"
  >
    <v-card variant="outlined" color="indigo-lighten-1">
      <div class="px-3 py-2" v-if="is_full">
        <div class="text-h6">
          {{ mention.project.official_name }}
        </div>
        <div class="d-flex flex-wrap">
          <StatusChip
            v-if="mention.project.status_register"
            :main="mention.project"
            collection="register"
            left_label
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
            color="accent"
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
            collection="register"
            left_label
            class="mb-1"
            bold_text
          />
        </div>
      </div>
      <v-divider></v-divider>
      <v-row class="py-3 mx-0">
        <ToolbarCommon
          :cols="5"
          v-if="true"
          :main_object="mention"
          main_collection_name="mention"
          filter_group_name="status_projects"
          child_relation_name="status_history"
          field="status_history"
          color="purple"
        >
          <template #rows="{ item }">
            <v-date-input
              _v-model="new_date"
              label="Fecha del status"
              max-width="220"
              class="ml-2"
            ></v-date-input>
          </template>
        </ToolbarCommon>
        <ToolbarCommon
          v-if="true"
          :cols="7"
          :main_object="mention"
          main_collection_name="mention"
          filter_group_name="impact_types"
          child_relation_name="impact"
          field="impacts"
        >
          <template #rows="{ item }">
            <v-textarea
              v-model="item.description"
              label="Descripción de la afectación"
              variant="outlined"
              density="compact"
              hide-details
              rows="1"
              auto-grow
              style="max-width: 600px;"
            ></v-textarea>
          </template>
        </ToolbarCommon>
        <ToolbarCommon
          v-if="true"
          :main_object="mention"
          main_collection_name="mention"
          filter_group_name="participant_types"
          child_relation_name="participant"
          field="participants"
          slot_before
          two_columns
          color="blue"
        >
          <template #rows_init="{ item }">
            <v-chip
              class="py-1 mb-2"
              prepend-icon="recent_actors"
              :text="item.actor.name"
              color="indigo lighten-4"
              closable
              close-icon="edit"
              close-label="Editar"
              @click:close="editItem(item)"
            >
            </v-chip>
          </template>
          <template #second-column="{ item }">
            <ToolbarCommon
              v-if="true"
              :main_object="item"
              main_collection_name="participant"
              filter_group_name="interest_types"
              child_relation_name="interest"
              field="interests"
              second_level
              color="cyan"
            >
              <template #rows="{ item }">
                <v-textarea
                  v-model="item.text"
                  label="Descripción del interés"
                  variant="outlined"
                  class="mr-8"
                  density="compact"
                  rows="1"
                  auto-grow
                ></v-textarea>
              </template>
            </ToolbarCommon>
            <v-divider class="mt-8" v-if="false"></v-divider>
          </template>
        </ToolbarCommon>
        <ToolbarCommon
          v-if="true"
          :main_object="mention"
          main_collection_name="mention"
          filter_group_name="event_types"
          child_relation_name="event"
          field="events"
          two_columns
          color="lime"
        >
          <template #rows="{ item }">
            <v-text-field
              v-model="item.description"
              label="Descripción del evento (opcional)"
              variant="outlined"
              density="compact"
              hide-details
              auto-grow
              style="width: 100%; max-width: 600px;"
            >
            </v-text-field>
          </template>
          <template #second-column="{ item }">
            <ToolbarCommon
              v-if="true"
              :main_object="item"
              main_collection_name="event"
              filter_group_name="involved_roles"
              child_relation_name="involved"
              field="involvements"
              second_level
              color="blue"
            >
              <template #rows="{ item }">
                <v-select
                  v-model="item.participant"
                  :items="all_actors"
                  item-title="name"
                  item-value="id"
                  label="Participante"
                  variant="outlined"
                ></v-select>
                <div class="text-subtitle-1">Número de víctimas:</div>
                <div class="d-flex mr-8">
                  <v-text-field
                    v-model="item.number_women"
                    type="number"
                    label="Mujeres"
                    class="mr-2"
                    variant="outlined"
                    density="compact"
                    max-width="140"
                    hide-details
                  ></v-text-field>
                  <v-text-field
                    v-model="item.number_men"
                    type="number"
                    label="Hombres"
                    class="mr-2"
                    variant="outlined"
                    density="compact"
                    max-width="140"
                    hide-details
                  ></v-text-field>
                  <v-text-field
                    v-model="item.number_mix"
                    type="number"
                    label="Otros"
                    class="mr-2"
                    variant="outlined"
                    density="compact"
                    max-width="140"
                    hide-details
                  ></v-text-field>
                </div>
              </template>
            </ToolbarCommon>
          </template>
        </ToolbarCommon>
        <v-col cols="12" class="d-flex justify-end px-6">
          <v-btn
            color="accent"
            variant="elevated"
            @click="saveMention"
          >
            Guardar cambios
          </v-btn>
        </v-col>
      </v-row>
    </v-card>
  </v-col>
</template>

<style scoped>

</style>