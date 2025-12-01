<script setup>

import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
import SelectDate from "~/components/dashboard/common/select/SelectDate.vue";
import ParticipantsToolbar from "~/components/dashboard/source/ParticipantsToolbar.vue";
import EventToolbar from "~/components/dashboard/event/event/EventToolbar.vue";
import CardCommon from "~/components/dashboard/common/CardCommon.vue";

import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import {nextTick, watch} from "vue";
import LocationsToolbar from "~/components/dashboard/space_time/LocationsToolbar.vue";
import DisplacementToolbar from "~/components/dashboard/df/DisplacementToolbar.vue";
const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)
const { saveSimple, getRelatedActors, deleteSimple } = mainStore
import { useSaveElements } from "~/composables/save_elements.js";
import ImpactToolbar from "~/components/dashboard/impact/impact/ImpactToolbar.vue";
const { saveComplex, save_errors } = useSaveElements()


const props = defineProps({
  mention: Object,
  is_full: {
    type: Boolean,
    default: false,
  },
})

const has_select = ref(null)
const emits = defineEmits(['mention-saved', 'mention-deleted'])
defineExpose({ allFinished })

// const mention_id = computed(() => props.mention.id)

const all_saving = ref(false)

const participantsToolbarRef = ref(null)
// const snackbar_message = ref('')
// const snackbar = ref(false)

function allFinished(mention_id=null) {
  if (mention_id && mention_id !== props.mention.id)
    return

  saveSimple(['mention', props.mention]).then(res => {
    emits('mention-saved', res)
    all_saving.value = false
    // console.log("participantsToolbarRef", participantsToolbarRef.value)
    participantsToolbarRef.value.resetInitialData()
    eventsToolbarRef.value.resetInitialData()
  })
}

const mentionForm = ref(null)
async function saveMention() {
  const { valid } = await mentionForm.value.validate()
  // console.log("saveMention valid", valid)
  if (!valid){
    save_errors.value = [{
      field: 'todo el formulario',
      errors: 'Hay errores con algunos campos, scrolea y revísalos.'
    }]
    return
  }
  all_saving.value = true
  saveComplex('mention', props.mention)
    .then(() => {
      allFinished()
    })
    .catch(errors => {
      console.error("Errores al guardar:", errors)
      all_saving.value = false
    })
}

const dialog_search = ref(false)
const actor_display = ref(null)
const eventsToolbarRef = ref(null)
const participant_group_selected = ref(null)

function searchActor(group) {
  // console.log("group to search", group)
  getRelatedActors(props.mention.project, group.id).then(actors => {
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
    if (group)
      participant_group_selected.value = group.id
    dialog_search.value = true
    nextTick(() => {
      actor_display.value.setInitResults(actors)
    })
  })
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
  const params = {
    mention: props.mention.id,
    actor: actor.id,
  }
  console.log("actor to save", actor)
  if (actor.participant_type)
    params.participant_types = [actor.participant_type]
  saveSimple(['participant', params]).then(response => {
    // props.mention.participants.push(response)
    // response.participant_group = participant_group_selected.value,
    if (!actor.participant_type && participant_group_selected.value)
      response.participant_group = participant_group_selected.value
    else if (actor.participant_group)
      response.participant_group = actor.participant_group
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

const dialog_delete = ref(false)
function deleteMention() {
  if (!props.mention.id)
    return
  all_saving.value = true
  deleteSimple(['mention', props.mention.id]).then(() => {
    emits('mention-deleted', props.mention.id)
    all_saving.value = false
    dialog_delete.value = false
    // snackbar.value = true
    // snackbar_message.value = 'Se ha eliminado la mención'
  })
}

</script>

<template>
  <v-col
    cols="12"
    _md="is_full ? 6 : 12"
  >
<!--    <v-fab-->
<!--      _id="fabPosition"-->
<!--      :key="props.mention.id"-->
<!--      location="top right"-->
<!--      size="large"-->
<!--      position="sticky"-->
<!--      icon-->
<!--      offset-->
<!--      style="z-index: 1000; bottom: 20px; left: 30px;"-->
<!--    >-->
<!--      <v-icon>save</v-icon>-->
<!--    </v-fab>-->
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
<!--      <v-divider></v-divider>-->
<!--      <v-banner-->
<!--        sticky-->
<!--        lines="one"-->
<!--      >-->
<!--        <template v-slot:text>-->
<!--          We can't save your edits while you are in offline mode.-->
<!--        </template>-->
<!--  -->
<!--        <template v-slot:actions>-->
<!--          <v-btn color="deep-purple-accent-4">-->
<!--            Go Online-->
<!--          </v-btn>-->
<!--        </template>-->
<!--      </v-banner>-->
      <v-form ref="mentionForm">
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
            ref="has_select"
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
          <ImpactToolbar
            :mention="mention"
            class="mt-2"
          />
          <ParticipantsToolbar
            ref="participantsToolbarRef"
            :mention="mention"
            @search-item="searchActor($event)"
            @selected-item="saveParticipant($event)"
          />
          <EventToolbar
            ref="eventsToolbarRef"
            :mention="mention"
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
      </v-form>
    </v-card>
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
  </v-col>
</template>

<style scoped>

</style>