<script setup>
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";

import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
import ParticipantsToolbar from "~/components/dashboard/source/ParticipantsToolbar.vue";
import EventToolbar from "~/components/dashboard/event/event/EventToolbar.vue";
import CardCommon from "~/components/dashboard/common/generic/CardCommon.vue";
import ImpactToolbar from "~/components/dashboard/impact/impact/ImpactToolbar.vue";
import StatusHistoryToolbar from "~/components/dashboard/project/status_history/StatusHistoryToolbar.vue";
import DialogSearch from "~/components/dashboard/common/dialog/DialogSearch.vue";
import ProjectCard from "~/components/dashboard/project/project/ProjectCard.vue";

const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)
const { showSnackbar } = mainStore
const { saveSimple, getRelatedActors, deleteSimple, patchSimple } = mainStore
import {savePreItem, saveItemMixed, discardPreItem, mixOrigins} from "~/composables/mix_pre_capture.js";
import { useSaveElements } from "~/composables/save_elements.js";
const { saveComplex, save_errors } = useSaveElements()

const props = defineProps({
  note_id: Number,
  is_full: {
    type: Boolean,
    default: false,
  },
  full_article: Object,
  two_columns: Boolean,
})
const mention = defineModel({type: Object, required: true})


const emits = defineEmits(
  ['mention-saved', 'mention-deleted', 'mention-accepted',
    'mention-discarded'])
defineExpose({ allFinished })

const all_saving = ref(false)

const participantsRef = ref(null)

async function allFinished(mention_id=null, pre_data=null) {
  if (mention_id && mention_id !== mention.value.id)
    return
  const res = await saveItemMixed('mention', mention.value, pre_data)
  emits('mention-saved', res)
  all_saving.value = false
  participantsRef.value.resetInitialData()
  eventsRef.value.resetInitialData()
}

const impactsRef = ref(null)
const statusHistoryRef = ref(null)
const eventsRef = ref(null)
async function saveMention() {
  const valid = await Promise.all([
    participantsRef.value.validate(),
    eventsRef.value.validate(),
    impactsRef.value.validate(),
    statusHistoryRef.value.validate(),
  ]).then(results => results.every(res => res))
  // console.log("saveMention valid", valid)
  if (!valid){
    save_errors.value = [{
      field: 'todo el formulario',
      errors: 'Hay errores con algunos campos, scrolea y revísalos.'
    }]
    return
  }
  all_saving.value = true
  saveComplex('mention', mention.value)
    .then(() => {
      allFinished(null, mention.value.pre_data)
    })
    .catch(errors => {
      console.error("Errores al guardar:", errors)
      all_saving.value = false
    })
}

const dialog_search_actor = ref(false)
const actor_display = ref(null)
const participant_group_selected = ref(null)


const all_actors = computed(() => {
  return mention.value.participants.map(participant => {
    return {...participant.actor_full, ...participant}
  })
})

function searchActor(group) {
  // console.log("group to search", group)
  getRelatedActors(mention.value.project, group.id).then(actors => {
    actors = actors.filter(actor => {
      return !mention.value.participants.some(
        part => part.actor === actor.id)
    })
    actors = actors.map(actor => {
      const part_types = actor.participant_types.filter(p_type => p_type)
      const unique_part_types = [...new Set(part_types)]
      if (unique_part_types.length === 1)
        actor.participant_type = unique_part_types[0]
      return actor
    })
    if (group)
      participant_group_selected.value = group.id
    dialog_search_actor.value = true
    nextTick(() => {
      actor_display.value.setInitResults(actors)
    })
  })
}

async function saveParticipant([elem_in_edition, part_idx, actor]) {
  if (!elem_in_edition.id && elem_in_edition.path){
    await saveNewParticipant(actor, elem_in_edition, part_idx)
  }
  else{
    mention.value.participants.splice(part_idx, 1, {
      ...elem_in_edition,
      actor: actor.id,
      actor_full: actor,
    })
  }
}

async function saveNewParticipant(actor, participant=null, part_idx=null) {
  const params = {
    mention: mention.value.id,
    actor: actor.id,
  }
  // console.log("actor to save", actor)
  if (participant && participant.participant_type)
    params.participant_types = [participant.participant_type]
  else if (actor.participant_type)
    params.participant_types = [actor.participant_type]
  let response = null
  if (participant){
    response = await savePreItem(
      participant.path, 'participant', props.note_id, params)
  }
  else{
    response = await saveSimple(['participant', params])
  }

  if (!actor.participant_type && participant_group_selected.value)
    response.participant_group = participant_group_selected.value
  else if (participant && participant.participant_group)
    response.participant_group = participant.participant_group
  else if (actor.participant_group)
    response.participant_group = actor.participant_group
  if (participant && part_idx !== null){
    mention.value.participants.splice(part_idx, 1, {
      ...response,
      actor: actor.id,
      actor_full: actor,
    })
  }
  else{
    mention.value.participants.unshift(response)
  }
  dialog_search_actor.value = false
}

async function discardParticipant([pre_item, index]) {
  const new_pre_item = await discardPreItem(
    pre_item.path, 'participant', props.note_id)
  console.log("new_pre_item Participant", new_pre_item)
  mention.value.participants.splice(index, 1)
  mention.value.participants.push(new_pre_item)
}

