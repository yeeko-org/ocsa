<script setup>

import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index";
import {useDashboardStore} from "~/store/dash.js";

import LocationsToolbar from "~/components/dashboard/space_time/LocationsToolbar.vue";
import FilesToolbar from "~/components/dashboard/capture/FilesToolbar.vue";
import PanelsResult from "~/components/dashboard/common/main/PanelsResult.vue";
import {show_details} from "~/composables/fetch.js";
const mainStore = useMainStore()
const dashboardStore = useDashboardStore()
const { schemas } = storeToRefs(mainStore)
const { saveSimple } = mainStore
const { showSnackbar } = dashboardStore

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  show_details: {
    type: Boolean,
    default: false,
  },
  collection_data: Object,
})
// const full_main = defineModel({type: Object, required: true})


const project_fields = [
  'id', 'name', 'alternative_name', 'conflict', 'megaproject_type',
  'status_project', 'description', 'status_validation', 'is_grouper'
]

const total_requests = ref(0)
const resolved_requests = ref(0)
const saving_locations = ref(false)
const locations = ref([])
const files = ref([])

watch(props.full_main.files, (newVal) => {
    files.value = newVal || []
  }, {immediate: true}
)
watch(props.full_main.locations, (newVal) => {
    locations.value = newVal || []
  }, {immediate: true}
)

const note_collection = computed(() => {
  return schemas.value.collections_dict['note']
})

const actor_collection = computed(() => {
  return schemas.value.collections_dict['actor']
})

// const full_main = computed(() => {
//   return props.full_main
// })

const related_notes = computed(() => {
  return props.full_main.mentions.map(mention => {
    const full_mention = {
      ...mention,
      project_full: props.full_main,
      project: props.full_main.id,
    }
    return {
      ...mention.note_full,
      mentions: [full_mention]
    }
  })
})

const related_actors = computed(() => {
  const project_full = project_fields.reduce((obj, field) => {
    obj[field] = props.full_main[field]
    return obj
  }, {})
  const actors_dict = props.full_main.mentions.reduce((dict, mention) => {
    mention.participants.forEach(participant => {
      const participant_data = {
        ...participant,
        mention: {
          id: mention.id,
          note: mention.note_full.id,
          note_full: mention.note_full,
          project_full: project_full,
          project: project_full.id,
        }
      }
      if (participant.actor in dict){
        dict[participant.actor].participants.push(participant_data)
        return
      }
      dict[participant.actor] = {
        ...participant.actor_full,
        participants: [participant_data],
      }
    })
    return dict
  }, {})

  let actors_list = Object.values(actors_dict).map(actor => {
    return {
      ...actor,
      mentions_count: actor.participants.length
    }
  })
  // Sort by number of mentions, descending
  actors_list.sort((a, b) => b.mentions_count - a.mentions_count)
  return actors_list
})

const save_errors = ref(null)
function saveLocations() {
  saving_locations.value = true
  total_requests.value = props.full_main.locations.length
  resolved_requests.value = 0
  save_errors.value = null
  props.full_main.locations.forEach(location => {
    saveSimple(['location', location]).then((res) => {
      if (res.errors){
        console.log("Error saving location", res.errors)
        saving_locations.value = false
        save_errors.value = res.errors
        return
      }
      resolved_requests.value += 1
      const idx = props.full_main.locations.findIndex(
        loc => loc.id === res.id)
      props.full_main.locations.splice(idx, 1, res)
      if (resolved_requests.value === total_requests.value){
        saving_locations.value = false
        showSnackbar('Se guardaron las ubicaciones')
      }
    })
  })
}

function buildRelatedProjects(projects) {
  if (!projects)
    return []
  return projects.map(project => {
    return {
      ...project,
      parent_project_full: props.full_main,
      parent_project: props.full_main.id,
    }
  })
}

const children_projects = computed(() => {
  return buildRelatedProjects(props.full_main.children_projects_full)
})

</script>

<template>
  <v-card class="mb-4" elevation="4" variant="elevated" color="blue-grey-lighten-4">
    <LocationsToolbar
      v-model="locations"
      :parent_id="full_main.id"
      main_collection_name="project"
    />
    <v-card
      v-if="save_errors"
      class="ma-2 px-3 py-2"
      elevation="2"
      color="red-lighten-3"
    >
      Errores en el guardado: {{save_errors}}
    </v-card>

    <v-col cols="12" class="d-flex justify-end px-3 py-3">
      <v-btn
        color="accent"
        variant="elevated"
        :loading="saving_locations"
        @click="saveLocations"
      >
        Guardar ubicaciones
      </v-btn>
    </v-col>
  </v-card>
  <v-card
    class="mb-4"
    elevation="4"
    variant="elevated"
    color="brown-lighten-4"
  >
    <FilesToolbar
      v-model="files"
      :parent_id="full_main.id"
      child_relation_name="project_file"
      main_collection_name="project"
    />
  </v-card>
  <v-card class="mb-4" v-if="full_main.is_grouper">
    <v-card-text v-if="children_projects && children_projects.length">
      <PanelsResult
        :results="children_projects"
        :collection_data="schemas.collections_dict['project']"
        :show_details="show_details"
        :total_count="children_projects.length"
        in_sheet
        hide_actions
      >
        <template #title>
          Proyectos agrupados:
          <span v-if="children_projects">
            ({{ children_projects.length }})
          </span>
        </template>
      </PanelsResult>
    </v-card-text>
  </v-card>

  <v-card v-if="full_main.mentions">
    <v-card-text>
      <PanelsResult
        :results="related_notes"
        :collection_data="note_collection"
        :show_details="show_details"
        :total_count="related_notes.length"
        in_sheet
        hide_actions
      >
        <template #title>
          {{ full_main.mentions.length }} Notas:
        </template>
      </PanelsResult>
    </v-card-text>
  </v-card>
  <v-card class="my-3">
    <v-card-text>
      Eventos registrados
    </v-card-text>
  </v-card>
  <v-card class="my-3">
    <v-card-text>


      Afectaciones registradas

    </v-card-text>
  </v-card>
  <v-card class="my-3">
    <v-card-text>
      <PanelsResult
        :results="related_actors"
        :collection_data="actor_collection"
        :show_details="show_details"
        :total_count="related_actors.length"
        in_sheet
      >
        <template #title>
          Actores involucrados ({{ related_actors.length }})
        </template>
      </PanelsResult>
    </v-card-text>
  </v-card>

</template>

<style scoped>

</style>