<script setup>

import {useMainStore} from "~/store/index";
import {storeToRefs} from "pinia";
import PanelList from "~/components/dashboard/common/PanelList.vue";
import {nextTick} from "vue";
import {show_details} from "~/composables/fetch.js";
import LocationsToolbar from "~/components/dashboard/space_time/LocationsToolbar.vue";
import FilesToolbar from "~/components/dashboard/utils/FilesToolbar.vue";
import PanelsResult from "~/components/dashboard/common/PanelsResult.vue";
const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)
const { getGeo, saveSimple } = mainStore

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

const total_requests = ref(0)
const resolved_requests = ref(0)
const saving_locations = ref(false)
const snackbar = ref(false)

const note_collection = computed(() => {
  return schemas.value.collections_dict['note']
})

const full_project = computed(() => {
  return props.full_main
})

const related_notes = computed(() => {
  return full_project.value.mentions.map(mention => {
    const full_mention = {...mention, project: full_project.value}
    return {
      ...mention.note,
      mentions: [full_mention]
    }
  })
})

function saveLocations() {
  saving_locations.value = true
  total_requests.value = full_project.value.locations.length
  resolved_requests.value = 0
  full_project.value.locations.forEach(location => {
    // total_requests.value += 1
    saveSimple(['location', location]).then((res) => {
      resolved_requests.value += 1
      const idx = full_project.value.locations.findIndex(
        loc => loc.id === res.id)
      full_project.value.locations.splice(idx, 1, res)
      if (resolved_requests.value === total_requests.value){
        saving_locations.value = false
        snackbar.value = true
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
      :full_main="full_project"
      main_collection_name="project"
    />
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
      :full_main="full_main"
      child_relation_name="project_file"
      main_collection_name="project"
    />
  </v-card>
  <v-card class="mb-4" v-if="full_main.is_grouper">
    <v-card-title>
      Proyectos agrupados
      <span v-if="children_projects">
        ({{ children_projects.length }})
      </span>
    </v-card-title>
    <v-card-text v-if="children_projects && children_projects.length">
      <PanelsResult
        :results="children_projects"
        :collection_data="schemas.collections_dict['project']"
        :show_details="show_details"
        :total_count="children_projects.length"
        in_sheet
      />
    </v-card-text>
  </v-card>

  <v-card v-if="full_project.mentions">
    <v-card-title class="text-deep-purple">
      {{ full_project.mentions.length }} Notas:
    </v-card-title>
    <v-card-text>
      <PanelList
        :results="related_notes"
        :collection_data="note_collection"
        :show_details="show_details"
        parent="project"
      />
    </v-card-text>
  </v-card>
  <v-card class="my-3">
    <v-card-title>
      Todos los actores:
    </v-card-title>
  </v-card>
  <v-snackbar
    v-model="snackbar"
    color="success"
    location="right top"
    location-strategy="connected"
  >
    Se guardaron las ubicaciones
    <template v-slot:actions>
      <v-btn
        color="accent"
        variant="text"
        @click="snackbar = false"
      >
        Cerrar
      </v-btn>
    </template>
  </v-snackbar>
</template>

<style scoped>

</style>