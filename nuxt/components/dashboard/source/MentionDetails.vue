<script setup>

import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
import SelectDate from "~/components/dashboard/common/select/SelectDate.vue";
import ParticipantsToolbar from "~/components/dashboard/source/ParticipantsToolbar.vue";
import EventToolbar from "~/components/dashboard/source/EventToolbar.vue";
import CardCommon from "~/components/dashboard/common/CardCommon.vue";

import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import {nextTick} from "vue";
import LocationsToolbar from "~/components/dashboard/space_time/LocationsToolbar.vue";
const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)
const { saveSimple, getRelatedActors } = mainStore

const props = defineProps({
  mention: Object,
  is_full: {
    type: Boolean,
    default: false,
  },
})
const dialog_search = ref(false)
const total_requests = ref(0)
const resolved_requests = ref(0)
const saving = ref(false)
const snackbar = ref(false)
const actor_display = ref(null)

const emits = defineEmits(['mention-saved'])

function searchActor() {
  getRelatedActors(props.mention.project).then(actors => {
    actors = actors.filter(actor => {
      return !props.mention.participants.some(
        part => part.actor === actor.id)
    })
    actors = actors.map(actor => {
      const part_types = actor.participant_types.filter(p_type => p_type)
      const unique_part_types = [...new Set(part_types)]
      if (unique_part_types.length === 1)
        actor.participant_type = unique_part_types[0]
      return actor
    })
    dialog_search.value = true
    nextTick(() => {
      actor_display.value.setInitResults(actors)
    })
  })
}

function saveOneToMany(snake_name, main_item) {
  // console.log("save one to many", snake_name, main_item)
  const main_schema = schemas.value.collections_dict[snake_name]
  const one_to_many = main_schema.fields.filter(
    field => field.relation_type === 'one_to_many')
  one_to_many.forEach(field => {
    if (['involved', "eventlocation"].includes(field.name))
      return
    const related_collection = schemas.value.collections_dict[
        field.related_model]
    // console.log("related_collection", related_collection)
    const snake_name2 = related_collection.snake_name
    // console.log("main_item", main_item)
    // console.log("field", field.name)
    main_item[field.name].forEach(item => {
      saveOneToMany(snake_name2, item)
      total_requests.value += 1
      saveSimple([snake_name2, item]).then(res => {
        // console.log(`response ${snake_name2}`, res)
        resolved_requests.value += 1
        // const idx = main_item[field.name].findIndex(
        //   item2 => item2.id === item.id)
        allFinished()
      })
    })
  })
}

function saveMention() {
  saving.value = true
  total_requests.value = 0
  resolved_requests.value = 0
  saveOneToMany('mention', props.mention)
}

function allFinished() {
  if (resolved_requests.value === total_requests.value){
    saveSimple(['mention', props.mention]).then(res => {
      emits('mention-saved', res)
      snackbar.value = true
      saving.value = false
    })
  }
}

function saveParticipant([elem_in_edition, actor]) {
  const part_idx = props.mention.participants.findIndex(
    part => part.id === elem_in_edition.id)
  props.mention.participants.splice(part_idx, 1, {
    ...elem_in_edition,
    actor: actor.id,
    actor_full: actor,
  })
}

function saveNewParticipant(actor) {
  console.log("saveNewParticipant", actor)
  const params = {
    mention: props.mention.id,
    actor: actor.id,
  }
  if (actor.participant_type)
    params.participant_types = [actor.participant_type]
  saveSimple(['participant', params]).then(response => {
    props.mention.participants.unshift(response)
    dialog_search.value = false
  })
}

function closeChangeDialog(event) {
  if (event)
    saveNewParticipant(event)
  dialog_search.value = false
}

function changeProject(project) {
  props.mention.project = project.id
  props.mention.project_full = project
}

</script>

<template>
  <v-col
    cols="12"
    _md="is_full ? 6 : 12"
  >
    <v-card variant="outlined" color="indigo-lighten-1">
