<script setup>

import StatusChip from "~/components/dashboard/status/StatusChip.vue";
import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";
import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";
import {computed, watch} from "vue";
import ActorSearch from "~/components/dashboard/actor/ActorSearch.vue";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
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
const dialog_search = ref(false)
const dialog_edit = ref(false)
const actor_in_edition = ref(null)
const total_requests = ref(0)
const resolved_requests = ref(0)


const actor_collection = computed(() => {
  return schemas.value.collections_dict['actor']
})
const all_actors = computed(() => {
  return props.mention.participants.map(participant => {
    return {...participant.actor_full, ...participant}
  })
})

function editItem(item) {
  actor_in_edition.value = item.actor_full
  dialog_edit.value = true
}
function searchItem(item) {
  console.log("searchItem")
  dialog_search.value = true
}

function saveOneToMany(snake_name, main_item) {
  // console.log("save one to many")
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
    console.log("main_item", main_item)
    console.log("field", field.name)
    main_item[field.name].forEach(item => {
      saveOneToMany(snake_name2, item)
      total_requests.value += 1
      saveSimple([snake_name2, item]).then(response => {
        console.log(`response ${snake_name2}`, response)
        resolved_requests.value += 1
      })
    })
  })
}

function saveMention() {
  console.log("save mention", schemas.value)
  // const mention_schema = schemas.value.collections_dict['mention']
  total_requests.value = 0
  saveOneToMany('mention', props.mention)
}

watch(() => resolved_requests.value, (value) => {
  if (value === total_requests.value){
    console.log("mention", props.mention)
    saveSimple(['mention', props.mention]).then(response => {
      console.log("response main", response)
    })
  }
})

function saveParticipant(actor) {
  console.log("save participant", actor)
  const params = {
    mention: props.mention.id,
    actor: actor.id,
  }
  saveSimple(['participant', params]).then(response => {
    console.log("response", response)
    props.mention.participants.unshift(response)
    dialog_search.value = false
  })
}

function closeDialog(event) {
  // dialog_search.value = false
  console.log("close dialog", event)
  if (event)
    saveParticipant(event)
  else
    dialog_search.value = false

}

</script>

<template>
  <v-col
    cols="12"
    _md="is_full ? 6 : 12"
  >
    <v-card variant="outlined" color="indigo-lighten-1">
      <div class="px-3 py-2" v-if="mention.project">
        <div class="text-h6">
          {{ mention.project_full.name }}
        </div>
        <div class="d-flex flex-wrap">
          <StatusChip
            v-if="mention.project_full.status_register"
            :main="mention.project"
            collection="register"
            left_label
            class="mb-1"
            bold_text
          />
          <ExtractivismIcons
            :project="mention.project_full"
            show_name
            class="ml-2"
          />
        </div>
      </div>
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
          :additional_fields="['interests']"
          color="blue"
          emit_add
          @add-item="searchItem"
        >
          <template #rows_init="{ item }">
            <v-chip
              v-if="item.actor_full"
              class="mb-2"
              prepend-icon="recent_actors"
              :text="item.actor_full.name"
              color="indigo lighten-4"
              append-icon="edit"
              @click="editItem(item)"
            >
            </v-chip>
            <v-btn
              v-else
              color="accent"
              variant="elevated"
              @click="searchItem(item)"
            >
              Agregar participante
            </v-btn>
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
          :additional_fields="['involvements']"
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
    <v-dialog
      v-model="dialog_search"
      max-width="920"
    >
      <v-card height="800">
        <v-card-text class="py-0">

          <CollectionDisplay
            :parent_collection="actor_collection"
            is_mini
            @select-item="closeDialog($event)"
          />
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-dialog v-model="dialog_edit">
      <ActorSearch
        :full_main="actor_in_edition"
        @close-dialog="dialog_search = false"
      />
    </v-dialog>
  </v-col>
</template>

<style scoped>

</style>