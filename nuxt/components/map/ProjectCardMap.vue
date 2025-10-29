<script setup>

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import ProjectCard from "~/components/dashboard/project/project/ProjectCard.vue";

import PanelsResult from "~/components/dashboard/common/PanelsResult.vue";
import {show_details} from "~/composables/fetch.js";
const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

const props = defineProps({
  selectedProject: {
    type: Object,
    default: null,
  },
  full_main: {
    type: Object,
    default: null,
  },
});


const note_collection = computed(() => {
  return schemas.value.collections_dict['note']
})

const actor_collection = computed(() => {
  return schemas.value.collections_dict['actor']
})


const emit = defineEmits(['update:selectedProject']);

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

const project_fields = [
  'id', 'name', 'alternative_name', 'conflict', 'megaproject_type',
  'status_project', 'description', 'status_validation', 'is_grouper'
]

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

const plural_comp = computed(() => {
  return related_notes.value.length !== 1 ? 's' : ''
})

</script>

<template>
  <v-card
    max-width="480"
    max-height="80vh"
    class="ma-3 project-card"
  >
<!--    <CardCommon-->
<!--      v-if="full_main"-->
<!--      :full_main="full_main"-->
<!--      :collection_data="schemas.collections_dict.project"-->
<!--      indirect_get-->
<!--      class="py-3"-->
<!--      is_map_viz-->
<!--    />-->


    <v-card
      v-if="full_main"
      class="d-flex align-center px-3"
      :color="selectedProject.color"
      variant="tonal"
      style="width: 100%;"
    >

      <ProjectCard
        :full_main="full_main"
        title="Detalles del Proyecto"
        is_map_viz
      />
      <v-btn
        size="small"
        icon
        variant="tonal"
        @click="emit('update:selectedProject', null)"
        class="close-btn"
        color="accent"
      >
        <v-icon>close</v-icon>
      </v-btn>
    </v-card>
    <v-progress-linear
      v-else
      height="40"
      indeterminate
      :color="selectedProject.color || 'primary'"
    ></v-progress-linear>
    <v-card-text v-if="false">
      <h3>Nombre: {{selectedProject.project.name}}</h3>
      <p><strong>Tipo de Megaproyecto:</strong>
        {{selectedProject}}
      </p>
    </v-card-text>
      <v-card-text v-if="full_main">
      <span class="text-subtitle-1 text-blue">
        Todos los actores ({{ related_actors.length }}):
      </span>

      <PanelsResult
        :results="related_actors"
        :collection_data="actor_collection"
        :show_details="show_details"
        :total_count="related_actors.length"
        in_sheet
        is_map_viz
      />

      <span class="text-subtitle-1 text-deep-purple mt-2">
        {{related_notes.length}}
        Nota{{plural_comp}} relacionada{{plural_comp}}:
      </span>
      <PanelsResult
        :results="related_notes"
        :collection_data="note_collection"
        :show_details="true"
        :total_count="related_notes.length"
        in_sheet
        is_map_viz
      />
    </v-card-text>
  </v-card>
</template>

<style scoped>

.project-card {
  position: absolute !important;
  top: 40px;
  right: 0;
  z-index: 2 !important;
  overflow-y: auto;
}

.close-btn {
  position: absolute;
  top: 8px;
  right: 8px;
}

</style>