<!--      <div class="px-3 py-2" v-else-if="mention.note">-->
<!--        <div class="text-h6 d-flex">-->
<!--          <v-icon>-->
<!--            newspaper-->
<!--          </v-icon>-->
<!--          {{ mention.note.title }}-->
<!--          <v-btn-->
<!--            v-if="mention.note.link"-->
<!--            color="accent"-->
<!--            icon-->
<!--            :href="mention.note.link"-->
<!--            target="_blank"-->
<!--            class="ml-2"-->
<!--            size="small"-->
<!--            variant="text"-->
<!--          >-->
<!--            <v-icon>open_in_new</v-icon>-->
<!--          </v-btn>-->
<!--        </div>-->
<!--        <div class="d-flex flex-wrap">-->
<!--          <span v-if="mention.note.section">-->
<!--            <b>Sección:</b> {{ mention.note.section }}-->
<!--          </span>-->
<!--          <StatusChip-->
<!--            :main="mention.note"-->
<!--            collection="register"-->
<!--            left_label-->
<!--            class="mb-1"-->
<!--            bold_text-->
<!--          />-->
<!--        </div>-->
<!--      </div>-->
      <v-divider></v-divider>
      <v-row class="py-3 mx-0" v-if="mention.id">
        <v-col cols="7">
          <CardCommon
            :full_main="mention.project_full"
            :collection_data="schemas.collections_dict.project"
            @selected-item="changeProject"
            indirect_get
            class="py-3"
          />
        </v-col>
        <ToolbarCommon
          :cols="5"
          :main_object="mention"
          main_collection_name="mention"
          filter_group_name="status_projects"
          child_relation_name="status_history"
          field="status_history"
          color="purple"

        >
          <template #rows_init="{item}" v-if="true">
            <div
              class="d-flex align-start align-self-start"
            >
              <v-chip variant="outlined" color="grey" min-width="150" label>
                Status
              </v-chip>
            </div>
            <v-spacer></v-spacer>
            <SelectDate
              :init_date="item.date"
              @update-date="item.date = $event"
              label="Fecha de cambio"
              class="mb-n6"
              hide_details
            />
          </template>
        </ToolbarCommon>
<!--        <ToolbarCommon-->
<!--          :cols="7"-->
<!--          :main_object="mention"-->
<!--          main_collection_name="mention"-->
<!--          filter_group_name="impact_types"-->
<!--          child_relation_name="impact"-->
<!--          field="impacts"-->
<!--          required-->
<!--        >-->
<!--          <template #rows="{ item }">-->
<!--            <v-textarea-->
<!--              v-model="item.description"-->
<!--              label="Descripción de la afectación"-->
<!--              variant="outlined"-->
<!--              density="compact"-->
<!--              hide-details-->
<!--              rows="1"-->
<!--              auto-grow-->
<!--              style="max-width: 600px;"-->
<!--            ></v-textarea>-->
<!--          </template>-->
<!--        </ToolbarCommon>-->
        <ToolbarCommon
          :main_object="mention"
          main_collection_name="mention"
          filter_group_name="impact_types"
          child_relation_name="impact"
          field="impacts"
          two_columns
          required
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
          <template #second-column="{ item }">
            <LocationsToolbar
              v-if="item"
              :full_main="item"
              main_collection_name="impact"
              second_level
            />
          </template>
        </ToolbarCommon>
        <ParticipantsToolbar
          :mention="mention"
          @search-item="searchActor"
          @selected-item="saveParticipant($event)"
        />
        <EventToolbar
          :mention="mention"
        />
        <v-col cols="12" class="d-flex justify-end px-6">
          <v-btn
            color="accent"
            variant="elevated"
            :loading="saving"
            @click="saveMention"
          >
            Guardar cambios
          </v-btn>
        </v-col>
      </v-row>
    </v-card>
    <v-snackbar
      v-model="snackbar"
      color="success"
      location="right top"
      location-strategy="connected"
    >
      Se ha guardado la mención
      <template v-slot:actions>
        <v-btn
          color="accent"
          variant="text"
          @click="snackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
    <v-dialog
      v-model="dialog_search"
      max-width="920"
    >
      <v-card height="800">
        <v-card-text class="py-0">
          <CollectionDisplay
            ref="actor_display"
            :parent_collection="schemas.collections_dict.actor"
            is_mini
            @select-item="closeChangeDialog"
          />
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-col>
</template>

<style scoped>

</style>