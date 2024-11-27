<script setup>

import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";
import {computed, watch} from "vue";
import DialogEdit from "~/components/dashboard/common/DialogEdit.vue";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
import SelectDate from "~/components/dashboard/common/SelectDate.vue";
import ProjectCard from "~/components/dashboard/project/project/ProjectCard.vue";

import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import ParticipantsToolbar from "~/components/dashboard/source/ParticipantsToolbar.vue";
import EventToolbar from "~/components/dashboard/source/EventToolbar.vue";
const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)
const { saveSimple } = mainStore

const props = defineProps({
  mention: Object,
  is_full: {
    type: Boolean,
    default: false,
  },
})
const collection_in_edit = ref('actor')
const dialog_search = ref(false)
const dialog_edit = ref(false)
const elem_in_edition = ref(null)
const participant_in_edition = ref(null)
const total_requests = ref(0)
const resolved_requests = ref(0)
const saving = ref(false)
const snackbar = ref(false)

const emits = defineEmits(['mention-saved'])

function editItem(item) {
  elem_in_edition.value = item.actor_full
  collection_in_edit.value = 'actor'
  dialog_edit.value = true
}
function editProject() {
  elem_in_edition.value = props.mention.project_full
  collection_in_edit.value = 'project'
  dialog_edit.value = true
}
function searchItem(item) {
  console.log("searchItem")
  participant_in_edition.value = item
  collection_in_edit.value = 'actor'
  dialog_search.value = true
}
function searchProject() {
  collection_in_edit.value = 'project'
  dialog_search.value = true
}

function saveOneToMany(snake_name, main_item) {
  // console.log("save one to many")
  const main_schema = schemas.value.collections_dict[snake_name]
  const one_to_many = main_schema.fields.filter(
    field => field.relation_type === 'one_to_many')
  // console.log("one_to_many", one_to_many)
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
  // console.log("save mention", schemas.value)
  saving.value = true
  total_requests.value = 0
  resolved_requests.value = 0
  saveOneToMany('mention', props.mention)
}

function allFinished() {
  console.log("all finished", resolved_requests.value, total_requests.value)
  if (resolved_requests.value === total_requests.value){
    saveSimple(['mention', props.mention]).then(res => {
      emits('mention-saved', res)
      snackbar.value = true
      saving.value = false
    })
  }
}

function saveParticipant(actor) {
  // console.log("save participant", actor)
  if (participant_in_edition.value){
    console.log("participant_in_edition", participant_in_edition.value)
    const part_idx = props.mention.participants.findIndex(
      part => part.id === participant_in_edition.value.id)
    props.mention.participants.splice(part_idx, 1, {
      ...participant_in_edition.value,
      actor: actor.id,
      actor_full: actor,
    })
    return
  }
  const params = {
    mention: props.mention.id,
    actor: actor.id,
  }
  saveSimple(['participant', params]).then(response => {
    // console.log("response", response)
    props.mention.participants.unshift(response)
    dialog_search.value = false
  })
}

function closeDialog(event) {
  console.log("close dialog", event)
  dialog_edit.value = false
}

function closeChangeDialog(event) {
  if (collection_in_edit.value === 'actor')
    saveParticipant(event)
  dialog_search.value = false
}

</script>

<template>
  <v-col
    cols="12"
    _md="is_full ? 6 : 12"
  >
    <v-card variant="outlined" color="indigo-lighten-1">
      <v-card
        v-if="mention.project"
        class="d-flex align-center px-3"
        color="purple"
        variant="tonal"
        style="width: 100%;"
      >

        <ProjectCard
          :full_main="mention.project_full"
          class="px-3"
        />
        <v-spacer></v-spacer>
        <div class="d-flex flex-column py-1">
          <v-btn
            icon="edit"
            size="small"
            color="accent"
            variant="outlined"
            @click="editProject"
          ></v-btn>
          <v-btn
            icon="cached"
            size="small"
            color="accent"
            variant="outlined"
            @click="searchProject"
          ></v-btn>
        </div>
      </v-card>
      <div v-else>
        <v-btn
          color="accent"
          variant="elevated"
        >
          Agregar proyecto
        </v-btn>
      </div>
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
            <SelectDate
              :init_date="item.date"
              @update-date="item.date = $event"
              label="Fecha de cambio"
            />
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
        </ToolbarCommon>
        <ParticipantsToolbar
          :mention="mention"
          @search-item="searchItem"
          @edit-item="editItem"
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
            :parent_collection="schemas.collections_dict[collection_in_edit]"
            is_mini
            @select-item="closeChangeDialog"
          />
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-dialog v-model="dialog_edit">
      <DialogEdit
        :full_main="elem_in_edition"
        :collection_data="schemas.collections_dict[collection_in_edit]"
        @close-dialog="closeDialog($event)"
      />
    </v-dialog>
  </v-col>
</template>

<style scoped>

</style>