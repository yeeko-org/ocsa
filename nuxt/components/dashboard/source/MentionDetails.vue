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

</script>

<template>
  <v-col
    cols="12"
    :md="is_full ? 6 : 12"
  >
    <v-card elevation="3" variant="elevated" color="indigo">
      <div class="px-3 py-2" v-if="is_full">
        <div class="text-h6">
          {{ mention.project.official_name }}
        </div>
        <div class="d-flex flex-wrap">
          <StatusChip
            v-if="mention.project.status_register"
            :main="mention.project"
            collection="register"
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
<!--      <v-card-text>-->
<!--        <v-col-->
<!--          cols="12"-->
<!--          v-for="status_record in mention.status_history"-->
<!--          :key="status_record.id"-->
<!--          class="d-flex"-->
<!--        >-->
<!--          <v-date-input-->
<!--            _v-model="new_date"-->
<!--            label="Fecha del status"-->
<!--            max-width="220"-->
<!--            class="mr-2"-->
<!--          ></v-date-input>-->
<!--          <GenericSelect-->
<!--            :final_filters="status_record"-->
<!--            collection="status_project"-->
<!--            collection_group="status_project"-->
<!--            field="status_project"-->
<!--            label="Status reportado"-->
<!--            clearable-->
<!--            density="default"-->
<!--            style="max-width: 220px; min-width: 200px;"-->
<!--            _change-status="applyFilters"-->
<!--          />-->
<!--        </v-col>-->

<!--      </v-card-text>-->
      <ToolbarCommon
        v-if="true"
        :main_object="mention"
        main_collection_name="mention"
        filter_group_name="status_projects"
        child_relation_name="status_history"
        field="status_history"
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
      <v-divider></v-divider>
      <ToolbarCommon
        v-if="true"
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
            rows="1"
            auto-grow
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
      >
        <template #rows_init="{ item }">
          <v-chip
            class="py-1"
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
        <template #rows="{ item }">
          <ToolbarCommon
            v-if="true"
            :main_object="item"
            main_collection_name="participant"
            filter_group_name="interest_types"
            child_relation_name="interest"
            field="interests"
            second_level
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
          <v-divider class="mt-8"></v-divider>
        </template>
      </ToolbarCommon>
      <ToolbarCommon
        v-if="true"
        :main_object="mention"
        main_collection_name="mention"
        filter_group_name="event_types"
        child_relation_name="event"
        field="events"
      >
        <template #rows="{ item }">
          <v-text-field
            v-model="item.description"
            label="Descripción del evento (opcional)"
            variant="outlined"
            density="compact"
            hide-details
            auto-grow
            style="width: 100%;"
          >
          </v-text-field>
          <ToolbarCommon
            v-if="true"
            :main_object="item"
            main_collection_name="event"
            filter_group_name="involved_roles"
            child_relation_name="involved"
            field="involvements"
            second_level
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
              <div class="d-flex mr-8">
                <v-text-field
                  v-model="item.number_women"
                  type="number"
                  label="Mujeres"
                  class="mr-2"
                  variant="outlined"
                  density="compact"
                  max-width="100"
                ></v-text-field>
                <v-text-field
                  v-model="item.number_men"
                  type="number"
                  label="Hombres"
                  class="mr-2"
                  variant="outlined"
                  density="compact"
                  max-width="100"
                ></v-text-field>
                <v-text-field
                  v-model="item.number_mix"
                  type="number"
                  label="Otros"
                  class="mr-2"
                  variant="outlined"
                  density="compact"
                  max-width="120"
                ></v-text-field>
              </div>
            </template>
          </ToolbarCommon>
        </template>
      </ToolbarCommon>
      <v-divider></v-divider>

    </v-card>
  </v-col>
</template>

<style scoped>

</style>