function closeChangeDialog(actor_data) {
  if (actor_data)
    saveNewParticipant(actor_data)
  else
    dialog_search_actor.value = false
}
const project_errors = ref(null)
async function changeProject(project) {
  project_errors.value = null
  if (mention.value.path && mention.value.discarded === null){
    emits('mention-accepted', project)
  }
  else{
    const params = {project: project.id, note: mention.value.note}
    const res = await patchSimple(['mention', mention.value.id, params])
    if (res.errors){
      project_errors.value = res.errors
      return
    }
    mention.value.project = project.id
    const pre_data = mention.value.project_full.pre_data
    if (pre_data)
      mention.value.project_full = mixOrigins(project, pre_data, 2)
    else
      mention.value.project_full = project
  }
}

const project_init_filters = computed(() => {
  if (mention.value.path && mention.value.project_full.locations.length > 0) {
    const first_location = mention.value.project_full.locations[0]
    return {
      state: first_location.state || null,
      q: mention.value.project_full.name || null,
    }
  }
  return {}
})


const dialog_delete = ref(false)
function deleteMention() {
  if (!mention.value.id)
    return
  all_saving.value = true
  deleteSimple(['mention', mention.value.id]).then(() => {
    emits('mention-deleted', mention.value.id)
    all_saving.value = false
    dialog_delete.value = false
    showSnackbar('Se ha eliminado la mención')
  })
}

async function discardLocation(pre_item) {
  const index = mention.value.project_full.locations.findIndex(
    loc => loc.path === pre_item.path)
  const new_pre_item = await discardPreItem(
    pre_item.path, 'location', props.note_id)
  mention.value.project_full.locations.splice(index, 1, new_pre_item)
}


</script>

<template>
  <v-card
    :variant="mention.discarded ? 'tonal' : 'outlined'"
    :color="mention.discarded ? 'red-lighten-3' : 'indigo-lighten-1'"
  >
    <v-row class="py-3 mx-0" v-if="mention.id || mention.path">
      <v-col cols="7">
        <v-card
          v-if="project_errors"
          class="my-2 px-3 py-2"
          elevation="2"
          color="red-lighten-3"
        >
          Errores: {{project_errors}}
        </v-card>

        <CardCommon
          v-if="mention.project_full"
          :full_main="mention.project_full"
          collection_name="project"
          :note_id="note_id"
          :init_filters="project_init_filters"
          indirect_get
          class="py-3"
          @selected-item="changeProject($event)"
          @discard-item="emits('mention-discarded')"
        >
          <template #card="{ final_collection_data }">
            <ProjectCard
              :final_collection_data="final_collection_data"
              :full_main="mention.project_full"
              @discard-location="discardLocation"
              :note_id="note_id"
            />

          </template>
          <template
            v-if="mention.project_full?.paragraphs && full_article"
            #dialog="{ closeSearchDialog }"
          >
            <DialogSearch
              collection_name="project"
              :full_main="mention.project_full"
              :full_article="full_article"
              :note_id="note_id"
              :show_base="true"
              :init_filters="project_init_filters"
              @selected-item="closeSearchDialog"
            />
<!--                <v-btn-->
<!--                  color="red"-->
<!--                  variant="text"-->
<!--                  @click="closeSearchDialog(); newTest"-->
<!--                >-->
<!--                  Descartar mención-->
<!--                </v-btn>-->
          </template>
        </CardCommon>
      </v-col>
      <StatusHistoryToolbar
        v-model="mention.status_history"
        :parent_id="mention.id"
        :note_id="note_id"
        ref="statusHistoryRef"
        class="mt-2"
      />
      <ImpactToolbar
        v-model="mention.impacts"
        :parent_id="mention.id"
        :note_id="note_id"
        ref="impactsRef"
        class="mt-2"
      />
      <ParticipantsToolbar
        v-model="mention.participants"
        :parent_id="mention.id"
        :note_id="note_id"
        ref="participantsRef"
        @search-item="searchActor($event)"
        @selected-item="saveParticipant($event)"
        @discard-participant="discardParticipant"
      />
      <EventToolbar
        v-model="mention.events"
        :all_actors="all_actors"
        :parent_id="mention.id"
        :note_id="note_id"
        ref="eventsRef"
      />
      <v-row v-if="save_errors.length > 0">
        <v-col
          v-for="(error, index) in save_errors"
          :key="index"
          cols="12"
          class="d-flex justify-end px-6 py-1"
        >
          <v-alert
            type="error"
          >
            Error al guardar {{ error.field }}: {{ error.errors }}
            <v-code v-if="error.item">
              {{ error.item }}
            </v-code>
          </v-alert>
        </v-col>
      </v-row>
      <v-col cols="12" class="d-flex justify-end px-6">
        <v-btn
          color="red"
          variant="outlined"
          class="mr-4"
          :disabled="all_saving"
          @click="dialog_delete = true"
        >
          Eliminar mención
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          color="accent"
          variant="elevated"
          :loading="all_saving"
          @click="saveMention"
        >
          Guardar cambios
        </v-btn>
      </v-col>
    </v-row>
    <v-dialog
      v-model="dialog_search_actor"
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
    <v-dialog
      v-model="dialog_delete"
      max-width="600"
    >
      <v-card class="pa-3">
        <v-card-title>
          ¿Confirmas la eliminación de esta mención?
        </v-card-title>
        <v-card-subtitle>
          Esta acción no se puede deshacer
        </v-card-subtitle>
        <v-card-actions class="py-4">
          <v-btn
            color="accent"
            variant="outlined"
            @click="dialog_delete = false"
          >
            Cancelar
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            color="error"
            variant="elevated"
            @click="deleteMention"
          >
            Eliminar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<style scoped>

</style>