<script setup>

import PanelsResult from "~/components/dashboard/common/PanelsResult.vue";

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

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

function build_participant(participant) {
  return {
    actor: props.full_main.id,
    actor_full: props.full_main,
    id: participant.id,
    mention: participant.mention.id,
    participant_types: participant.participant_types,
  }
}

const projects = computed(() => {
  if (!props.full_main.projects)
    return []
  return props.full_main.projects.map(project => {
    let mentions = props.full_main.participants.filter(
        participant => participant.mention.project === project.id)
    const all_notes = props.full_main.notes
    mentions = mentions.map(participant => {
      const note = all_notes.find(note => note.id === participant.mention.note)
      const participants = [build_participant(participant)]
      return {
        note,
        id: participant.mention.id,
        participants,
      }
    })
    return {
      ...project,
      mentions,
    }
  })
})

const notes = computed(() => {
  const notes_full = props.full_main.notes
  if (!notes_full)
    return []
  return props.full_main.participants.map(participant =>{
    const note = notes_full.find(note => note.id === participant.mention.note)
    const project = projects.value.find(
        project => project.id === participant.mention.project)
    let part = build_participant(participant)
    part.project_full = project
    return {
      ...note,
      mentions: [{
        ...participant.mention,
        project_full: project,
        participants: [part],
      }]
    }
  })
})

const children_actors = computed(() => {
  if (!props.full_main.children_actors_full)
    return []
  return props.full_main.children_actors_full.map(actor => {
    return {
      ...actor,
      parent_actor_full: props.full_main,
      parent_actor: props.full_main.id,
    }
  })
})

const other_parents = computed(() => {
  if (!props.full_main.other_parents_full)
    return []
  return props.full_main.other_parents_full.map(actor => {
    return {
      ...actor,
      parent_actor_full: props.full_main,
      parent_actor: props.full_main.id,
    }
  })
})

</script>

<template>
  <v-card class="mb-4" v-if="other_parents.length">
    <v-card-title>
      Actores padres extras
      <span>
        ({{ other_parents.length }})
      </span>
    </v-card-title>
    <v-card-text>
      <PanelsResult
        :results="other_parents"
        :collection_data="schemas.collections_dict['actor']"
        :show_details="show_details"
        :total_count="other_parents.length"
        in_sheet
        is_simple
      />
    </v-card-text>
  </v-card>
  <v-card class="mb-4">
    <v-card-title>
      Actores hijos
      <span v-if="children_actors">
        ({{ children_actors.length }})
      </span>
    </v-card-title>
    <v-card-text v-if="children_actors && children_actors.length">
      <PanelsResult
        :results="children_actors"
        :collection_data="schemas.collections_dict['actor']"
        :show_details="show_details"
        :total_count="children_actors.length"
        in_sheet
        is_simple
      />
    </v-card-text>
  </v-card>
  <v-card class="mb-4">
    <v-card-title>
      Proyectos
      <span v-if="projects">
        ({{ projects.length }})
      </span>
    </v-card-title>
    <v-card-text>
      <PanelsResult
        :results="projects"
        :collection_data="schemas.collections_dict['project']"
        :show_details="show_details"
        :total_count="projects.length"
        in_sheet
        is_simple
      />
    </v-card-text>
  </v-card>
  <v-card class="mb-4">
    <v-card-title>
      Notas
      <span v-if="notes">
        ({{ notes.length }})
      </span>
    </v-card-title>
    <v-card-text>
      <PanelsResult
        :results="notes"
        :collection_data="schemas.collections_dict['note']"
        :show_details="show_details"
        :total_count="notes.length"
        in_sheet
        is_simple
      />
    </v-card-text>
  </v-card>
</template>

<style scoped>

</style>